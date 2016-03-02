import ctypes
from enum import Enum
import os


class PageSegMode(Enum):
    PSM_OSD_ONLY = 0
    PSM_AUTO_OSD = 1
    PSM_AUTO_ONLY = 2
    PSM_AUTO = 3
    PSM_SINGLE_COLUMN = 4
    PSM_SINGLE_BLOCK_VERT_TEX = 5
    PSM_SINGLE_BLOCK = 6
    PSM_SINGLE_LINE = 7
    PSM_SINGLE_WORD = 8
    PSM_CIRCLE_WORD = 9
    PSM_SINGLE_CHAR = 10
    PSM_SPARSE_TEXT = 11
    PSM_SPARSE_TEXT_OSD = 12
    PSM_COUNT = 13


class ConfidenceChar(ctypes.Structure):
    _fields_ = (('letter', ctypes.c_char),
                ('percent', ctypes.c_float))

class ConfidenceWord(ctypes.Structure):
    _fields_ = (('word', ctypes.POINTER(ctypes.c_char)),
                ('percent', ctypes.c_float))

class ConfidenceWordInit(ctypes.Structure):
    _fields_ = (('cw', ctypes.POINTER(ConfidenceWord)),
                ('length', ctypes.c_int))

class TesseractVariable(ctypes.Structure):
    _fields_ = (('name', ctypes.POINTER(ctypes.c_char)),
                ('value', ctypes.POINTER(ctypes.c_char)))

class TesseractConfig(ctypes.Structure):
    _fields_ = (('lang', ctypes.c_char * 8),
                ('variables_count', ctypes.c_int),
                ('variables', ctypes.POINTER(TesseractVariable)),
                ('psm', ctypes.c_int),
                ('hocr', ctypes.c_bool))

    def __init__(self, lang='eng', psm=0, hocr=False):
        if type(psm) == PageSegMode:
            psm = psm.value
        lang = lang.encode('ascii')
        self.obj_variables = []
        super().__init__(lang=lang, variables_count=0, psm=psm, hocr=hocr)

    def add_variable(self, name, value):
        name = name.encode('ascii')
        value = value.encode('ascii')
        self.obj_variables.append(TesseractVariable(name=(ctypes.c_char * len(name))(*name), value=(ctypes.c_char * len(value))(*value)))

        self.variables_count += len(self.obj_variables)
        self.variables = (TesseractVariable * self.variables_count)(*self.obj_variables)


class LibTesseract:
    my_path = os.path.dirname(os.path.realpath(__file__))
    lib = ctypes.CDLL(my_path + '/cppcode/libpyslibtesseract.so')

    lib.simple_read.restype = ctypes.POINTER(ctypes.c_char)
    lib.simple_read.argtypes = (TesseractConfig, ctypes.c_char_p)

    lib.read_and_get_confidence_char.restype = ctypes.POINTER(ConfidenceChar)
    lib.read_and_get_confidence_char.argtypes = (TesseractConfig, ctypes.c_char_p)

    lib.read_and_get_confidence_word.restype = ConfidenceWordInit
    lib.read_and_get_confidence_word.argtypes = (TesseractConfig, ctypes.c_char_p)

    lib.freeme.restype = None
    lib.freeme.argtypes = (ctypes.c_void_p,)

    @staticmethod
    def _get_arg_image_dir(image_dir):
        """Transform variable image path to understandable array in C"""
        if not os.path.exists(image_dir):
            raise ValueError('The "{}" file does not exist!'.format(image_dir))

        return image_dir.encode('utf-8')

    @classmethod
    def simple_read(cls, config, image_dir):
        buff_pointer = cls.lib.simple_read(config, cls._get_arg_image_dir(image_dir))
        buff_value = ctypes.cast(buff_pointer, ctypes.c_char_p).value.decode('utf-8')

        cls.lib.freeme(buff_pointer)

        if config.hocr:
            return buff_value[:-1]
        else:
            return buff_value[:-2]

    @classmethod
    def read_and_get_confidence_char(cls, config, image_dir):
        lib_return = cls.lib.read_and_get_confidence_char(config, cls._get_arg_image_dir(image_dir))
        to_return = []
        for i in lib_return:
            if i.letter == b'\x00':
                break
            to_return.append((i.letter.decode('utf-8'), i.percent))

        cls.lib.freeme(lib_return)

        return to_return

    @classmethod
    def read_and_get_confidence_word(cls, config, image_dir):
        lib_return = cls.lib.read_and_get_confidence_word(config, cls._get_arg_image_dir(image_dir))
        to_return = []
        for i in range(lib_return.length):
            current = lib_return.cw[i]
            to_return.append((ctypes.cast(current.word, ctypes.c_char_p).value.decode('utf-8'), current.percent))

        cls.lib.freeme(lib_return.cw)

        return to_return


if __name__ == '__main__':
    # Char
    config_single_char = TesseractConfig(psm=PageSegMode.PSM_SINGLE_CHAR)
    config_single_char.add_variable('tessedit_char_whitelist', 'QWERTYUIOPASDFGHJKLZXCVBNM')
    print(LibTesseract.read_and_get_confidence_char(config_single_char, 'char1.png'))
    print(LibTesseract.read_and_get_confidence_char(config_single_char, 'char2.png'))

    # Line
    config_line = TesseractConfig(psm=PageSegMode.PSM_SINGLE_LINE)
    print(LibTesseract.simple_read(config_line, 'phrase1.png'))
    print(LibTesseract.read_and_get_confidence_word(config_line, 'phrase1.png'))
    print(LibTesseract.simple_read(config_line, 'phrase2.png'))
    print(LibTesseract.read_and_get_confidence_word(config_line, 'phrase2.png'))

    # hOCR
    config_line_with_hocr = TesseractConfig(psm=PageSegMode.PSM_SINGLE_LINE, hocr=True)
    print(LibTesseract.simple_read(config_line_with_hocr, 'phrase3.png'))
    config_line.hocr = True
    print(LibTesseract.simple_read(config_line, 'phrase1.png'))
