import os
import ctypes
import time
import numpy as np


class HKIPCam():
	def __init__(self, IP, username, psw):
		# 获取所有的库文件到一个列表
		self.path = "lib_new/win64/"
		self.sDVRIP = IP
		self.dll_list = self.file_name(self.path)
		self.lUserID = 0
		self.lChannel = 1
		self.sUserName = username
		self.sPassword = psw
		self.NET_DVR_Login_V30()
		self.caplib= None

	def file_name(self, file_dir):
		pathss = []
		for root, dirs, files in os.walk(file_dir):
			for file in files:
				pathss.append(self.path + file)
		return pathss

	def callCpp2(self, func_name, *args):
		if self.caplib == None:
			for HK_dll in self.dll_list:
				try:
					lib = ctypes.cdll.LoadLibrary(HK_dll)
					try:
						value = eval("lib.NET_DVR_CaptureJPEGPicture")(*args)
						print("调用的库："+HK_dll)
						print("执行成功,返回值："+str(value))
						self.caplib = HK_dll
						return value
					except:
						continue
				except:
					# print("库文件载入失败："+HK_dll)
					continue
			# print("没有找到接口！")
			return False
		else:
			lib = ctypes.cdll.LoadLibrary(self.caplib)
			value = eval("lib.NET_DVR_CaptureJPEGPicture")(*args)
			return value

	def callCpp(self, func_name, *args):
		for HK_dll in self.dll_list:
			try:
				lib = ctypes.cdll.LoadLibrary(HK_dll)
				try:
					value = eval("lib.%s" % func_name)(*args)
					# print("调用的库："+HK_dll)
					# print("执行成功,返回值："+str(value))
					return value
				except:
					continue
			except:
				# print("库文件载入失败："+HK_dll)
				continue
		# print("没有找到接口！")
		return False

	# region 登入
	# 定义登入结构体
	class LPNET_DVR_DEVICEINFO_V30(ctypes.Structure):
		_fields_ = [
			("sSerialNumber", ctypes.c_byte * 48),
			("byAlarmInPortNum", ctypes.c_byte),
			("byAlarmOutPortNum", ctypes.c_byte),
			("byDiskNum", ctypes.c_byte),
			("byDVRType", ctypes.c_byte),
			("byChanNum", ctypes.c_byte),
			("byStartChan", ctypes.c_byte),
			("byAudioChanNum", ctypes.c_byte),
			("byIPChanNum", ctypes.c_byte),
			("byZeroChanNum", ctypes.c_byte),
			("byMainProto", ctypes.c_byte),
			("bySubProto", ctypes.c_byte),
			("bySupport", ctypes.c_byte),
			("bySupport1", ctypes.c_byte),
			("bySupport2", ctypes.c_byte),
			("wDevType", ctypes.c_uint16),
			("bySupport3", ctypes.c_byte),
			("byMultiStreamProto", ctypes.c_byte),
			("byStartDChan", ctypes.c_byte),
			("byStartDTalkChan", ctypes.c_byte),
			("byHighDChanNum", ctypes.c_byte),
			("bySupport4", ctypes.c_byte),
			("byLanguageType", ctypes.c_byte),
			("byVoiceInChanNum", ctypes.c_byte),
			("byStartVoiceInChanNo", ctypes.c_byte),
			("byRes3", ctypes.c_byte * 2),
			("byMirrorChanNum", ctypes.c_byte),
			("wStartMirrorChanNo", ctypes.c_uint16),
			("byRes2", ctypes.c_byte * 2)]

	# 用户注册设备 并登入，需要修改IP,账号、密码
	def NET_DVR_Login_V30(self, wDVRPort=8000):
		init_res = self.callCpp("NET_DVR_Init")  # SDK初始化
		if init_res:
			print("SDK初始化成功")
			error_info = self.callCpp("NET_DVR_GetLastError")
		else:
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("SDK初始化错误：" + str(error_info))
			return False

		set_overtime = self.callCpp("NET_DVR_SetConnectTime", 2000, 1)  # 设置超时
		if set_overtime:
			print("设置超时时间成功")
		# a = 1
		else:
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("设置超时错误信息：" + str(error_info))
			return False

		# 用户注册设备
		# c++传递进去的是byte型数据，需要转成byte型传进去，否则会乱码
		sDVRIP = bytes(self.sDVRIP, "ascii")
		sUserName = bytes(self.sUserName, "ascii")
		sPassword = bytes(self.sPassword, "ascii")
		# print("数据转化成功")
		DeviceInfo = self.LPNET_DVR_DEVICEINFO_V30()
		# print(DeviceInfo)
		lUserID = self.callCpp("NET_DVR_Login_V30", sDVRIP, wDVRPort, sUserName, sPassword, ctypes.byref(DeviceInfo))

		if lUserID == -1:
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("登录错误信息：" + str(error_info))
			return error_info
		else:
			print("登录成功，用户IP：" + self.sDVRIP)
			return lUserID

	# endregion


	def NET_DVR_SetLogToFile(self):
		if self.callCpp("NET_DVR_SetLogToFile", 3) == False:
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("日志开启失败：" + str(error_info))
		else:
			print("日志开启成功")

	# region 预览
	# 定义预览结构体
	class NET_DVR_PREVIEWINFO(ctypes.Structure):
		_fields_ = [
			("lChannel", ctypes.c_long),
			("lLinkMode", ctypes.c_long),
			("hPlayWnd", ctypes.c_void_p),
			("sMultiCastIP", ctypes.c_char_p),
			("byProtoType", ctypes.c_byte),
			("byRes", ctypes.c_byte * 3)]

	# 预览实现
	def Preview(self):
		lpPreviewInfo = self.NET_DVR_PREVIEWINFO()
		# hPlayWnd需要输入创建图形窗口的handle,没有输入无法实现BMP抓图
		lpPreviewInfo.hPlayWnd = None
		lpPreviewInfo.lChannel = 1
		lpPreviewInfo.dwLinkMode = 0
		lpPreviewInfo.sMultiCastIP = None
		m_lRealHandle = self.callCpp("NET_DVR_RealPlay_V40", self.lUserID, ctypes.byref(lpPreviewInfo), None, None,
									 True)
		if (m_lRealHandle < 0):
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("预览失败：" + str(error_info))
		else:
			print("预览成功")
		return m_lRealHandle

	# endregion


	# region 抓图
	# BMP抓图预览的时候hPlayWnd显示窗口不能为none
	def Get_BMPPicture(self):
		if self.callCpp("NET_DVR_SetCapturePictureMode", 0) == False:
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("change fail" + str(error_info))
		else:
			print("change success")

		m_lRealHandle = self.Preview()
		sBmpPicFileName = bytes("pytest.bmp", "ascii")
		if (self.callCpp("NET_DVR_CapturePicture", m_lRealHandle, sBmpPicFileName) == False):
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("抓图失败：" + str(error_info))
		else:
			print("抓图成功")

	#
	# 抓图数据结构体
	class NET_DVR_JPEGPARA(ctypes.Structure):
		_fields_ = [
			("wPicSize", ctypes.c_ushort),
			("wPicQuality", ctypes.c_ushort)]

	# jpeg抓图hPlayWnd显示窗口能为none，存在缺点采集图片速度慢
	def Get_JPEGpicture(self, Name, pic_turn=0):
		print("摄像机开始抓图...")
		time_strat = time.time()
		if pic_turn > 0:
			sJpegPicFileName = bytes("capture_{}_{}.jpg".format(Name, pic_turn), "ascii")
		else:
			sJpegPicFileName = bytes("capture_{}.jpg".format(Name), "ascii")

		lpJpegPara = self.NET_DVR_JPEGPARA()
		lpJpegPara.wPicSize = 0
		lpJpegPara.wPicQuality = 0
		if (self.callCpp2("NET_DVR_CaptureJPEGPicture", self.lUserID, self.lChannel, ctypes.byref(lpJpegPara),
						  sJpegPicFileName) == False):
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("抓图失败" + str(error_info))
			return -error_info
		else:
			time_end = time.time()
			print("抓图成功, 用时{}s".format(time_end - time_strat))
			return time_end - time_strat

	# endregion


	def Restart(self):
		if self.callCpp("NET_DVR_RebootDVR", self.lUserID) == False:
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("重启失败：" + str(error_info))
		else:
			print("正在重启，请稍后...")

	def Convert1DToCArray(self, TYPE, ary):
		arow = TYPE(*ary.tolist())
		return arow

	def Convert2DToCArray(self, ary):
		ROW = ctypes.c_int * len(ary[0])
		rows = []
		for i in range(len(ary)):
			rows.append(self.Convert1DToCArray(ROW, ary[i]))
		MATRIX = ROW * len(ary)
		return MATRIX(*rows)

	# jpeg抓图hPlayWnd显示窗口能为none，存在缺点采集图片速度慢
	def Get_JPEGpicture_New(self):
		print("摄像机开始抓图...")
		time_strat = time.time()
		lpJpegPara = self.NET_DVR_JPEGPARA()
		lpJpegPara.wPicSize = 9
		lpJpegPara.wPicQuality = 0
		height = 960
		width = 1280
		tmp = np.zeros((height, width), dtype=int)
		sJpegPicBuffer = self.Convert2DToCArray(tmp)
		if (self.callCpp("NET_DVR_CaptureJPEGPicture_NEW", self.lUserID, self.lChannel, ctypes.byref(lpJpegPara),
						 sJpegPicBuffer, height * width, ctypes.c_uint(0)) == False):
			error_info = self.callCpp("NET_DVR_GetLastError")
			print("抓图失败" + str(error_info))
		else:
			time_end = time.time()
			print("抓图成功, 用时{}s".format(time_end - time_strat))
			# re = np.zeros([height, width])
			# for i in range(width):
			# 	for j in range(width):
			# 		re[i][j] = sJpegPicBuffer[i][j]
			re = np.asarray(sJpegPicBuffer, dtype=np.uint32)
			return re

	# 定义光学变倍结构体

	# 光学变倍结构体
	class NET_DVR_FOCUSMODE_CFG(ctypes.Structure):
		_fields_ = [
			("dwSize", ctypes.c_uint32),
			("byFocusMode", ctypes.c_byte),
			("byAutoFocusMode", ctypes.c_byte),
			("wMinFocusDistance", ctypes.c_uint16),
			("byZoomSpeedLevel", ctypes.c_byte),
			("byFocusSpeedLevel", ctypes.c_byte),
			("byOpticalZoom", ctypes.c_byte),
			("byDigtitalZoom", ctypes.c_byte),
			("fOpticalZoomLevel", ctypes.c_float),
			("dwFocusPos", ctypes.c_uint32),
			("byFocusDefinitionDisplay", ctypes.c_byte),
			("byFocusSensitivity", ctypes.c_byte),
			("byRes1", ctypes.c_byte * 2),
			("dwRelativeFocusPos", ctypes.c_uint32),
			("byRes", ctypes.c_byte * 48), ]

	# 获取光学变倍值
	def get_CamZoom(self):
		m_struFocusModeCfg = self.NET_DVR_FOCUSMODE_CFG()
		dwReturned = ctypes.c_uint16(0)
		# print(callCpp("NET_DVR_GetDVRConfig"))
		if (self.callCpp("NET_DVR_GetDVRConfig", self.lUserID, 3305, self.lChannel, ctypes.byref(m_struFocusModeCfg),
						 76,
						 ctypes.byref(dwReturned)) == False):
			error_info = self.callCpp("NET_DVR_GetLastError")
		# print("光学变倍获取失败：" + str(error_info))
		# else:
		# 	print("光学变倍获取成功")
		return m_struFocusModeCfg.fOpticalZoomLevel

	# 修改光学变倍值
	def Change_CamZoom(self, zoomScale):
		m_struFocusModeCfg = self.NET_DVR_FOCUSMODE_CFG()
		dwReturned = ctypes.c_uint16(0)
		# print(callCpp("NET_DVR_GetDVRConfig"))
		if (self.callCpp("NET_DVR_GetDVRConfig", self.lUserID, 3305, self.lChannel, ctypes.byref(m_struFocusModeCfg),
						 76,
						 ctypes.byref(dwReturned)) == False):
			error_info = self.callCpp("NET_DVR_GetLastError")
		# print("光学变倍获取失败：" + str(error_info))
		else:
			# print("光学变倍获取成功")
			# print("当前光学变倍值：" + str(m_struFocusModeCfg.fOpticalZoomLevel))
			m_struFocusModeCfg.fOpticalZoomLevel = zoomScale
			if (self.callCpp("NET_DVR_SetDVRConfig", self.lUserID, 3306, self.lChannel,
							 ctypes.byref(m_struFocusModeCfg), 76) == False):
				error_info = self.callCpp("NET_DVR_GetLastError")
				print("光学变倍修改失败：" + str(error_info))
			else:
				print("光学变倍修改成功;修改后的数据为：" + str(m_struFocusModeCfg.fOpticalZoomLevel))
