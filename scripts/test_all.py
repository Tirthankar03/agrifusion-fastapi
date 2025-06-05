import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("/run/media/aun1x/New Volume/final year project/runs/detect/4_take1_50e_8b_y116/weights/best.pt") 

# Run inference
# results = model("/run/media/aun1x/New Volume/final year project/MAIN/2_combined.png")
# results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/Screenshot_2025-05-04-01-31-35_1920x1080.png")
# results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/Screenshot_2025-05-04-01-29-03_1920x1080.png")
# results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/Screenshot_2025-05-04-01-37-19_1920x1080.png")
# results = model("")
# results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/Screenshot_2025-05-04-01-39-31_1920x1080.png")
# results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/Screenshot_2025-05-04-01-41-37_1920x1080.png")
# results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/Screenshot_2025-05-04-01-43-57_1920x1080.png")
results = model("/run/media/aun1x/New Volume/final year project/dataset/3/test/images/75fc530e-9a02-4840-ad73-554f4237b0c4.jpeg")


# 



# Access the first result

results[0].show()
