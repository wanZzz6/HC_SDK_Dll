import datetime
import ctypes
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


class HCTools(object):
    def __init__(self, ip, username, password, port=8000, sdk_path='dll/HCNetSDK'):
        self.path = sdk_path
        self.dll_lib = self.load_dll(sdk_path)
        self.sIp = ip
        self.sUsername = username
        self.sPassword = password
        self.sPort = port
        self.lUserID = 0
        self.lChannel = 1

    @staticmethod
    def load_dll(path):
        dll_lib = ctypes.WinDLL(path)
        return dll_lib

    def get_error_code(self) -> int:
        return self.dll_lib.NET_DVR_GetLastError()

    def get_error_message(self) -> str:
        error_code = self.get_error_code()
        return ''
        # todo

    def init_tools(self):
        """
        SDK 初始化
        :return:
        """
        init_res = self.dll_lib.NET_DVR_Init()
        error_msg = self.get_error_message()
        if init_res:
            print("SDK初始化成功：{}".format(error_msg))
        else:
            raise RuntimeError('SDK 初始化失败：{}'.format(error_msg))

    def set_timeout(self, timeout=2000):
        """
        设置连接超时时间
        :param timeout:
        :return:
        """
        ret = self.dll_lib.NET_DVR_SetConnectTime(timeout, 1)
        if ret:
            print('设置超时时间成功')
        else:
            error_msg = self.get_error_message()
            raise RuntimeError("设置超时错误信息：{}".format(error_msg))

    def login(self):
        pass
