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


# 报警布防参数结构体。V41
class NET_DVR_SETUPALARM_PARAM(Structure):
    _fields_ = [
        ('dwSize', DWORD),  # 结构体大小
        ('byLevel', BYTE),  # 布防优先级：0- 一等级（高），1- 二等级（中），2- 三等级（低）
        ('byAlarmInfoType', BYTE),  # 智能交通报警信息上传类型：0- 老报警信息，1- 新报警信息
        ('byRetAlarmTypeV40', BYTE),
        ('byRetDevInfoVersion', BYTE),
        ('byRetVQDAlarmType', BYTE),
        ('byFaceAlarmDetection', BYTE),
        ('bySupport', BYTE),
        # 按位表示，每一位取值表示不同的能力
        # bit0- 表示二级布防是否上传图片，值：0-上传，1-不上传
        # Bit1- 表示是否启用断网续传数据确认机制，值：0-不开启，1-开启
        ('byBrokenNetHttp', BYTE),
        ('wTaskNo', WORD),  # 任务处理号
        ('byDeployType', BYTE),  # 布防类型：0-客户端布防，1-实时布防
        ('byRes1', BYTE * 3),  # 保留，置为0
        ('byAlarmTypeURL', BYTE),  # 报警图片数据类型，按位表示：
        ('byCustomCtrl', BYTE),  # 按位表示，bit0表示是否上传副驾驶人脸子图: 0- 不上传，1- 上传
    ]


# 报警设备信息结构体。
class NET_DVR_ALARMER(Structure):
    _fields_ = [
        ('byUserIDValid', BYTE),  # userid是否有效：0－无效；1－有效
        ('bySerialValid', BYTE),  # 序列号是否有效：0－无效；1－有效
        ('byVersionValid', BYTE),  # 版本号是否有效：0－无效；1－有效
        ('byDeviceNameValid', BYTE),  # 设备名字是否有效：0－无效；1－有效
        ('byMacAddrValid', BYTE),  # MAC地址是否有效：0－无效；1－有效
        ('byLinkPortValid', BYTE),  # Login端口是否有效：0－无效；1－有效
        ('byDeviceIPValid', BYTE),  # 设备IP是否有效：0－无效；1－有效
        ('bySocketIPValid', BYTE),  # Socket IP是否有效：0-无效；1-有效
        ('lUserID', LONG),
        ('sSerialNumber', BYTE * SERIALNO_LEN),  # 序列号
        ('dwDeviceVersion', DWORD),  # 版本信息
        ('sDeviceName', c_char * NAME_LEN),  # 设备名称
        ('byMacAddr', BYTE * MACADDR_LEN),  # MAC地址
        ('wLinkPort', WORD),  # 设备通讯端口
        ('sDeviceIP', c_char * 128),  # 设备IP地址
        ('sSocketIP', c_char * 128),  # 报警主动上传时的Socket IP地址
        ('byIpProtocol', BYTE),  # IP协议：0－IPV4；1－IPV6
        ('byRes2', BYTE * 11),  # 保留，置为0
    ]


# 时间参数结构体
class NET_DVR_TIME(Structure):
    _fields_ = [
        ('dwYear', DWORD),  # 年
        ('dwMonth', DWORD),  # 月
        ('dwDay', DWORD),  # 日
        ('dwHour', DWORD),  # 时
        ('dwMinute', DWORD),  # 分
        ('dwSecond', DWORD),  # 秒
    ]


# IP地址结构体
class NET_DVR_IPADDR(Structure):
    _fields_ = [
        ('sIpV4', c_char * 16),  # 设备IPv4地址
        ('sIpV6', BYTE * 128),  # 设备IPv6地址
    ]


