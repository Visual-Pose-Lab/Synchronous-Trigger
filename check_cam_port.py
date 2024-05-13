import cv2


for cam_port in range(10):
    cap = cv2.VideoCapture(cam_port)
    if cap.isOpened():
        print(f"摄像头端口 {cam_port} 可用")
        cap.release()
    else:
        pass
        print(f"摄像头端口 {cam_port} 不可用")