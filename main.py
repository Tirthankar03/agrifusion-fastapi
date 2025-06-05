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

# Load env vars
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

# Initialize your YOLO model
model = YOLO(
    "/home/aun1x/final-year-backend/fastapi-backend/models/take1_50e_8b_y112/best.pt"
)

# Configure Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


# logic for watering plants
@app.post("/water/")
async def water_plants():
    await asyncio.sleep(10)  # simulate a delay (3 seconds)
    return JSONResponse(content={"success": True})


@app.post("/detect/")
async def detect_image(file: UploadFile = File(...)):
    # Save uploaded file to a temporary location
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

    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_names = result.names

    for box, cls, conf in zip(boxes, classes, confidences):
        x1, y1, x2, y2 = map(int, box)
        class_name = class_names[int(cls)]
        label = f"{class_name} {conf:.2f}"

        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Text box
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

    # Save processed image temporarily
    temp_output_path = f"temp_output_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(temp_output_path, img)

    # Upload processed image to Cloudinary
    processed_upload = cloudinary.uploader.upload(temp_output_path)
    processed_url = processed_upload["secure_url"]

    # Clean up
    os.remove(temp_input_path)
    os.remove(temp_output_path)

    return JSONResponse(
        content={
            "original_image_url": original_url,
            "processed_image_url": processed_url,
            "weedCount": len(boxes),
            "weedsEliminated": 0,  # Placeholder for weeds eliminated
            "successRate": 0,  # Placeholder for success rate
        }
    )