# 门禁主机事件信息
class NET_DVR_ACS_EVENT_INFO(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),  # 卡号
        ('byCardType', BYTE),  # 卡类型：1- 普通卡，2- 残疾人卡，3- 黑名单卡，4- 巡更卡，5- 胁迫卡，6- 超级卡，7- 来宾卡，8- 解除卡，为0表示无效
        ('byWhiteListNo', BYTE),  # 白名单单号，取值范围：1~8，0表示无效
        ('byReportChannel', BYTE),  # 报告上传通道：1- 布防上传，2- 中心组1上传，3- 中心组2上传，0表示无效
        ('byCardReaderKind', BYTE),  # 读卡器类型：0- 无效，1- IC读卡器，2- 身份证读卡器，3- 二维码读卡器，4- 指纹头
        ('dwCardReaderNo', DWORD),  # 读卡器编号，为0表示无效
        ('dwDoorNo', DWORD),  # 门编号（或者梯控的楼层编号），为0表示无效（当接的设备为人员通道设备时，门1为进方向，门2为出方向）
        ('dwVerifyNo', DWORD),
        ('dwAlarmInNo', DWORD),
        ('dwAlarmOutNo', DWORD),
        ('dwCaseSensorNo', DWORD),
        ('dwRs485No', DWORD),
        ('dwMultiCardGroupNo', DWORD),
        ('wAccessChannel', WORD),
        ('byDeviceNo', BYTE),
        ('byDistractControlNo', BYTE),
        ('dwEmployeeNo', DWORD),  # 工号，为0无效
        ('wLocalControllerID', WORD),
        ('byInternetAccess', BYTE),
        ('byType', BYTE),
        ('byMACAddr', BYTE * MACADDR_LEN),
        ('bySwipeCardType', BYTE),
        ('byMask', BYTE),  # 是否带口罩：0-保留，1-未知，2-不戴口罩，3-戴口罩
        ('dwSerialNo', DWORD),  # 事件流水号，为0无效
        ('byChannelControllerID', BYTE),
        ('byChannelControllerLampID', BYTE),
        ('byChannelControllerIRAdaptorID', BYTE),
        ('byChannelControllerIREmitterID', BYTE),
        ('byRes', BYTE * 4),
    ]


# 门禁主机报警信息结构体
class NET_DVR_ACS_ALARM_INFO(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('dwMajor', DWORD),  # 报警主类型
        ('dwMinor', DWORD),  # 报警次类型，次类型含义根据主类型不同而不同
        ('struTime', NET_DVR_TIME),  # 报警时间
        ('sNetUser', BYTE * MAX_NAMELEN),
        ('struRemoteHostAddr', NET_DVR_IPADDR),  # 远程主机地址
        ('struAcsEventInfo', NET_DVR_ACS_EVENT_INFO),  # 报警信息详细参数
        ('dwPicDataLen', DWORD),  # 图片数据大小，不为0是表示后面带数据
        ('pPicData', c_char_p),  # 图片数据缓冲区
        ('wInductiveEventType', WORD),
        ('byPicTransType', BYTE),
        ('byRes1', BYTE),
        ('dwIOTChannelNo', DWORD),
        ('pAcsEventInfoExtend', c_char_p),
        ('byAcsEventInfoExtend', BYTE),
        ('byTimeType', BYTE),
        ('byRes2', BYTE),
        ('byAcsEventInfoExtendV20', BYTE),
        ('pAcsEventInfoExtendV20', c_char_p),
        ('byRes', BYTE * 4),
    ]


# 时间参数结构体
class NET_DVR_TIME_EX(Structure):
    _fields_ = [
        ('wYear', WORD),
        ('byMonth', BYTE),
        ('byDay', BYTE),
        ('byHour', BYTE),
        ('byMinute', BYTE),
        ('bySecond', BYTE),
        ('byRes', BYTE),
    ]


# 有效期参数结构体。
class NET_DVR_VALID_PERIOD_CFG(Structure):
    _fields_ = [
        ('byEnable', BYTE),  # 是否启用该有效期：0- 不启用，1- 启用
        ('byBeginTimeFlag', BYTE),  # 是否限制起始时间的标志，0-不限制，1-限制
        ('byEnableTimeFlag', BYTE),  # 是否限制终止时间的标志，0-不限制，1-限制
        ('byTimeDurationNo', BYTE),  # 有效期索引,从0开始（时间段通过SDK设置给锁，后续在制卡时，只需要传递有效期索引即可，以减少数据量
        ('struBeginTime', NET_DVR_TIME_EX),  # 有效期起始时间
        ('struEndTime', NET_DVR_TIME_EX),  # 有效期结束时间
        ('byTimeType', BYTE),  # 时间类型：0-设备本地时间（默认），1-UTC时间（对于struBeginTime，struEndTime字段有效）
        ('byRes2', BYTE * 31),  # 保留，置为0
    ]


# ****************优化接口结构体定义开始*************
NET_DVR_GET_CARD = 2560
NET_DVR_SET_CARD = 2561
NET_DVR_SET_FACE = 2567
NET_DVR_DEL_CARD = 2562

