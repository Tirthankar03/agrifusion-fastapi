# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse
# import shutil
# import cv2
# import uuid
# import cloudinary
# import cloudinary.uploader
# from ultralytics import YOLO
# import numpy as np
# import os
# import asyncio

# # Load env vars
# from dotenv import load_dotenv

# load_dotenv()


# app = FastAPI()

# # Initialize your YOLO model
# model = YOLO(
#     "/home/raspberry/agrifusion-fastapi/models/take1_50e_8b_y112/best.pt"
# )

# # Configure Cloudinary with environment variables
# cloudinary.config(
#     cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
#     api_key=os.getenv("CLOUDINARY_API_KEY"),
#     api_secret=os.getenv("CLOUDINARY_API_SECRET"),
# )


# # logic for watering plants
# @app.post("/water/")
# async def water_plants():
#     await asyncio.sleep(10)  # simulate a delay (3 seconds)
#     return JSONResponse(content={"success": True})


# @app.post("/detect/")
# async def detect_image(file: UploadFile = File(...)):
#     # Save uploaded file to a temporary location
#     temp_input_path = f"temp_input_{uuid.uuid4().hex}.jpg"
#     with open(temp_input_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Upload original image to Cloudinary
#     original_upload = cloudinary.uploader.upload(temp_input_path)
#     original_url = original_upload["secure_url"]

#     # Run YOLOv8 inference
#     results = model(temp_input_path)
#     result = results[0]
#     img = cv2.imread(temp_input_path)

#     boxes = result.boxes.xyxy.cpu().numpy()
#     classes = result.boxes.cls.cpu().numpy()
#     confidences = result.boxes.conf.cpu().numpy()
#     class_names = result.names

#     for box, cls, conf in zip(boxes, classes, confidences):
#         x1, y1, x2, y2 = map(int, box)
#         class_name = class_names[int(cls)]
#         label = f"{class_name} {conf:.2f}"

#         # Draw bounding box
#         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

#         # Text box
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 0.5
#         font_thickness = 1
#         font_color = (255, 255, 255)
#         bg_color = (0, 0, 255)
#         (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
#         text_bg_top_left = (
#             x1,
#             y1 - text_h - 4 if y1 - text_h - 4 > 0 else y1 + text_h + 4,
#         )
#         text_bg_bottom_right = (
#             x1 + text_w,
#             y1 if y1 - text_h - 4 > 0 else y1 + text_h + 4 + text_h,
#         )
#         cv2.rectangle(img, text_bg_top_left, text_bg_bottom_right, bg_color, -1)
#         text_org = (x1, y1 - 5 if y1 - text_h - 4 > 0 else y1 + text_h + 5)
#         cv2.putText(img, label, text_org, font, font_scale, font_color, font_thickness)

#     # Save processed image temporarily
#     temp_output_path = f"temp_output_{uuid.uuid4().hex}.jpg"
#     cv2.imwrite(temp_output_path, img)

#     # Upload processed image to Cloudinary
#     processed_upload = cloudinary.uploader.upload(temp_output_path)
#     processed_url = processed_upload["secure_url"]

#     # Clean up
#     os.remove(temp_input_path)
#     os.remove(temp_output_path)

#     #####gantry

#     return JSONResponse(
#         content={
#             "original_image_url": original_url,
#             "processed_image_url": processed_url,
#             "weedCount": len(boxes),
#             "weedsEliminated": len(boxes),  # Placeholder for weeds eliminated
#             "successRate": 100,  # Placeholder for success rate
#         }
#     )
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import cv2
import uuid
import cloudinary
import cloudinary.uploader
from ultralytics import YOLO
import numpy as np
import os
import asyncio
import RPi.GPIO as GPIO
import time

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize YOLO model
model = YOLO("/home/raspberry/agrifusion-fastapi/models/take1_50e_8b_y112/best.pt")

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# Gantry setup
X_PINS = [17, 27, 22, 23]  # GPIOs for X-axis stepper
Y_PINS = [5, 6, 13, 19]  # GPIOs for Y-axis stepper
STEPS_PER_CM_X = 362 / 3.4  # X calibration
STEPS_PER_CM_Y = 362 / 3.4  # Y calibration

halfstep_seq = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]


# Gantry control functions
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in X_PINS + Y_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)


def cleanup_gpio():
    GPIO.cleanup()


def move_axis(pins, distance_cm, direction, steps_per_cm):
    steps = int(abs(distance_cm) * steps_per_cm)
    seq = halfstep_seq if direction > 0 else halfstep_seq[::-1]
    for _ in range(steps):
        for halfstep in seq:
            for pin in range(4):
                GPIO.output(pins[pin], halfstep[pin])
            time.sleep(0.001)


