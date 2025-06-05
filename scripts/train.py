# # %%
# from ultralytics import YOLO


# # %%
# model = YOLO("yolo11n.pt")

# # %%
# train_results = model.train(
#     data="/run/media/aun1x/New Volume/final year project/dataset/4/data.yaml",  # path to dataset YAML
#     epochs=50,  # number of training epochs
#     imgsz=640,  # training image size
#     amp=False,
#     batch=8,
#     name='4_take1_50e_8b_y11'
# )


# # %%


# %%
from ultralytics import YOLO


# %%
model = YOLO("yolo11n.pt")

# %%
train_results = model.train(
    data="/run/media/aun1x/New Volume/final year project/dataset/5/data.yaml",  # path to dataset YAML
    epochs=50,  # number of training epochs
    imgsz=960,  # training image size
    amp=False,
    batch=8,
    name='5_take1_50e_8b_y11'
)


# %%




