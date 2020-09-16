import ctypes
import datetime
import os
import re
import uuid

struct_body = re.compile(r'struct\s*\{(.*)\}\s*([\w_]+)', re.DOTALL)
num_pattern = re.compile(r'\s*(\w+)\s+(\w+)\s*\[*(\s*\w+\s*)*\]*\s*;')


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
    fields = ["('{}', {}),".format(name, '{} * {}'.format(type_, array_len) if array_len else type_) for
              type_, name, array_len in structure_numbers]

    fields = '\n{}'.format(' ' * tab_size * 2).join(fields)
    result = "class {stru_name}(Structure):\n{indent}_fields_ = [\n{indent}{indent}{fields}\n{indent}]".format(
        stru_name=structure_name, indent=' ' * tab_size, fields=fields)

    return result


if __name__ == '__main__':
    import sys

    print('请复制海康SDK文档内容并粘贴到此处，并按回车')
    text = ''
    while True:
        t = sys.stdin.readline().strip()
        if not t:
            break
        text = text + t
    print(gen_structure(text))