def move_to_position(x_cm, y_cm, current_x, current_y):
    dx = x_cm - current_x
    dy = y_cm - current_y
    if dx != 0:
        move_axis(
            X_PINS, dx, direction=1 if dx > 0 else -1, steps_per_cm=STEPS_PER_CM_X
        )
        current_x += dx
        time.sleep(0.2)
    if dy != 0:
        move_axis(
            Y_PINS, dy, direction=1 if dy > 0 else -1, steps_per_cm=STEPS_PER_CM_Y
        )
        current_y += dy
        time.sleep(0.5)
    return current_x, current_y


def perform_gantry_actions(target_points_cm):
    setup_gpio()
    current_x = 0
    current_y = 0
    try:
        for x_target, y_target in target_points_cm:
            current_x, current_y = move_to_position(
                x_target, y_target, current_x, current_y
            )
            # Simulate laser action (replace with actual hardware control if available)
            print(f"Laser action at ({x_target:.2f}, {y_target:.2f}) cm")
            time.sleep(0.6)
        # Return to home
        if current_x != 0:
            move_axis(
                X_PINS,
                -current_x,
                direction=-1 if current_x > 0 else 1,
                steps_per_cm=STEPS_PER_CM_X,
            )
            time.sleep(0.2)
        if current_y != 0:
            move_axis(
                Y_PINS,
                -current_y,
                direction=-1 if current_y > 0 else 1,
                steps_per_cm=STEPS_PER_CM_Y,
            )
            time.sleep(0.2)
    finally:
        cleanup_gpio()


# Existing watering endpoint
@app.post("/water/")
async def water_plants():
    await asyncio.sleep(10)  # Simulate a delay
    return JSONResponse(content={"success": True})


# Integrated detection and gantry control endpoint
@app.post("/detect/")
async def detect_image(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_input_path = f"temp_input_{uuid.uuid4().hex}.jpg"
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload original image to Cloudinary
    original_upload = cloudinary.uploader.upload(temp_input_path)
    original_url = original_upload["secure_url"]

    # Run YOLOv8 inference
    results = model(temp_input_path)
    result = results[0]
    img = cv2.imread(temp_input_path)
    img_height, img_width = img.shape[:2]

    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_names = result.names

    # Draw bounding boxes
    for box, cls, conf in zip(boxes, classes, confidences):
        x1, y1, x2, y2 = map(int, box)
        class_name = class_names[int(cls)]
        label = f"{class_name} {conf:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        font_color = (255, 255, 255)
        bg_color = (0, 0, 255)
        (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
        text_bg_top_left = (
            x1,
            y1 - text_h - 4 if y1 - text_h - 4 > 0 else y1 + text_h + 4,
        )
        text_bg_bottom_right = (
            x1 + text_w,
            y1 if y1 - text_h - 4 > 0 else y1 + text_h + 4 + text_h,
        )
        cv2.rectangle(img, text_bg_top_left, text_bg_bottom_right, bg_color, -1)
        text_org = (x1, y1 - 5 if y1 - text_h - 4 > 0 else y1 + text_h + 5)
        cv2.putText(img, label, text_org, font, font_scale, font_color, font_thickness)

    # Save and upload processed image
    temp_output_path = f"temp_output_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(temp_output_path, img)
    processed_upload = cloudinary.uploader.upload(temp_output_path)
    processed_url = processed_upload["secure_url"]

    # Clean up temporary files
    os.remove(temp_input_path)
    os.remove(temp_output_path)

    # Define gantry working area (crop region from gantry code)
    crop_width = 650
    crop_height = 750
    offset_x = 10
    offset_y = 10
    x_start = (img_width - crop_width) // 2 + offset_x
    y_start = (img_height - crop_height) // 2 + offset_y

    # Physical dimensions of gantry working area
    physical_width_cm = 19  # X-axis range
    physical_height_cm = 21  # Y-axis range
    pixels_per_cm_x = crop_width / physical_width_cm
    pixels_per_cm_y = crop_height / physical_height_cm

    # Calculate target points for gantry based on YOLO detections
    target_points_cm = []
    for box in boxes:
        x1, y1, x2, y2 = box
        cx = (x1 + x2) / 2  # Center x
        cy = (y1 + y2) / 2  # Center y
        # Check if center is within the gantry's working area
        if (
            x_start <= cx <= x_start + crop_width
            and y_start <= cy <= y_start + crop_height
        ):
            cx_crop = cx - x_start  # Relative to crop origin
            cy_crop = cy - y_start
            x_cm = cx_crop / pixels_per_cm_x
            y_cm = (crop_height - cy_crop) / pixels_per_cm_y  # Y=0 at bottom
            target_points_cm.append((x_cm, y_cm))

    # Execute gantry actions in a separate thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, perform_gantry_actions, target_points_cm)

    # Return response
    return JSONResponse(
        content={
            "original_image_url": original_url,
            "processed_image_url": processed_url,
            "weedCount": len(boxes),
            "weedsEliminated": len(target_points_cm),  # Actual weeds targeted
            "successRate": 100 if len(boxes) > 0 else 0,  # Placeholder
        }
    )
