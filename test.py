# -*- coding: utf-8 -*-

import datetime
import ctypes
import tkinter as tk
from ctypes import *
from ctypes.wintypes import DWORD
from ctypes.wintypes import WORD
from ctypes.wintypes import USHORT
from ctypes.wintypes import SHORT
from ctypes.wintypes import LONG
from ctypes.wintypes import BYTE
from ctypes.wintypes import UINT
from ctypes.wintypes import LPVOID
from ctypes.wintypes import HANDLE
from ctypes.wintypes import COLORREF
from ctypes.wintypes import HWND

# import cv2
# from tkinter import filedialog#文件控件
# from PIL import Image, ImageTk#图像控件
# import threading#多线程

STRING = c_char_p


# 定义登录结构体
class NET_DVR_DEVICEINFO_V30(Structure):
    _fields_ = [
        ('sSerialNumber', BYTE * 48),
        ('byAlarmInPortNum', BYTE),
        ('byAlarmOutPortNum', BYTE),
        ('byDiskNum', BYTE),
        ('byDVRType', BYTE),
        ('byChanNum', BYTE),
        ('byStartChan', BYTE),
        ('byAudioChanNum', BYTE),
        ('byIPChanNum', BYTE),
        ('byZeroChanNum', BYTE),
        ('byMainProto', BYTE),
        ('bySubProto', BYTE),
        ('bySupport', BYTE),
        ('bySupport1', BYTE),
        ('bySupport2', BYTE),
        ('wDevType', WORD),
        ('bySupport3', BYTE),
        ('byMultiStreamProto', BYTE),
        ('byStartDChan', BYTE),
        ('byStartDTalkChan', BYTE),
        ('byHighDChanNum', BYTE),
        ('bySupport4', BYTE),
        ('byLanguageType', BYTE),
        ('byVoiceInChanNum', BYTE),
        ('byStartVoiceInChanNo', BYTE),
        ('bySupport5', BYTE),
        ('bySupport6', BYTE),
        ('byMirrorChanNum', BYTE),
        ('wStartMirrorChanNo', WORD),
        ('bySupport7', BYTE),
        ('byRes2', BYTE),
    ]


LPNET_DVR_DEVICEINFO_V30 = POINTER(NET_DVR_DEVICEINFO_V30)


# 定义预览结构体
class NET_DVR_PREVIEWINFO(Structure):
    _fields_ = [
        ('lChannel', LONG),
        ('dwStreamType', DWORD),
        ('dwLinkMode', DWORD),
        ('hPlayWnd', HWND),
        ('bBlocked', LONG),
        ('bPassbackRecord', LONG),
        ('byPreviewMode', BYTE),
        ('byStreamID', BYTE * 32),
        ('byProtoType', BYTE),
        ('byRes1', BYTE),
        ('byVideoCodingType', BYTE),
        ('dwDisplayBufNum', DWORD),
        ('byRes', BYTE * 216)
    ]


# 定义抓图结构体
class NET_DVR_JPEGPARA(Structure):
    _fields_ = [
        ('wPicSize', WORD),
        ('wPicQuality', WORD),
    ]


# 码流回调数据类型
NET_DVR_SYSHEAD = 1
NET_DVR_STREAMDATA = 2
NET_DVR_AUDIOSTREAMDATA = 3
NET_DVR_PRIVATE_DATA = 112
# 码流回调函数
REALDATACALLBACK = CFUNCTYPE(None, c_long, c_ulong, POINTER(c_ubyte), c_ulong, c_void_p)


def RealDataCallBack_V30(lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
    '''
    码流回调函数
    '''
    print(u'码流数据,类型 长度:', dwDataType, dwBufSize)


LPNET_DVR_JPEGPARA = POINTER(NET_DVR_JPEGPARA)

if __name__ == "__main__":
    import os

    os.chdir('dll')

    jpgname_root = "D:\\"
    ip = "10.86.77.12"
    port = 8000
    username = 'admin'
    password = 'admin777'
    wait_time = 1000
    strDllPath = 'HCNetSDK.dll'
    Objdll = WinDLL(strDllPath)

    # 初始化DLL
    Objdll.NET_DVR_Init()
    Objdll.NET_DVR_SetLogToFile(3, bytes(jpgname_root, 'utf-8'), True)
    # 设置设备超时时间
    Objdll.NET_DVR_SetConnectTime(int(wait_time), 1)

    # 登录设备
    device_info = NET_DVR_DEVICEINFO_V30()

    lUserId = Objdll.NET_DVR_Login_V30(bytes(ip, 'utf-8'), port, bytes(username, 'utf-8') \
                                       , bytes(password, 'utf-8'), byref(device_info))
    print('登陆成功')

    jpegpara = NET_DVR_JPEGPARA()
    jpegpara.wPicSize = 0xff
    jpegpara.wPicQuality = 2

    if (lUserId < 0):
        print("Login error," + str(Objdll.NET_DVR_GetLastError()))

        Objdll.NET_DVR_Cleanup()

    if lUserId >= 0:
        a = 1
        while (1):
            #        CapturePicture(jpgname_root, ip)

            #            time_now = time.strftime('%Y-%m-%d %H.%M.%S',time.localtime(time.time()))
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S.%f')
            jpgname = jpgname_root + str(lUserId) + "_" + time_now + ".jpg"
            print(jpgname)
            #            jpgname = jpgname_root + str(lUserId) + "_" + str(a) + ".jpg"

            suss = Objdll.NET_DVR_CaptureJPEGPicture(lUserId, 1, byref(jpegpara), bytes(jpgname, 'utf-8'))
            print("Error code=" + str(Objdll.NET_DVR_GetLastError()))
            if suss == 0:
                print("抓图不成功")
            if (a >= 1):
                break
            a = a + 1

    window = tk.Tk()
    window.title('TK窗口调用视频')

    preview_info = NET_DVR_PREVIEWINFO()
    preview_info.lChannel = 1  # 通道号
    preview_info.dwStreamType = 0  # 主码流
    preview_info.dwLinkMode = 0  # TCP
    preview_info.bBlocked = 1  # 阻塞取流
    funcRealDataCallBack_V30 = REALDATACALLBACK(RealDataCallBack_V30)
    lRealPlayHandle = Objdll.NET_DVR_RealPlay_V40(lUserId, byref(preview_info), funcRealDataCallBack_V30, None)
    Objdll.NET_DVR_RealPlay_V40()
    print("lRealPlayHandle=", lRealPlayHandle)

    # 登出设备A
    # Objdll.NET_DVR_Logout(lUserId)

    # 反初始化DLL
    # Objdll.NET_DVR_Cleanup()

    Objdll.NET_DVR_Logout(lUserId)
    print('登出')

    Objdll.NET_DVR_Cleanup()
    print('释放资源')
