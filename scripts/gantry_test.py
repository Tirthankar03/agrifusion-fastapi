import subprocess
import json
import os
import time


# Upload image using login and curl
def upload_image_with_login(image_path):
    if not os.path.exists(image_path):
        print(f"Image file {image_path} does not exist.")
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


# Specify the static image path
image_path = "/home/raspberry/agrifusion-fastapi/scripts/image.png"

# Upload the image to trigger gantry actions
print("Uploading image to test gantry...")
upload_image_with_login(image_path)

# Wait to observe gantry actions
print("Waiting 30 seconds to observe gantry movements...")
time.sleep(30)

print("Test complete.")
