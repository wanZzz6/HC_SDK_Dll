from ctypes import *
from ctypes.wintypes import DWORD
from ctypes.wintypes import WORD
from ctypes.wintypes import USHORT
from ctypes.wintypes import BOOL
from ctypes.wintypes import LONG
from ctypes.wintypes import BYTE
from ctypes.wintypes import UINT
from ctypes.wintypes import LPVOID
from ctypes.wintypes import HANDLE
from ctypes.wintypes import COLORREF
from ctypes.wintypes import HWND

from Constants import *


# 定义登录结构体
class NET_DVR_DEVICEINFO_V30(Structure):
    _fields_ = [
        ('sSerialNumber', BYTE * SERIALNO_LEN),
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
        ('byRes3', BYTE * 2),
        ('byMirrorChanNum', BYTE),
        ('wStartMirrorChanNo', WORD),
        ('byRes2', BYTE * 2),
    ]


# JPEG图像信息结构体。
class NET_DVR_JPEGPARA(Structure):
    _fields_ = [
        ('wPicSize', WORD),
        # wPicSize 图片尺寸：0-CIF(352*288/352*240)，1-QCIF(176*144/176*120)，2-4CIF(704*576/704*480)或D1(720*576/720*486)，
        # 3-UXGA(1600*1200)， 4-SVGA(800*600)，5-HD720P(1280*720)，6-VGA(640*480)，7-XVGA(1280*960)，8-HD900P(1600*900)，
        # 9-HD1080P(1920*1080)，10-2560*1920， 11-1600*304，12-2048*1536，13-2448*2048，14-2448*1200，15-2448*800，
        # 16-XGA(1024*768)，17-SXGA(1280*1024)，18-WD1(960*576/960*480), 19-1080I(1920*1080)，20-576*576，21-1536*1536，
        # 22-1920*1920，23-320*240，24-720*720，25-1024*768，26-1280*1280，27-1600*600， 28-2048*768，29-160*120，
        # 75-336*256，78-384*256，79-384*216，80-320*256，82-320*192，83-512*384，127-480*272，128-512*272， 161-288*320，
        # 162-144*176，163-480*640，164-240*320，165-120*160，166-576*720，167-720*1280，168-576*960，180-180*240,
        # 181-360*480, 182-540*720, 183-720*960, 184-960*1280, 185-1080*1440, 500-384*288, 0xff-Auto(使用当前码流分辨率)
        ('wPicQuality', WORD),  # wPicQuality：图片质量系数：0-最好，1-较好，2-一般
    ]


# 定义预览结构体
class NET_DVR_PREVIEWINFO(Structure):
    _fields_ = [
        ('lChannel', LONG),
        ('dwStreamType', DWORD),  # 码流类型：0-主码流，1-子码流，2-三码流，3-虚拟码流
        ('dwLinkMode', DWORD),
        # 连接方式：0- TCP方式，1- UDP方式，2- 多播方式，3- RTP方式，4- RTP/RTSP，5- RTP/HTTP，6- HRUDP（可靠传输） ，7- RTSP/HTTPS，8- NPQ
        ('hPlayWnd', HWND),  # 播放窗口的句柄，为NULL表示不解码显示。
        ('bBlocked', BOOL),  # 0- 非阻塞取流，1- 阻塞取流
        ('bPassbackRecord', BOOL),
        ('byPreviewMode', BYTE),
        ('byStreamID', BYTE * STREAM_ID_LEN),
        ('byProtoType', BYTE),
        ('byRes1', BYTE),
        ('byVideoCodingType', BYTE),
        ('dwDisplayBufNum', DWORD),
        ('byNPQMode', BYTE),
        ('byRes', BYTE * 215),
    ]
