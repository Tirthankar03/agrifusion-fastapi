import cv2


def find_camera_index(max_index=5):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera found at index {i}")
                cap.release()
                return i
            cap.release()
    print("❌ No camera found.")
    return None


index = find_camera_index()
if index is not None:
    print(f"Use index {index} in your script.")
