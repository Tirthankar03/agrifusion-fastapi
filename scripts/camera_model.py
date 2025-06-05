import cv2
from ultralytics import YOLO

# Load a YOLOv8 model (pre-trained on COCO dataset)
model = YOLO(
    "/run/media/aun1x/New Volume1/final year project/runs/detect/take1_50e_8b_y112/weights/best.pt"
)  # You can also use yolov8s.pt, yolov8m.pt, etc.
# model = YOLO("/run/media/aun1x/New Volume1/final year project/runs/detect/take1_100e2_old/weights/best.pt")  # You can also use yolov8s.pt, yolov8m.pt, etc.


# Start webcam feed
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("Error: Could not oqpen webcam.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    # Run YOLOv8 inference on the frame
    results = model(frame)

    # Visualize results on the frame
    annotated_frame = results[0].plot()

    # Display the frame with detections
    cv2.imshow("YOLOv8 Webcam", annotated_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
