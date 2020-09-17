# 海康SDK二次开发

## todo

- [ ] 抽象出通用接口，每类类设备继承，如摄像头，HKIPCam，门禁：HKDoor

---

## 开发指导

想要正确调用dll文件，你要找到正确的调用约定，必须查看C头文件或要调用的函数的文档。
整数、字节对象和（unicode）字符串是唯一可以在这些函数调用中直接用作参数的本地Python对象。
它们都不作为C语言NULL指针传递，字节对象和字符串作为指针传递给包含它们的数据的内存块（char*或wchar_t*）。
Python整数作为平台默认的C int类型传递，它们的值被屏蔽以适合于C类型。在继续使用其他参数类型调用函数之前，
我们必须了解更多关于ctypes数据类型的信息。

### Python ctypes 数据类型表
        
| ctypes type  | C type                                   | Python type              |
| ------------ | ---------------------------------------- | ------------------------ |
| c_bool       | \_Bool                                   | bool (1)                 |
| c_char、CHAR  | char                                     | 1-character bytes object |
| c_wchar、WCHAR| wchar_t                                  | 1-character string       |
| c_byte、BYTE、BOOLEAN  | char                            | int                      |
| c_ubyte       | unsigned char                            | int                      |
| c_short       | short                                    | int                      |
| c_ushort、WORD、USHORT| unsigned short                    | int                      |
| c_int、INT    | int                                      | int                      |
| c_uint、UINT  | unsigned int                             | int                      |
| c_long、BOOL  | long                                     | int                      |
| c_ulong、DWORD| unsigned long                            | int                      |
| c_longlong   | \_\_int64 or long long                   | int                      |
| c_ulonglong  | unsigned \_\_int64 or unsigned long long | int                      |
| c_size_t     | size_t                                   | int                      |
| c_ssize_t    | ssize_t or Py_ssize_t                    | int                      |
| c_float、FLOAT| float                                    | float                    |
|c_double、DOUBLE| double                                  | float                   |
| c_longdouble | long double                              | float                    |
| c_char_p     | char \* (NUL terminated)                 | bytes object or None     |
| c_wchar_p    | wchar_t \* (NUL terminated)              | string or None           |
| c_void_p     | void \*                                  | int or None              |


### 开发方法

### 参数

1. 基本类型：转换参照上表
2. 指针类型： 传入 `byref(xxx)` 
3. char* : 传入 `bytes(xxx, 'utf-8'))`
4. 缓冲区指针：
    - 开辟：`buf = ctypes.create_string_buffer(缓冲大小)`
    - 读取: `buf.raw` 或者 `buf.value`
5. `LPDWORD`
    - 方式一：先创建 `a = ctypes.c_ulong(0)`，再传入 `bytef(a)`，事后打印 `a.value`
    - 方式二：先创建 `a = LPDWORD(ctypes.c_ulong(0))`， 直接传入 `a`，事后打印 `a[0]`
### 回调函数

1. 声明：`callback = CFUNCTYPE（返回值类型，参数1类型， 参数2类型，。。。）`
2. 定义 python 实现方法 `imp_callback(参数1，参数2，。。。)`
3. 创建回调函数对象：`func = CMPFUNC（imp_callback）`

### 错误码

定位到执行SDK失败的函数名，从 《海康设备SDK使用手册.chm》 文件中搜索该函数或者直接搜索`NET_DVR_GetLastError`，查看相关的错误信息

### 其他

- `sizeof()` 获取C（结构体）对象大小
- `addressof()` 取C对象内存地址
- `string_at(addr[, size])` 从地址中取字符数据
- 👍`cast(obj, typ)` 强制转换
- `Structure.from_buffer_copy(b'xxxx')` 从bytes流中创建结构体
- `cast(obj, POINTER(Structure))` 将一个指针转换为结构体指针