NET_SDK_CONFIG_STATUS_SUCCESS = 1000
NET_SDK_CONFIG_STATUS_NEEDWAIT = 1001
NET_SDK_CONFIG_STATUS_FINISH = 1002
NET_SDK_CONFIG_STATUS_FAILED = 1003
NET_SDK_CONFIG_STATUS_EXCEPTION = 1004


class NET_DVR_CARD_COND(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('dwCardNum', DWORD),  # 设置或获取卡数量，获取时置为0xffffffff表示获取所有卡信息
        ('byRes', BYTE * 64),
    ]


class NET_DVR_CARD_SEND_DATA(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),  # 卡号
        ('byRes', BYTE * 16),
    ]


class NET_DVR_CARD_RECORD(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        # 卡号，特殊卡号定义如下：
        # 0xFFFFFFFFFFFFFFFF：非法卡号
        # 0xFFFFFFFFFFFFFFFE：胁迫码
        # 0xFFFFFFFFFFFFFFFD：超级码
        # 0xFFFFFFFFFFFFFFFC~0xFFFFFFFFFFFFFFF1：预留的特殊卡
        # 0xFFFFFFFFFFFFFFF0：最大合法卡号
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),
        # 1- 普通卡（默认），2- 残疾人卡，3- 黑名单卡，4- 巡更卡，5- 胁迫卡，6- 超级卡，7- 来宾卡，8- 解除卡，9- 员工卡，10- 应急卡，
        # 11- 应急管理卡（用于授权临时卡权限，本身不能开门），默认普通卡
        ('byCardType', BYTE),
        ('byLeaderCard', BYTE),  # 是否为首卡：1- 是，0- 否
        ('byUserType', BYTE),  # 用户类型：0–普通用户 1-管理员用户
        ('byRes1', BYTE),  # 保留，置为0
        # 门权限（梯控的楼层权限、锁权限），按字节表示，1-为有权限，0-为无权限，从低位到高位依次表示对门（或者梯控楼层、锁）1-N是否有权限
        ('byDoorRight', BYTE * MAX_DOOR_NUM_256),
        ('struValid', NET_DVR_VALID_PERIOD_CFG),  # 有效期参数（有效时间跨度为1970年1月1日0点0分0秒~2037年12月31日23点59分59秒）
        ('byBelongGroup', BYTE * MAX_GROUP_NUM_128),  # 所属群组，按字节表示，1-属于，0-不属于，从低位到高位表示是否从属群组1~N
        ('byCardPassword', BYTE * CARD_PASSWORD_LEN),  # 卡密码
        ('wCardRightPlan', WORD * MAX_DOOR_NUM_256),  # 卡权限计划，取值为计划模板编号，同个门（锁）不同计划模板采用权限或的方式处理
        ('dwMaxSwipeTimes', DWORD),  # 最大刷卡次数，0为无次数限制
        ('dwSwipeTimes', DWORD),  # 已刷卡次数
        ('dwEmployeeNo', DWORD),  # 工号（用户ID），1~99999999，不能以0开头且不能重复
        ('byName', BYTE * NAME_LEN),  # 姓名
        # 卡权限，按位表示，0-无权限，1-有权限// 第0位表示：弱电报警// 第1位表示：开门提示音// 第2位表示：限制客卡// 第3位表示：通道
        # 第4位表示：反锁开门// 第5位表示：巡更功能
        ('dwCardRight', DWORD),
        ('byRes', BYTE * 256),  # 保留，置为0
    ]


class NET_DVR_CARD_STATUS(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),
        ('dwErrorCode', DWORD),
        ('byStatus', BYTE),  # 状态：0-失败，1-成功
        ('byRes', BYTE * 23),
    ]


class NET_DVR_FACE_COND(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),
        ('dwFaceNum', DWORD),
        ('dwEnableReaderNo', DWORD),
        ('byRes', BYTE * 124),
    ]


class NET_DVR_FACE_RECORD(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),
        ('dwFaceLen', DWORD),
        ('pFaceBuffer', c_char_p),
        ('byRes', BYTE * 128),
    ]


class NET_DVR_FACE_STATUS(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('byCardNo', BYTE * ACS_CARD_NO_LEN),
        ('byErrorMsg', BYTE * ERROR_MSG_LEN),
        ('dwReaderNo', DWORD),
        ('byRecvStatus', BYTE),
        ('byRes', BYTE * 131),
    ]

# ****************优化接口结构体定义结束*************
