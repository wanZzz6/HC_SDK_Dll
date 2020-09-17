from ctypes import *
from ctypes.wintypes import *
import Struct
from Constants import *
import struct

# 定义码流回调函数
REALDATACALLBACK = CFUNCTYPE(None, c_long, c_ulong, POINTER(c_ubyte), c_ulong, c_void_p)


# 实现回调函数功能
def _fRealDataCallBack_V30(lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
    """
    码流回调函数
    """
    print(u'预览句柄：{} 类型：{}， 长度：{} \n码流数据： {}'.format(lPlayHandle, dwDataType, dwBufSize, string_at(pBuffer, dwBufSize)))


fRealDataCallBack_V30 = REALDATACALLBACK(_fRealDataCallBack_V30)

# 接收设备报警消息等
MSGCallBack_V31 = WINFUNCTYPE(BOOL, LONG, Struct.NET_DVR_ALARMER, POINTER(c_char), DWORD, LPVOID)


def _fMessageCallBack(lCommand: LONG, pAlarmer: Struct.NET_DVR_ALARMER, pAlarmInfo: POINTER(c_char), dwBufLen: DWORD,
                      pUser: c_void_p) -> bool:
    print('设备名：{} - IP: {}'.format(pAlarmer.sDeviceName, pAlarmer.sDeviceIP))
    print('Info:{}'.format(pAlarmInfo))
    print('len: {}'.format(dwBufLen))
    # 不同的报警信息对应不同的类型
    if lCommand == COMM_ALARM_ACS:
        print('lCommand={} - 门禁主机报警信息'.format(lCommand))
        print(pAlarmInfo[:dwBufLen])
        a = cast(pAlarmInfo, POINTER(Struct.NET_DVR_ACS_ALARM_INFO))
        # a = Struct.NET_DVR_ACS_ALARM_INFO.from_buffer_copy(pAlarmInfo[:dwBufLen])
        print(a.contents.dwMajor, a.contents.struTime.dwYear)

    return True


fMessageCallBack = MSGCallBack_V31(_fMessageCallBack)
