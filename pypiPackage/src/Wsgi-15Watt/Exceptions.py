"""
    The exceptions that can be thrown by the application.

    If you like to create your own exception, please derive them from Base.
"""


class Base(Exception):
    """
    Base class of all Wsgi exceptions.
    """
    def __init__(self, returnCode: int = 500, returnMsg: str = 'Internal server _error'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg

    @property
    def returnCode(self) -> int:
        return self.__returnCode

    @property
    def returnMsg(self) -> str:
        return self.__returnMsg


class ProtocolException(Base):
    def __init__(self, returnCode: int = 500, returnMsg: str = 'Protocol exception'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class ParamNotFound(Base):
    def __init__(self, returnCode: int = 400, returnMsg: str = 'Parameter not found'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class ValueNotFound(Base):
    def __init__(self, returnCode: int = 500, returnMsg: str = 'Value not found'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class FileNotFound(Base):
    def __init__(self, returnCode: int = 404, returnMsg: str = 'File not found'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class NotAllowedHttpMethod(Base):
    def __init__(self, returnCode: int = 405, returnMsg: str = 'Not allowed HTTP method'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class NotAllowedHttpResponseCode(Base):
    def __init__(self, returnCode: int = 500, returnMsg: str = 'Not allowed HTTP response code'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class InvalidData(Base):
    def __init__(self, returnCode: int = 500, returnMsg: str = 'Invalid data'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class NotUnique(Base):
    def __init__(self, returnCode: int = 500, returnMsg: str = 'Not unique'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg


class Unauthorized(Base):
    def __init__(self, returnCode: int = 401, returnMsg: str = 'Unauthorized'):
        self.__returnCode = returnCode
        self.__returnMsg = returnMsg
