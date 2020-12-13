import ctypes
import logging
import time
from ctypes import byref, c_long
from wintypes import LPDWORD

from HCNetSDK import Callback
from HCNetSDK import Constants
from HCNetSDK import Struct
from HCNetSDK.Error import get_error_msg
from utils import load_dll, gen_file_name, createStructure

logging.basicConfig(level='DEBUG', format='[%(name)s:%(lineno)d] [%(levelname)s]- %(message)s')

logger = logging.getLogger('SDK_Tools')


# todo 创建结构体全部改为creatSturcture
class SDKError(Exception):
    pass


def _log_execute_result(func):
    def warper(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        if ret:
            logger.debug('操作成功')
        else:
            logger.error('操作失败！ %s', self.sys_get_error_detail())
        return ret

    return warper


# todo 单例模式
class HKBaseTool(object):
    def __init__(self, ip, username, password, port=8000, log_level=3, sdk_path='../dll/libhcnetsdk.so'):
        """创建实例后自动初始化SDK"""
        self.sdk_dll_path = sdk_path
        self.hCNetSDK = None
        self.sIp = ip
        self.sUsername = username
        self.sPassword = password
        self.sPort = port
        self.lUserID = -1  # 用户句柄

        self.lChannel = 1
        self.logLevel = log_level

        self.__is_init = False
        self.sys_init_tools()

    @property
    def is_init(self):
        return self.__is_init

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

    def sys_get_error_detail(self):
        """获取错误详细信息"""
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
            self.__is_init = True
        else:
            raise SDKError('SDK 初始化失败：{}'.format(self.sys_get_error_detail()))

    @_log_execute_result
    def sys_get_sdk_ersion(self) -> str:
        return hex(self.hCNetSDK.NET_DVR_GetSDKVersion())

    @_log_execute_result
    def sys_get_sdk_bulid_version(self) -> str:
        return hex(self.hCNetSDK.NET_DVR_GetSDKBuildVersion())

    @_log_execute_result
    def sys_set_timeout(self, timeout=2000, retry_times=1) -> bool:
        """
        设置连接超时时间
        :param timeout: 超时时间
        :param retry_times: 连接尝试次数
        :return:
        """
        logger.debug('设置超时时间'.center(24, '-'))
        if self.hCNetSDK.NET_DVR_SetConnectTime(timeout, retry_times):
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
            raise SDKError('登陆失败, {}'.format(self.sys_get_error_detail()))
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
        if self.is_init:
            self.sys_logout()
            self.hCNetSDK.NET_DVR_Cleanup()
            self.__is_init = False
        logger.debug('已释放所有资源'.center(24, '-'))

    def __del__(self):
        if self.is_init:
            self.sys_clean_up()


class HKDoor(HKBaseTool):
    """门禁设备相关功能"""

    def __init__(self, *args, **kwargs):
        super(HKDoor, self).__init__(*args, **kwargs)
        self.dwState = -1  # 下发卡数据状态
        self.dwFaceState = -1  # 下发人脸数据状态
        self.lAlarmHandle = -1  # 报警布防句柄
        self.lListenHandle = -1  # 报警监听句柄
        self.fMSFCallBack = None  # 报警回调函数实现
        self.fMSFCallBack_V31 = None  # 报警回调函数实现
        self.remoteCfgHandle = -1  # NET_DVR_SendRemoteConfig等接口的句柄

        self._card_numbers = set()  # 保存门禁所有卡号

    def sys_clean_up(self):
        self.sys_stop_remote_config()
        self.sys_close_alarm_chan()
        super(HKDoor, self).sys_clean_up()

    @_log_execute_result
    def setup_alarm_chan(self, callback=Callback.fMessageCallBack):
        """门禁布防监听"""
        if not self.hCNetSDK.NET_DVR_SetDVRMessageCallBack_V31(callback, ctypes.c_void_p()):
            logger.error('设置布防回调函数失败')
            return
        # 报警布防参数
        param = {'byLevel': 1, 'byAlarmInfoType': 1, 'byDeployType': 1}
        lpSetupParam = createStructure(Struct.NET_DVR_SETUPALARM_PARAM, param)

        self.lAlarmHandle = self.hCNetSDK.NET_DVR_SetupAlarmChan_V41(self.lUserID, byref(lpSetupParam))
        return self.lAlarmHandle > -1

    def sys_close_alarm_chan(self):
        """撤防"""
        if self.lAlarmHandle > -1:
            logger.debug('撤防操作'.center(24, '-'))
            if self.hCNetSDK.NET_DVR_CloseAlarmChan_V30(self.lAlarmHandle):
                self.lAlarmHandle = -1
                logger.debug('操作成功')
            else:
                logger.error('撤防失败: %s', self.sys_get_error_detail())

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
    def sys_start_remote_config(self, dwCommand, lpInBuffer, dwInBufferLen, cbStateCallback=None,
                                pUserData=None):
        """启动远程配置
        :return: -1表示失败，其他值作为NET_DVR_SendRemoteConfig等接口的句柄
        """
        logger.debug('启动长连接远程配置'.center(24, '-'))
        # -1 表示失败，其他值作为NET_DVR_SendRemoteConfig等接口的句柄
        if self.remoteCfgHandle > -1:
            logger.debug('已存在长连接远程配置句柄')
            return True
        self.remoteCfgHandle = self.hCNetSDK.NET_DVR_StartRemoteConfig(
            self.lUserID, dwCommand, lpInBuffer, dwInBufferLen, cbStateCallback, pUserData)
        return self.remoteCfgHandle != -1

    def sys_stop_remote_config(self):
        if self.remoteCfgHandle > -1:
            if self.hCNetSDK.NET_DVR_StopRemoteConfig(self.remoteCfgHandle):
                logger.debug('成功关闭长连接配置句柄'.center(24, '-'))
                self.remoteCfgHandle = -1
            else:
                logger.error('关闭长连接配置句柄失败！ %s', self.sys_get_error_detail())

    def get_card_status_callback(self, struCardRecord):
        """获取卡状态"""
        if self.dwState == Constants.NET_SDK_CONFIG_STATUS_NEEDWAIT:
            logger.debug('配置等待')
            time.sleep(2)
            return True
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_SUCCESS:
            card_num = bytes(struCardRecord.byCardNo).strip(b'\x00').decode('ascii')
            logger.debug(
                '获取卡参数成功, 卡号: {}, 卡类型: {}, 姓名: {}'.format(
                    card_num, struCardRecord.byCardType, bytes(struCardRecord.byName).decode('gbk')))

            self._card_numbers.add(card_num)
            return True
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_FAILED:
            logger.error('获取卡参数失败，%s', self.sys_get_error_detail())
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_EXCEPTION:
            logger.error('获取卡参数异常，%s', self.sys_get_error_detail())
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_FINISH:
            logger.debug('获取卡参数完成')
        return False

    def _print_set_card_status(self, struCardStatus):
        """下发卡状态"""
        if self.dwState == Constants.NET_SDK_CONFIG_STATUS_NEEDWAIT:
            logger.debug('配置等待')
            time.sleep(2)
            return True
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_SUCCESS:
            if self.sys_get_error_code() != 0:
                logger.error('下发卡成功，但是有错误，卡号: %s, 错误码：%s', bytes(struCardStatus.byCardNo).decode(),
                             struCardStatus.dwErrorCode)
            else:
                logger.debug('下发卡成功，卡号: %s, 状态: %s', bytes(struCardStatus.byCardNo).decode('ascii'),
                             struCardStatus.byStatus)
            return True
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_FAILED:
            logger.error('下发卡失败，卡号：%s, 错误码：%s', bytes(struCardStatus.byCardNo).decode(), struCardStatus.dwErrorCode)
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_EXCEPTION:
            logger.error('下发卡异常，卡号：%s, 错误码：%s', bytes(struCardStatus.byCardNo).decode(), struCardStatus.dwErrorCode)
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_FINISH:
            logger.debug('下发卡完成')
        return False

    def _print_del_card_status(self, struCardStatus):
        """删除卡状态"""
        if self.dwState == Constants.NET_SDK_CONFIG_STATUS_NEEDWAIT:
            logger.debug('配置等待')
            time.sleep(2)
            return True
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_SUCCESS:
            if self.sys_get_error_code() != 0:
                logger.error('删除卡成功，但是有错误，卡号: %s, 错误码：%s', bytes(struCardStatus.byCardNo).decode(),
                             struCardStatus.dwErrorCode)
            else:
                logger.debug('删除卡成功，卡号: %s, 状态: %s', bytes(struCardStatus.byCardNo).decode('ascii'),
                             struCardStatus.byStatus)
            return True
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_FAILED:
            logger.error('删除卡失败，卡号：%s, 错误码：%s', bytes(struCardStatus.byCardNo).decode(), struCardStatus.dwErrorCode)
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_EXCEPTION:
            logger.error('删除卡异常，卡号：%s, 错误码：%s', bytes(struCardStatus.byCardNo).decode(), struCardStatus.dwErrorCode)
        elif self.dwState == Constants.NET_SDK_CONFIG_STATUS_FINISH:
            logger.debug('删除卡完成')
        return False

    def door_get_one_card(self, cardNum: str):
        """查询一个门禁卡参数详细信息"""
        # 创建发送命令结构体：查询一张卡参数
        commandParam = {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_COND), 'dwCardNum': 1}
        struCardCond = createStructure(Struct.NET_DVR_CARD_COND, commandParam)
        self.sys_start_remote_config(Constants.NET_DVR_GET_CARD, byref(struCardCond), struCardCond.dwSize)

        # 查找指定卡号的参数，需要下发查找的卡号条件
        sendParam = {'byCardNo': cardNum, 'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_SEND_DATA)}
        struCardNo = createStructure(Struct.NET_DVR_CARD_SEND_DATA, sendParam)
        # 存储卡信息结构体
        struCardRecord = createStructure(Struct.NET_DVR_CARD_RECORD,
                                         {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_RECORD)})

        while True:
            self.dwState = self.hCNetSDK.NET_DVR_SendWithRecvRemoteConfig(
                self.remoteCfgHandle, byref(struCardNo), struCardNo.dwSize, byref(struCardRecord),
                struCardRecord.dwSize, ctypes.byref(ctypes.c_int(0)))
            if self.dwState == -1:
                logger.error('NET_DVR_SendWithRecvRemoteConfig查询卡参数调用失败, %s', self.sys_get_error_detail())
                break
            if self.get_card_status_callback(struCardRecord):
                continue
            break
        self.sys_stop_remote_config()

    def door_get_all_card(self):
        """读取所有门禁卡信息"""
        # 创建发送命令结构体：所有卡信息0xffffffff
        commandParam = {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_COND), 'dwCardNum': 0xffffffff}
        struCardCond = createStructure(Struct.NET_DVR_CARD_COND, commandParam)

        self.sys_start_remote_config(Constants.NET_DVR_GET_CARD, byref(struCardCond), struCardCond.dwSize)
        # 创建卡信息结构体，用于存储卡信息
        struCardRecord = createStructure(Struct.NET_DVR_CARD_RECORD,
                                         {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_RECORD)})

        # clear
        self._card_numbers = set()
        while True:
            self.dwState = self.hCNetSDK.NET_DVR_GetNextRemoteConfig(self.remoteCfgHandle, byref(struCardRecord),
                                                                     struCardRecord.dwSize)
            if self.dwState == -1:
                logger.error('NET_DVR_GetNextRemoteConfig接口调用失败, %s', self.sys_get_error_detail())
                break
            if self.get_card_status_callback(struCardRecord):
                continue
            break
        self.sys_stop_remote_config()

        return list(self._card_numbers)

    def door_set_one_card(self, card_num: str, byDoorRight: str = '1', byCardType=1, byName='张三', **kwargs):
        """下发一张门禁卡
        :param byCardType: 1=普通卡
        :param byDoorRight: 1-为有权限，0-为无权限，从低位到高位依次表示对门
        :param card_num: 卡号
        :param byName: 姓名
        """
        commandParam = {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_COND), 'dwCardNum': 1}  # 下发一张
        struct_card_condition = createStructure(Struct.NET_DVR_CARD_COND, commandParam)
        self.sys_start_remote_config(Constants.NET_DVR_SET_CARD, byref(struct_card_condition),
                                     struct_card_condition.dwSize)

        # 起止时间
        param_begin_time = {'wYear': 2000, 'byMonth': 1, 'byDay': 1, 'byHour': 11, 'byMinute': 11, 'bySecond': 11}
        struct_begin_time = createStructure(Struct.NET_DVR_TIME_EX, param_begin_time)
        param_end_time = {'wYear': 2099, 'byMonth': 1, 'byDay': 1, 'byHour': 11, 'byMinute': 11, 'bySecond': 11}
        struct_end_time = createStructure(Struct.NET_DVR_TIME_EX, param_end_time)
        # 有效期参数
        valid_param = {'byEnable': 1, 'struBeginTime': struct_begin_time, 'struEndTime': struct_end_time}
        struct_valid = createStructure(Struct.NET_DVR_VALID_PERIOD_CFG, valid_param)

        param_card = {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_RECORD), 'byCardNo': card_num,
                      'byCardType': byCardType, 'byLeaderCard': 0, 'byUserType': 0, 'byDoorRight': byDoorRight,
                      'struValid': struct_valid, 'wCardRightPlan': '11', 'byName': byName}
        param_card.update(kwargs)
        struCardRecord = createStructure(Struct.NET_DVR_CARD_RECORD, param_card)

        struCardStatus = createStructure(Struct.NET_DVR_CARD_STATUS,
                                         {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_STATUS)})

        while True:
            self.dwState = self.hCNetSDK.NET_DVR_SendWithRecvRemoteConfig(
                self.remoteCfgHandle, byref(struCardRecord), struCardRecord.dwSize, byref(struCardStatus),
                struCardStatus.dwSize, byref(ctypes.c_int(0)))
            if self.dwState == -1:
                logger.error('NET_DVR_SendWithRecvRemoteConfig调用失败, %s', self.sys_get_error_detail())
                break
            if self._print_set_card_status(struCardStatus):
                continue
            break
        self.sys_stop_remote_config()

    def door_del_one_card(self, card_num: str):
        """删除一张门禁卡"""
        # 创建发送命令结构体：删除一张卡参数
        commandParam = {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_COND), 'dwCardNum': 1}
        struCardCond = createStructure(Struct.NET_DVR_CARD_COND, commandParam)
        self.sys_start_remote_config(Constants.NET_DVR_DEL_CARD, byref(struCardCond), struCardCond.dwSize)

        # 删除指定卡号的参数
        sendParam = {'byCardNo': card_num, 'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_SEND_DATA)}
        struCardData = createStructure(Struct.NET_DVR_CARD_SEND_DATA, sendParam)

        struCardStatus = createStructure(Struct.NET_DVR_CARD_STATUS,
                                         {'dwSize': ctypes.sizeof(Struct.NET_DVR_CARD_STATUS)})

        while True:
            self.dwState = self.hCNetSDK.NET_DVR_SendWithRecvRemoteConfig(
                self.remoteCfgHandle, byref(struCardData), struCardData.dwSize, byref(struCardStatus),
                struCardStatus.dwSize, byref(ctypes.c_int(0)))
            if self.dwState == -1:
                logger.error('NET_DVR_SendWithRecvRemoteConfig调用失败, %s', self.sys_get_error_detail())
                break
            if self._print_del_card_status(struCardStatus):
                continue
            break
        self.sys_stop_remote_config()

from PIL import Image
class HKIPCam(HKBaseTool):

    def __init__(self, *args, **kwargs):
        super(HKIPCam, self).__init__(*args, **kwargs)
        self.lRealPlayHandle = -1  # 预览播放句柄

    @_log_execute_result
    def IPC_setCapturePictureMode(self, dwCaptureMode):
        """设置抓图模式
        :param dwCaptureMode: BMP_MODE = 0, JPEG_MODE = 1
        """
        logger.debug('设置抓图模式')
        return self.hCNetSDK.NET_DVR_SetCapturePictureMode(dwCaptureMode)

    @_log_execute_result
    def IPC_captureJPEGPicture(self, channel: c_long = 1, pic_name=None, quality=2, picSize=0xff):
        """设备抓图，保存到本地jpeg图片"""
        logger.debug('单帧数据捕获并保存jpg'.center(24, '-'))
        if not pic_name:
            pic_name = gen_file_name('jpg')
        logger.debug(pic_name)
        jpeg_param = Struct.NET_DVR_JPEGPARA(wPicSize=picSize, wPicQuality=quality)
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
    def IPC_captureBMPicture(self, pic_name=None):
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
        :param stream_type: 码流类型，子码流
        :param link_mode: TCP
        :param block: 0- 非阻塞取流，1- 阻塞取流
        :param callback: 回调函数
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

    @_log_execute_result
    def IPC_stop_real_play(self):
        """停止预览"""
        logger.debug('停止预览'.center(24, '-'))
        if self.lRealPlayHandle > -1:
            if self.hCNetSDK.NET_DVR_StopRealPlay(self.lRealPlayHandle):
                self.lRealPlayHandle = -1
                return True
            return False
        return True

    def sys_clean_up(self):
        self.IPC_stop_real_play()
        super(HKIPCam, self).sys_clean_up()


if __name__ == '__main__':
    tool = HKBaseTool('10.86.77.12', 'admin', 'admin777')  # IPC

    print('SDK Build Version:', tool.sys_get_sdk_bulid_version())
    tool.sys_login()

    tool.sys_clean_up()
