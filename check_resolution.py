import cv2

# 初始化摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    cap.release()
    exit()

# 尝试的分辨率列表
resolutions = [(640, 480), (800, 600), (960, 840), (1280, 720), (1920, 1080), (2048, 1152), (2560, 1440), (3840, 2160)]

# 测试分辨率
for width, height in resolutions:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"请求分辨率: {width}x{height} -> 实际分辨率: {int(actual_width)}x{int(actual_height)}")

# 清理资源
cap.release()