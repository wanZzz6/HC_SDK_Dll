import Struct
import ctypes

a = b'\xe4\x07\x00\x00\t\x00\x00\x00\x11\x00\x00\x00\x0f\x00\x00\x00\x15\x00\x00\x008\x00\x00\x00'

b = Struct.NET_DVR_TIME.from_buffer_copy(a)
print(ctypes.sizeof(b), len(a))
print(list(a))
print(b.dwYear)
print(b.dwMonth)
print(b.dwDay)
print(b.dwHour)
print(b.dwMinute)
print(b.dwSecond)


