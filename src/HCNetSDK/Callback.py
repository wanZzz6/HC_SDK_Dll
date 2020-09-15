from ctypes import *

# 定义码流回调函数
REALDATACALLBACK = CFUNCTYPE(None, c_long, c_ulong, POINTER(c_ubyte), c_ulong, c_void_p)


# 实现回调函数功能
def _fRealDataCallBack_V30(lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
    """
    码流回调函数
    """
    print(u'预览句柄：{} 类型：{}， 长度：{} \n码流数据： {}'.format(lPlayHandle, dwDataType, dwBufSize, string_at(pBuffer, dwBufSize)))


# 回调函数对象
fRealDataCallBack_V30 = REALDATACALLBACK(_fRealDataCallBack_V30)
