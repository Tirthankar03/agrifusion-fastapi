import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import subprocess
import json
import os

# Raspberry Pi Motor Control Pins
IN1, IN2, IN3, IN4 = 17, 27, 22, 23
ENA, ENB = 18, 19
RELAY_PIN = 16  # GPIO pin for relay control

# Servo Pins
SERVO1 = 5
SERVO2 = 6

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB, RELAY_PIN, SERVO1, SERVO2], GPIO.OUT)

# Setup PWM
motor_pwm_a = GPIO.PWM(ENA, 5000)
motor_pwm_b = GPIO.PWM(ENB, 5000)
servo1_pwm = GPIO.PWM(SERVO1, 50)  # 50 Hz
servo2_pwm = GPIO.PWM(SERVO2, 50)

motor_pwm_a.start(50)
motor_pwm_b.start(50)
servo1_pwm.start(0)
servo2_pwm.start(0)


# Helper: convert angle to duty cycle
def angle_to_duty(angle):
    return 2 + (angle / 18)


# Upload image using login and curl
def upload_image_with_login(image_path):
    login_command = [
        "curl",
        "-s",
        "-X",
        "POST",
        "http://localhost:3000/login",
        "-H",
        "Content-Type: application/json",
        "-d",
        '{"email":"test@gmail.com", "password":"123456"}',
    ]

    try:
        login_result = subprocess.check_output(login_command).decode()
        token = json.loads(login_result).get("token")
        if not token:
            print("Login failed: No token received")
            return

        logs_command = [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:3000/logs",
            "-H",
            f"Authorization: Bearer {token}",
            "-F",
            f"image=@{image_path}",
        ]

        logs_result = subprocess.check_output(logs_command).decode()
        print("Upload response:", logs_result)

    except subprocess.CalledProcessError as e:
        print("Error executing curl:", e.output.decode())


def move_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)


def stop_motor():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)


def activate_relay():
    print("Capturing image before activating relay...")

    cam = cv2.VideoCapture(0)
    time.sleep(1)  # Let camera warm up
    ret, frame = cam.read()
    cam.release()

    if ret:
        temp_image_path = "/tmp/relay_trigger.jpg"
        cv2.imwrite(temp_image_path, frame)
        upload_image_with_login(temp_image_path)
        os.remove(temp_image_path)
    else:
        print("Failed to capture image.")

    water_time = 5
    print("Activating relay for water delivery")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(water_time)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Relay Deactivated")


def set_servo_angle(servo_pwm, angle):
    duty = angle_to_duty(angle)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    servo_pwm.ChangeDutyCycle(0)


def activate_servos():
    print("Blue Detected! Turning servos and slowing motors.")

    motor_pwm_a.ChangeDutyCycle(0)
    motor_pwm_b.ChangeDutyCycle(0)
    time.sleep(1)
    set_servo_angle(servo1_pwm, 40)
    set_servo_angle(servo2_pwm, 40)
    time.sleep(1)
    motor_pwm_a.ChangeDutyCycle(35)
    motor_pwm_b.ChangeDutyCycle(35)
    time.sleep(10)

    motor_pwm_a.ChangeDutyCycle(0)
    motor_pwm_b.ChangeDutyCycle(0)
    time.sleep(1)
    set_servo_angle(servo1_pwm, 90)
    set_servo_angle(servo2_pwm, 90)
    time.sleep(1)
    motor_pwm_a.ChangeDutyCycle(50)
    motor_pwm_b.ChangeDutyCycle(50)


# Start moving
move_forward()
set_servo_angle(servo1_pwm, 90)
set_servo_angle(servo2_pwm, 90)

# Use attached camera
cap = cv2.VideoCapture(0)
time.sleep(2)  # Camera warm-up

blue_detected_prev = False

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Red detection
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.bitwise_or(
            cv2.inRange(hsv, lower_red1, upper_red1),
            cv2.inRange(hsv, lower_red2, upper_red2),
        )
        red_pixels = cv2.countNonZero(mask_red)

        # Blue detection
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([200, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_pixels = cv2.countNonZero(mask_blue)

        # Red handling
        if red_pixels > 500:
            print("Red Detected! Stopping Bot...")
            stop_motor()
            time.sleep(1)
            activate_relay()
            time.sleep(5)
            print("Resuming Forward Movement...")
            move_forward()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask_red = cv2.bitwise_or(
                    cv2.inRange(hsv, lower_red1, upper_red1),
                    cv2.inRange(hsv, lower_red2, upper_red2),
                )
                red_pixels = cv2.countNonZero(mask_red)
                if red_pixels < 500:
                    print("Red cleared. Scanning resumes...")
                    break

        # Blue handling
        if blue_pixels > 800 and not blue_detected_prev:
            activate_servos()
            blue_detected_prev = True
        elif blue_pixels < 500:
            blue_detected_prev = False

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    motor_pwm_a.stop()
    motor_pwm_b.stop()
    servo1_pwm.stop()
    servo2_pwm.stop()
    GPIO.cleanup()
