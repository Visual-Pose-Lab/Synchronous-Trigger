import cv2
import time

# 定义捕获视频的参数
width, height = 640, 480
cap = cv2.VideoCapture(2)  # 0 是默认摄像头的ID
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
# fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 定义编码器
# out = cv2.VideoWriter('output.avi', fourcc, 6.0, (width, height))  # 输出文件名，编码器，帧率和分辨率

# 检查摄像头是否成功开启
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# 捕获视频直到按下 'q'
frame_nub = 0
while True:
    t1 = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    t2 = time.time()
    # 将帧写入输出文件
    # out.write(frame)
    # print(frame.shape)

    frame_nub += 1
    print(frame_nub, frame.shape, 1/(t2-t1))
    

    # 显示帧
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'): 
        break

# 完成后释放所有资源
cap.release()
# out.release()
cv2.destroyAllWindows()
