"""
类型枚举模块

定义 Python 枚举类，提供类型转换函数。
映射自 C++ 头文件 OXTradeApiType.h
"""

from enum import Enum
from typing import Union


class AccountType(Enum):
    """账户类型枚举
    
    映射自 C++ enum OXAccountType
    """
    STOCK = '0'     # 现货
    OPTION = '1'    # 期权
    FUTURE = '2'    # 期货
    CREDIT = '3'    # 信用交易
    
    def to_char(self) -> bytes:
        """转换为 C char 类型"""
        return self.value.encode('utf-8')
    
    @classmethod
    def from_char(cls, value: Union[str, bytes, int]) -> 'AccountType':
        """从 C char 类型转换
        
        Args:
            value: 可以是字符、字节或整数
            
        Returns:
            AccountType 枚举值
        """
        if isinstance(value, bytes):
            value = value.decode('utf-8') if value else '0'
        elif isinstance(value, int):
            value = chr(value)
        
        for account_type in cls:
            if account_type.value == value:
                return account_type
        
        # 默认返回 STOCK
        return cls.STOCK


class OrderState(Enum):
    """委托状态枚举
    
    映射自 C++ enum OXOrderState
    """
    NOT_REPORT = '0'            # 未报
    REPORTING = '1'             # 正报
    REPORTED = '2'              # 已报
    CANCELING = '3'             # 已报撤单
    PARTIAL_CANCELING = '4'     # 部成待撤
    PARTIAL_CANCELED = '5'      # 部成部分撤
    CANCELED = '6'              # 已撤
    PARTIAL_FILLED = '7'        # 部成成交
    FILLED = '8'                # 已成交
    REJECTED = '9'              # 废单
    REPORT_WAITING = 'A'        # 报盘等待 - 写入报盘队列未成功
    REPORT_ACK = 'B'            # 报盘确认 - 已经成功写入接口库,报盘回报写入确认
    
    # 以下状态只在组合订单中处理
    NEED_SEND = 'N'             # 需报送 - OCO/BRK组合，委托1已报，委托0未报，委托1未成前处于中间状态
    DIVIDEND_CANCELED = 'D'     # 红利息止 - 红利利息终止
    EXPIRED = 'E'               # 过期终止
    TRIGGER_AGAIN = 'T'         # 再次触发 - 前置条件满足，已触发，下一日再次触发
    
    def to_char(self) -> bytes:
        """转换为 C char 类型"""
        return self.value.encode('utf-8')
    
    @classmethod
    def from_char(cls, value: Union[str, bytes, int]) -> 'OrderState':
        """从 C char 类型转换
        
        Args:
            value: 可以是字符、字节或整数
            
        Returns:
            OrderState 枚举值
        """
        if isinstance(value, bytes):
            value = value.decode('utf-8') if value else '0'
        elif isinstance(value, int):
            value = chr(value)
        
        for order_state in cls:
            if order_state.value == value:
                return order_state
        
        # 默认返回 NOT_REPORT
        return cls.NOT_REPORT


class ExchangeId(Enum):
    """交易所枚举"""
    SH = '1'        # 上海证券交易所
    SZ = '0'        # 深圳证券交易所
    
    def to_char(self) -> bytes:
        """转换为 C char 类型"""
        return self.value.encode('utf-8')
    
    @classmethod
    def from_char(cls, value: Union[str, bytes, int]) -> 'ExchangeId':
        """从 C char 类型转换
        
        Args:
            value: 可以是字符、字节或整数
            
        Returns:
            ExchangeId 枚举值
        """
        if isinstance(value, bytes):
            value = value.decode('utf-8') if value else '0'
        elif isinstance(value, int):
            value = chr(value)
        
        for exchange in cls:
            if exchange.value == value:
                return exchange
        
        # 默认返回 SZ
        return cls.SZ


def account_type_to_char(account_type: Union[AccountType, str, int]) -> bytes:
    """将账户类型转换为 C char 类型
    
    Args:
        account_type: 账户类型，可以是 AccountType 枚举、字符串或整数
        
    Returns:
        编码后的字节串
    """
    if isinstance(account_type, AccountType):
        return account_type.to_char()
    elif isinstance(account_type, str):
        return AccountType(account_type).to_char()
    elif isinstance(account_type, int):
        return AccountType.from_char(account_type).to_char()
    else:
        raise ValueError(f"Invalid account type: {account_type}")


def order_state_to_char(order_state: Union[OrderState, str, int]) -> bytes:
    """将委托状态转换为 C char 类型
    
    Args:
        order_state: 委托状态，可以是 OrderState 枚举、字符串或整数
        
    Returns:
        编码后的字节串
    """
    if isinstance(order_state, OrderState):
        return order_state.to_char()
    elif isinstance(order_state, str):
        return OrderState(order_state).to_char()
    elif isinstance(order_state, int):
        return OrderState.from_char(order_state).to_char()
    else:
        raise ValueError(f"Invalid order state: {order_state}")


def exchange_id_to_char(exchange_id: Union[ExchangeId, str, int]) -> bytes:
    """将交易所 ID 转换为 C char 类型
    
    Args:
        exchange_id: 交易所 ID，可以是 ExchangeId 枚举、字符串或整数
        
    Returns:
        编码后的字节串
    """
    if isinstance(exchange_id, ExchangeId):
        return exchange_id.to_char()
    elif isinstance(exchange_id, str):
        return ExchangeId(exchange_id).to_char()
    elif isinstance(exchange_id, int):
        return ExchangeId.from_char(exchange_id).to_char()
    else:
        raise ValueError(f"Invalid exchange ID: {exchange_id}")
