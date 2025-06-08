import subprocess
import json
import os
import time
from datetime import datetime


def log(message):
    print(f"[{datetime.now().isoformat()}] {message}")


def upload_image_with_login(image_path):
    log(f"Checking if image exists: {image_path}")
    if not os.path.exists(image_path):
        log(f"Image file {image_path} does not exist")
        return

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
        log("Executing login command")
        login_result = subprocess.check_output(login_command).decode()
        token = json.loads(login_result).get("token")
        if not token:
            log("Login failed: No token received")
            return
        log("Login successful, token received")

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

        log("Executing logs command")
        logs_result = subprocess.check_output(logs_command).decode()
        log(f"Upload response: {logs_result}")

    except subprocess.CalledProcessError as e:
        log("Error executing curl: subprocess failed")


# Specify the static image path
image_path = "/home/raspberry/agrifusion-fastapi/scripts/image.png"

# Upload the image to trigger gantry actions
log(f"Uploading image: {image_path}")
upload_image_with_login(image_path)
log("Upload completed")

# Wait to observe gantry actions
log("Waiting 30 seconds to observe gantry movements")
time.sleep(30)

log("Test complete")
