import sys

SERVER_IP = "81.71.93.76"
# SERVER_IP = "127.0.0.1"
SERVER_VIDEO_PORT=12360
CAM_DEVICE_NAME = "USB Camera" if sys.platform == 'win32' else "dev/video5"
CAM_FORMAT = "dshow" if sys.platform == 'win32' else "v4l2"
CAM_CAP_FPS = 15
CAM_CAP_WIDTH = 640
CAM_CAP_HEIGHT = 480
CAM_OUTPUT_FPS = 15
