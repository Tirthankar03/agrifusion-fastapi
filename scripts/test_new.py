import cv2
from ultralytics import YOLO

# Load a YOLOv8 model (pre-trained on COCO dataset)
model = YOLO(
    "/home/aun1x/final-year-backend/fastapi-backend/models/take1_50e_8b_y112/best.pt"
)

# result = model("/run/media/aun1x/New Volume1/final year project/Weeds.v3-augmented_nottrained.yolov8/test/images/20210907_153931_x264_mp4-184_jpg.rf.d84795ffcfda403b97a022567dc0cde6.jpg")
result = model("/run/media/aun1x/New Volume/final year project/MAIN/image copy 2.png")
# result = model("/run/media/aun1x/New Volume/final year project/dataset/3/image.png")
result[0].show()
