"""
回调接口模块

实现回调接口的 Python 包装。
"""

from typing import Optional, Dict, Any
from ctypes import CFUNCTYPE, c_int, c_bool, POINTER
from .structs import (
    CRspErrorField,
    COXRspLogonField,
    COXRspTradeAcctField,
    COXOrderTicket,
    COXOrderFilledField,
    COXRspCancelTicketField,
    COXReqBatchOrderTicketField,
)
from .utils import struct_to_dict


# 定义回调函数类型（用于 C 函数指针）
# 注意：C++ 虚函数不能直接用 ctypes 回调，这些类型定义用于文档和类型检查

# OnConnected / OnDisconnected 回调类型
OnConnectedCallback = CFUNCTYPE(c_int)
OnDisconnectedCallback = CFUNCTYPE(c_int)

# OnRspLogon 回调类型
OnRspLogonCallback = CFUNCTYPE(
    None,  # return type (void)
    c_int,  # nRequest
    POINTER(CRspErrorField),  # pError
    c_bool,  # bLast
    POINTER(COXRspLogonField),  # pField
)

# OnRspTradeAccounts 回调类型
OnRspTradeAccountsCallback = CFUNCTYPE(
    None,  # return type (void)
    c_int,  # nRequest
    POINTER(CRspErrorField),  # pError
    c_bool,  # bLast
    POINTER(COXRspTradeAcctField),  # pField
)

# OnRtnOrder 回调类型
OnRtnOrderCallback = CFUNCTYPE(
    None,  # return type (void)
    POINTER(COXOrderTicket),  # pRtnOrderTicket
)

# OnRtnOrderFilled 回调类型
OnRtnOrderFilledCallback = CFUNCTYPE(
    None,  # return type (void)
    POINTER(COXOrderFilledField),  # pFilledInfo
)

# OnRspCancelTicket 回调类型
OnRspCancelTicketCallback = CFUNCTYPE(
    None,  # return type (void)
    c_int,  # nRequest
    POINTER(CRspErrorField),  # pError
    POINTER(COXRspCancelTicketField),  # pField
)

# OnRspBatchOrder 回调类型
OnRspBatchOrderCallback = CFUNCTYPE(
    None,  # return type (void)
    c_int,  # nRequest
    POINTER(CRspErrorField),  # pError
    POINTER(COXReqBatchOrderTicketField),  # pField
)


class OXTradeSpi:
    """OX 交易回调接口基类
    
    用户应该继承此类并重写需要处理的回调方法。
    """
    
    def on_connected(self) -> int:
        """连接建立回调
        
        Returns:
            0 表示成功
        """
        return 0
    
    def on_disconnected(self) -> int:
        """连接断开回调
        
        Returns:
            0 表示成功
        """
        return 0
    
    def on_rsp_logon(self, request: int, error: Optional[Dict[str, Any]], 
                     is_last: bool, field: Optional[Dict[str, Any]]) -> None:
        """登录响应回调
        
        Args:
            request: 请求编号
            error: 错误信息字典（如果发生错误），None 表示无错误
            is_last: 是否最后一条
            field: 响应字段字典（成功时），None 表示无数据
        """
        pass
    
    def on_rsp_trade_accounts(self, request: int, error: Optional[Dict[str, Any]], 
                              is_last: bool, field: Optional[Dict[str, Any]]) -> None:
        """交易账户响应回调
        
        Args:
            request: 请求编号
            error: 错误信息字典（如果发生错误），None 表示无错误
            is_last: 是否最后一条
            field: 响应字段字典（成功时），None 表示无数据
        """
        pass
    
    def on_rtn_order(self, field: Optional[Dict[str, Any]]) -> None:
        """委托回报回调
        
        Args:
            field: 委托回报字段字典，None 表示无数据
        """
        pass
    
    def on_rtn_order_filled(self, field: Optional[Dict[str, Any]]) -> None:
        """成交回报回调
        
        Args:
            field: 成交回报字段字典，None 表示无数据
        """
        pass
    
    def on_rsp_cancel_ticket(self, request: int, error: Optional[Dict[str, Any]], 
                             field: Optional[Dict[str, Any]]) -> None:
        """撤单响应回调
        
        Args:
            request: 请求编号
            error: 错误信息字典（如果发生错误），None 表示无错误
            field: 响应字段字典（成功时），None 表示无数据
        """
        pass
    
    def on_rsp_batch_order(self, request: int, error: Optional[Dict[str, Any]], 
                           field: Optional[Dict[str, Any]]) -> None:
        """批量下单响应回调
        
        Args:
            request: 请求编号
            error: 错误信息字典（如果发生错误），None 表示无错误
            field: 响应字段字典（成功时），None 表示无数据
        """
        pass


def convert_error_field(error_ptr: Optional[Any]) -> Optional[Dict[str, Any]]:
    """将 C 错误字段转换为 Python 字典
    
    Args:
        error_ptr: C 错误字段指针或结构体实例
        
    Returns:
        错误信息字典，如果指针为 None 则返回 None
    """
    if error_ptr is None:
        return None
    
    # 如果是指针，获取其内容；如果是结构体实例，直接使用
    if hasattr(error_ptr, 'contents'):
        error = error_ptr.contents
    else:
        error = error_ptr
    
    return struct_to_dict(error)


def convert_rsp_field(field_ptr: Optional[Any]) -> Optional[Dict[str, Any]]:
    """将 C 响应字段转换为 Python 字典
    
    Args:
        field_ptr: C 响应字段指针或结构体实例
        
    Returns:
        响应字段字典，如果指针为 None 则返回 None
    """
    if field_ptr is None:
        return None
    
    # 如果是指针，获取其内容；如果是结构体实例，直接使用
    if hasattr(field_ptr, 'contents'):
        field = field_ptr.contents
    else:
        field = field_ptr
    
    return struct_to_dict(field)


def convert_order_ticket(field_ptr: Optional[Any]) -> Optional[Dict[str, Any]]:
    """将 C 委托回报字段转换为 Python 字典
    
    Args:
        field_ptr: C 委托回报字段指针或结构体实例
        
    Returns:
        委托回报字典，如果指针为 None 则返回 None
    """
    return convert_rsp_field(field_ptr)


def convert_order_filled(field_ptr: Optional[Any]) -> Optional[Dict[str, Any]]:
    """将 C 成交回报字段转换为 Python 字典
    
    Args:
        field_ptr: C 成交回报字段指针或结构体实例
        
    Returns:
        成交回报字典，如果指针为 None 则返回 None
    """
    return convert_rsp_field(field_ptr)

