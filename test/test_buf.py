import Struct
import ctypes

a = b'\xe4\x07\x00\x00\t\x00\x00\x00\x11\x00\x00\x00\x0f\x00\x00\x00\x15\x00\x00\x008\x00\x00\x00'
print(list(a))

b = Struct.NET_DVR_TIME.from_buffer_copy(a)
print('结构体大小：', ctypes.sizeof(b), '缓存块大小：', len(a))

print('结构体成员：{}-{}-{} {}:{}:{}'.format(b.dwYear, b.dwMonth, b.dwDay, b.dwHour, b.dwMinute, b.dwSecond))
