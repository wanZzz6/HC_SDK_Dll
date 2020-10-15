import ctypes
import ctypes.wintypes
import datetime
import os
import uuid
from typing import Union, List
from logging import getLogger

logger = getLogger('HK_utils')


def load_dll(path):
    cwd = os.getcwd()
    dir_name, file_name = os.path.split(os.path.abspath(path))
    try:
        os.chdir(dir_name)
        dll_lib = ctypes.WinDLL(file_name)
        return dll_lib
    finally:
        os.chdir(cwd)


def gen_file_name(extention='jpg', way='time') -> str:
    if way == 'time':
        name = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S.%f')
    else:
        name = uuid.uuid4().hex
    return "{}.{}".format(name, extention)


def assignByteArray(c_array_type, value: str, encoding='gbk'):
    """
    为 c_byte_Array 数组对象赋值
    """
    # todo 通过指针赋值
    return c_array_type(*value.encode(encoding))


def assignIntArray(c_int_type, value: Union[str, List[int]]):
    """
    为c_ulong_Array 或者 c_ushort_Array 数组对象赋值
    """
    # todo 通过指针赋值
    return c_int_type(*map(int, value))


def createStructure(structure, param: dict = None):
    """根据参数自动匹配数据类型并创建结构体"""
    # 创建
    instance = structure()
    if not param:
        return instance
    # 赋值
    for k, v in param.items():
        if hasattr(structure, k):
            # todo 完善其他类型
            field_type = getattr(instance, k).__class__
            # print(field_type, issubclass(field_type, ctypes.Structure), instance(v, field_type))
            if 'c_byte_Array' in field_type.__name__:
                setattr(instance, k, assignByteArray(field_type, str(v)))
            elif 'c_ulong_Array' in field_type.__name__ or 'c_ushort_Array' in field_type.__name__:
                setattr(instance, k, assignIntArray(field_type, v))
            elif field_type in (
                    int, ctypes.c_short, ctypes.c_int, ctypes.c_longlong, ctypes.c_ushort, ctypes.c_ulong,
                    ctypes.c_long):
                setattr(instance, k, int(v))
            elif 'c_byte' is ctypes.c_byte:
                if isinstance(v, int):
                    setattr(instance, k, v)
                elif isinstance(v, str) and len(k) == 1:
                    setattr(instance, k, ord(v))
                else:
                    logger.warning("Can't assign %s to a c_byte type!", v)
            elif issubclass(field_type, ctypes.Structure) and isinstance(v, field_type):
                setattr(instance, k, v)
            else:
                logger.error('结构体字段类型赋值暂时不可用，请手动完善此处代码😂😂😂 - %s.%s - %s', instance.__class__.__name__, k,
                             getattr(instance, k).__class__)
        else:
            logger.warning('Structure `{}` has no attribute: {}'.format(instance, k))
    return instance


__all__ = [i for i in globals() if i[:1] != '_']