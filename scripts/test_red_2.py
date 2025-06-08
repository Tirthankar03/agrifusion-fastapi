import cv2
from ultralytics import YOLO
import numpy as np

# Load the YOLOv8 model
# model = YOLO("/run/media/aun1x/New Volume/final year project/runs/detect/4_take1_50e_8b_y116/weights/best.pt")
model = YOLO("/home/raspberry/agrifusion-fastapi/models/take1_50e_8b_y112/best.pt")


# Run inference on the image
image_path = "/home/aun1x/final-year-backend/fastapi-backend/scripts/image.png"
results = model(image_path)

# Get the first result
result = results[0]

# Load the original image directly (without YOLO's default plotting)
img = cv2.imread(image_path)  # Load the image in BGR format

# Get the bounding boxes, class names, and confidences
boxes = result.boxes.xyxy.cpu().numpy()  # Bounding box coordinates [x1, y1, x2, y2]
classes = result.boxes.cls.cpu().numpy()  # Class indices
confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
class_names = result.names  # Class names dictionary

# Define the red color in BGR
red_color = (0, 0, 255)  # Red in BGR

# Font settings for class name and confidence
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_thickness = 1
font_color = (255, 255, 255)  # White text
bg_color = (0, 0, 255)  # Red background for text

# Iterate through each detection and draw a red bounding box
for box, cls, conf in zip(boxes, classes, confidences):
    x1, y1, x2, y2 = map(int, box)  # Convert coordinates to integers
    class_name = class_names[int(cls)]  # Get class name
    label = f"{class_name} {conf:.2f}"  # Create label with class name and confidence

    # Draw red bounding box
    cv2.rectangle(img, (x1, y1), (x2, y2), red_color, 2)

    # Get the size of the text to create a background rectangle
    (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
    text_bg_top_left = (x1, y1 - text_h - 4 if y1 - text_h - 4 > 0 else y1 + text_h + 4)
    text_bg_bottom_right = (
        x1 + text_w,
        y1 if y1 - text_h - 4 > 0 else y1 + text_h + 4 + text_h,
    )

    # Draw a red background rectangle for the text
    cv2.rectangle(img, text_bg_top_left, text_bg_bottom_right, bg_color, -1)

    # Draw the class name and confidence text
    text_org = (x1, y1 - 5 if y1 - text_h - 4 > 0 else y1 + text_h + 5)
    cv2.putText(img, label, text_org, font, font_scale, font_color, font_thickness)

# Display the image in a window (not saved to disk)
cv2.imshow("YOLOv8 Detection", img)
cv2.waitKey(0)  # Wait for any key press to close the window
cv2.destroyAllWindows()  # Close the window
