import ctypes
import datetime
import os
import re
import uuid

__all__ = ['load_dll', 'gen_file_name', 'gen_callback', 'gen_structure', 'gen_auto_from_doc']

struct_body = re.compile(r'struct\s*\{(.*)\}\s*([\w_]+)', re.DOTALL)
callback_body = re.compile(r'typedef\s(\w+)\s*\(\s*CALLBACK[^\w]*?(\w+).*?\((.*?)\)\s*;', re.DOTALL)
num_pattern = re.compile(r'\s*(\w+)\s+(\*)*\s*(\w+)\s*\[*(\s*\w+\s*)*\]*\s*[;,]?')

type_trans_map = {
    'char': 'c_char',
    'void': 'None'
}
type_trans_map_p = {
    'void': 'c_void_p',
    'BYTE': 'POINTER(c_ubyte)',
    'char': 'POINTER    (c_char)'
}


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


def gen_structure(doc_str: str, tab_size: int = 4) -> str:
    try:
        body_content, structure_name = struct_body.search(doc_str).groups()
    except AttributeError:
        exit('\n格式不匹配')

    structure_numbers = num_pattern.findall(body_content)
    fields = ["('{}', {}),".format(name, type_trans_map_p.get(type_, type_) if point_flag else (
        '{} * {}'.format(type_, array_len) if array_len else type_)) for
              type_, point_flag, name, array_len in structure_numbers]

    fields = '\n{}'.format(' ' * tab_size * 2).join(fields)
    result = "class {stru_name}(Structure):\n{indent}_fields_ = [\n{indent}{indent}{fields}\n{indent}]".format(
        stru_name=structure_name, indent=' ' * tab_size, fields=fields)

    return result


def gen_callback(doc_str: str, tab_size: int = 4) -> str:
    try:
        return_type, func_name, define_body = callback_body.search(doc_str).groups()
    except AttributeError:
        exit('格式不匹配')

    params = num_pattern.findall(define_body)
    in_define = [type_trans_map.get(return_type, return_type)]
    in_py_func = []
    for type_, point_flag, name, _ in params:
        type_ = type_trans_map_p.get(type_, type_) if point_flag else type_trans_map.get(type_, type_)
        in_define.append(type_)
        in_py_func.append("{}: {}".format(name, type_))

    temp = "{} = CFUNCTYPE({})\n\ndef _名称({}) -> {}:\n{}pass\n\n名称 = {}(_名称)".format(
        func_name, ', '.join(in_define), ', '.join(in_py_func), in_define[0], ' ' * tab_size, func_name
    )

    return temp


def gen_auto_from_doc(doc_str):
    if callback_body.search(doc_str):
        return gen_callback(doc_str)
    elif struct_body.search(doc_str):
        return gen_structure(doc_str)
    exit('格式不匹配')


if __name__ == '__main__':
    import sys

    print('请复制海康SDK文档内容并粘贴到此处，并按回车')
    text = ''
    while True:
        t = sys.stdin.readline().strip()
        if not t:
            break
        text = text + t
    print(gen_auto_from_doc(text))
