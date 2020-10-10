from src.interface import HKIPCam
import time

if __name__ == '__main__':
    tool = HKIPCam('10.86.77.12', 'admin', 'admin777')  # IPC
    tool.sys_login()

    # tool.IPC_preview()
    # tool.IPC_captureBMPicture()
    tool.IPC_captureJPEGPicture_NEW(pic_size=2)
    time.sleep(5)
    tool.sys_clean_up()
