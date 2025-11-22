"""
异常定义模块

定义自定义异常类，用于 API 错误处理。
"""


class OXApiError(Exception):
    """OX API 基础异常类"""
    pass


class OXConnectionError(OXApiError):
    """连接错误异常"""
    pass


class OXLoginError(OXApiError):
    """登录错误异常"""
    pass


class OXOrderError(OXApiError):
    """下单错误异常"""
    pass


class OXQueryError(OXApiError):
    """查询错误异常"""
    pass


class OXDllError(OXApiError):
    """DLL 加载错误异常"""
    pass

