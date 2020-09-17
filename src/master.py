import ctypes
import logging
from ctypes import byref, c_long
from ctypes.wintypes import LPDWORD

from HCNetSDK import Callback
from HCNetSDK import Struct
from HCNetSDK.Error import get_error_msg
from utils import load_dll, gen_file_name

logging.basicConfig(level='DEBUG')

logger = logging.getLogger('SDK_Tools')


class SDKError(Exception):
    pass


def _log_execute_result(func):
    def warper(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        if ret:
            logger.debug('操作成功')
        else:
            logger.error('操作失败！ %s', self.sys_get_error_info())
        return ret

    return warper


# todo 单例模式
class HCTools(object):
    def __init__(self, ip, username, password, port=8000, sdk_path='../dll/HCNetSDK'):
        """创建实例后自动初始化SDK"""
        self.sdk_dll_path = sdk_path
        self.hCNetSDK = None
        self.sIp = ip
        self.sUsername = username
        self.sPassword = password
        self.sPort = port
        self.lUserID = -1  # 用户句柄
        self.lAlarmHandle = -1  # 报警布防句柄
        self.lListenHandle = -1  # 报警监听句柄
        self.lRealPlayHandle = -1  # 预览播放句柄
        self.lChannel = 1
        self.logLevel = 3
        self.fMSFCallBack = None  # 报警回调函数实现
        self.fMSFCallBack_V31 = None  # 报警回调函数实现
        self.sys_init_tools()

    def sys_get_error_code(self) -> int:
        """获取错误码"""
        return self.hCNetSDK.NET_DVR_GetLastError()

    # todo 指针异常
    def sys_get_error_message(self) -> str:
        """获取错误信息"""
        error_code = self.sys_get_error_code()
        return get_error_msg(error_code)
        # data = self.hCNetSDK.NET_DVR_GetErrorMsg(error_code)
        # return ctypes.string_at(data).decode('utf-8')

    def sys_get_error_info(self):
        return '错误码：{}，错误信息：{}'.format(self.sys_get_error_code(), self.sys_get_error_message())

    def sys_init_tools(self):
        """
        SDK 初始化
        :return:
        """
        self.hCNetSDK = load_dll(self.sdk_dll_path)
        init_res = self.hCNetSDK.NET_DVR_Init()
        if init_res:
            logger.debug("SDK初始化成功")
        else:
            raise SDKError('SDK 初始化失败：{}'.format(self.sys_get_error_info()))

    @_log_execute_result
    def sys_set_timeout(self, timeout=2000) -> bool:
        """
        设置连接超时时间
        :param timeout:
        :return:
        """
        logger.debug('设置超时时间'.center(24, '-'))
        if self.hCNetSDK.NET_DVR_SetConnectTime(timeout, 1):
            return True
        return False

    @_log_execute_result
    def sys_enable_log(self, log_level: int = 3, log_dir: str = './logs') -> bool:
        """0-表示关闭日志，
        1-表示只输出ERROR错误日志，
        2-输出ERROR错误信息和DEBUG调试信息，
        3-输出ERROR错误信息、DEBUG调试信息和INFO普通信息等所有信息 """
        logger.debug('日志目录：{}'.format(log_dir))
        if self.hCNetSDK.NET_DVR_SetLogToFile(log_level, bytes(log_dir, 'utf-8'), True):
            return True
        return False

    def sys_login(self) -> bool:
        """登陆注册"""
        # 先注销
        self.sys_logout()
        # 登录设备
        device_info = Struct.NET_DVR_DEVICEINFO_V30()
        self.lUserID = self.hCNetSDK.NET_DVR_Login_V30(bytes(self.sIp, 'utf-8'), self.sPort,
                                                       bytes(self.sUsername, 'utf-8'), bytes(self.sPassword, 'utf-8'),
                                                       byref(device_info))
        if self.lUserID == -1:
            raise SDKError('登陆失败, {}'.format(self.sys_get_error_info()))
        else:
            logger.debug('登陆成功，lUserID:{}'.format(self.lUserID))
            return True

    def sys_logout(self):
        """注销"""
        if self.lUserID > 1:
            self.hCNetSDK.NET_DVR_Logout(self.lUserID)
            self.lUserID = -1

    def sys_clean_up(self):
        """撤防 + 注销 + 释放SDK资源"""
        self.sys_close_alarm_chan()

        self.IPC_stop_real_play()
        self.sys_logout()
        self.hCNetSDK.NET_DVR_Cleanup()
        logger.debug('已释放所有资源'.center(24, '-'))

    def __del__(self):
        self.sys_clean_up()

    @_log_execute_result
    def setup_alarm_chan(self):
        """布防监听"""
        if not self.hCNetSDK.NET_DVR_SetDVRMessageCallBack_V31(Callback.fMessageCallBack, ctypes.c_void_p()):
            logger.error('设置布防回调函数失败')
            return
        lpSetupParam = Struct.NET_DVR_SETUPALARM_PARAM()
        # 报警布防参数
        lpSetupParam.byLevel = 1
        lpSetupParam.byAlarmInfoType = 1
        lpSetupParam.byDeployType = 1
        self.lAlarmHandle = self.hCNetSDK.NET_DVR_SetupAlarmChan_V41(self.lUserID, byref(lpSetupParam))
        return self.lAlarmHandle > -1

    @_log_execute_result
    def sys_close_alarm_chan(self):
        """撤防"""
        logger.debug('撤防操作'.center(24, '-'))
        if self.lAlarmHandle > -1:
            if self.hCNetSDK.NET_DVR_CloseAlarmChan_V30(self.lAlarmHandle):
                self.lAlarmHandle = -1
                return True
            return False
        return True

    @_log_execute_result
    def door_open(self, door_index=1) -> bool:
        """远程开门"""
        logger.debug('远程开门'.center(24, '-'))
        return self._control_gateway(door_index, 1)

    @_log_execute_result
    def door_open_forever(self, door_index=1) -> bool:
        """远程控制门常开"""
        logger.debug('控制门常开'.center(24, '-'))
        return self._control_gateway(door_index, 2)

    @_log_execute_result
    def door_close_forever(self, door_index=1) -> bool:
        """远程控制门常闭"""
        logger.debug('控制门常闭'.center(24, '-'))
        return self._control_gateway(door_index, 3)

    def _control_gateway(self, door_index, status):
        return self.hCNetSDK.NET_DVR_ControlGateway(self.lUserID, door_index, status)

    @_log_execute_result
    def IPC_stop_real_play(self):
        """停止预览"""
        if self.lRealPlayHandle > -1:
            if self.hCNetSDK.NET_DVR_StopRealPlay(self.lRealPlayHandle):
                self.lRealPlayHandle = -1
                return True
            return False
        return True

    @_log_execute_result
    def IPC_setCapturePictureMode(self, dwCaptureMode):
        """设置抓图模式
        :param dwCaptureMode: BMP_MODE = 0, JPEG_MODE = 1
        """
        logger.debug('设置抓图模式')
        return self.hCNetSDK.NET_DVR_SetCapturePictureMode(dwCaptureMode)

    @_log_execute_result
    def IPC_captureJPEGPicture(self, channel: c_long = 1, pic_name=None, quality=2, PicSize=0xff):
        """设备抓图，保存到本地jpeg图片"""
        logger.debug('单帧数据捕获并保存jpg'.center(24, '-'))
        if not pic_name:
            pic_name = gen_file_name('jpg')
        logger.debug(pic_name)
        jpeg_param = Struct.NET_DVR_JPEGPARA(wPicSize=PicSize, wPicQuality=quality)
        return self.hCNetSDK.NET_DVR_CaptureJPEGPicture(self.lUserID, channel, byref(jpeg_param),
                                                        bytes(pic_name, 'utf-8'))

    @_log_execute_result
    def IPC_captureJPEGPicture_NEW(self, channel: c_long = 1, pic_name=None, quality=2, pic_size=0xff):
        """单帧数据捕获并保存成JPEG存放在指定的内存空间中。"""
        logger.debug('单帧抓图jpeg并保存到内存'.center(24, '-'))
        if not pic_name:
            pic_name = gen_file_name('jpg')
        logger.debug(pic_name)
        jpeg_param = Struct.NET_DVR_JPEGPARA(wPicSize=pic_size, wPicQuality=quality)
        buffer_size = 1024 * 1024
        sJpegPicBuffer = ctypes.create_string_buffer(buffer_size)
        lpSizeReturned = LPDWORD(ctypes.c_ulong(0))
        if self.hCNetSDK.NET_DVR_CaptureJPEGPicture_NEW(self.lUserID, channel, byref(jpeg_param), sJpegPicBuffer,
                                                        buffer_size, ctypes.byref(lpSizeReturned)):
            logger.debug('抓图成功')
            with open(pic_name, 'wb') as f:
                f.write(sJpegPicBuffer.raw)
                logger.debug('图片大小: %s', lpSizeReturned[0])
            return True
        return False

    # todo 未实现
    @_log_execute_result
    def IPC_captureBMPicture(self, channel: c_long = 1, pic_name=None):
        """设备抓图，保存到本地bmp图片,
        要求在调用NET_DVR_RealPlay_V40等接口时传入非空的播放句柄（播放库解码显示），否则时接口会返回失败，调用次序错误。
        """
        logger.debug('单帧数据捕获并保存bmp'.center(24, '-'))
        self.IPC_setCapturePictureMode(0)
        if not pic_name:
            pic_name = gen_file_name('bmp')
        logger.debug(pic_name)
        if self.lRealPlayHandle == -1:
            self.IPC_preview(callback=None)
        time.sleep(1)
        return self.hCNetSDK.NET_DVR_CapturePicture(self.lRealPlayHandle, bytes(pic_name, 'utf-8'))

    @_log_execute_result
    def IPC_preview(self, channel=1, stream_type=1, link_mode=0, block=1, callback=Callback.fRealDataCallBack_V30,
                    **kwargs):
        """实时预览
        :param channel: 通道号
        :param dwStreamType: 码流类型，子码流
        :param link_mode: TCP
        """
        # 构造预览参数结构体
        # hPlayWnd需要输入创建图形窗口的handle,没有输入无法实现BMP抓图
        preview_info = Struct.NET_DVR_PREVIEWINFO(lChannel=channel, dwStreamType=stream_type,
                                                  dwLinkMode=link_mode,
                                                  bBlocked=block, **kwargs)

        self.lRealPlayHandle = self.hCNetSDK.NET_DVR_RealPlay_V40(self.lUserID, byref(preview_info),
                                                                  callback, None)
        if self.lRealPlayHandle > -1:
            return True


if __name__ == '__main__':
    import time

    # tool = HCTools('10.86.23.111', 'admin', 'tsit2020')  # 门禁主机
    # tool = HCTools('10.86.77.12', 'admin', 'admin777')  # IPC
    tool = HCTools('10.86.77.119', 'admin', 'admin777')  # 门禁
    tool.sys_login()
    # print(tool.sys_get_error_info())

    # tool.IPC_preview()
    # tool.IPC_captureBMPicture()
    # tool.IPC_captureJPEGPicture_NEW(pic_size=2)
    tool.setup_alarm_chan()
    tool.door_open()
    time.sleep(2)

    tool.sys_clean_up()
