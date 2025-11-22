"""
基础功能测试

测试基础模块的基本功能。
"""

import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from stock_ox import __version__, VERSION
from stock_ox.types import AccountType, OrderState, ExchangeId
from stock_ox.constants import STK_BIZ_BUY, STK_BIZ_SELL, BOARD_SH, BOARD_SZ
from stock_ox.utils import encode_str, decode_str, format_price
from stock_ox.exceptions import (
    OXApiError, 
    OXConnectionError, 
    OXLoginError, 
    OXOrderError,
    OXQueryError,
    OXDllError
)


def test_version():
    """测试版本信息"""
    assert __version__ == "0.1.0"
    assert VERSION == "0.1.0"


def test_account_type():
    """测试账户类型枚举"""
    assert AccountType.STOCK.value == '0'
    assert AccountType.OPTION.value == '1'
    assert AccountType.FUTURE.value == '2'
    assert AccountType.CREDIT.value == '3'


def test_order_state():
    """测试委托状态枚举"""
    assert OrderState.NOT_REPORT.value == '0'
    assert OrderState.FILLED.value == '8'
    assert OrderState.CANCELED.value == '6'


def test_exchange_id():
    """测试交易所枚举"""
    assert ExchangeId.SH.value == '1'
    assert ExchangeId.SZ.value == '0'


def test_constants():
    """测试常量"""
    assert STK_BIZ_BUY == 100
    assert STK_BIZ_SELL == 101
    assert BOARD_SH == "10"
    assert BOARD_SZ == "00"


def test_encode_decode_str():
    """测试字符串编码解码"""
    test_str = "测试字符串"
    encoded = encode_str(test_str)
    decoded = decode_str(encoded)
    assert decoded == test_str


def test_encode_decode_utf8():
    """测试 UTF-8 编码解码"""
    test_str = "Hello World 测试"
    encoded = encode_str(test_str, encoding='utf-8')
    decoded = decode_str(encoded, encoding='utf-8')
    assert decoded == test_str


def test_format_price():
    """测试价格格式化"""
    assert format_price(9.9) == "9.90"
    assert format_price(10.5, precision=3) == "10.500"
    assert format_price(0.01) == "0.01"


def test_exceptions():
    """测试异常类"""
    # 测试基础异常
    error = OXApiError("Base error")
    assert str(error) == "Base error"
    assert isinstance(error, Exception)
    
    # 测试连接错误
    conn_error = OXConnectionError("Connection failed")
    assert str(conn_error) == "Connection failed"
    assert isinstance(conn_error, OXApiError)
    
    # 测试登录错误
    login_error = OXLoginError("Login failed")
    assert str(login_error) == "Login failed"
    assert isinstance(login_error, OXApiError)


def test_exception_inheritance():
    """测试异常继承关系"""
    assert issubclass(OXConnectionError, OXApiError)
    assert issubclass(OXLoginError, OXApiError)
    assert issubclass(OXOrderError, OXApiError)
    assert issubclass(OXQueryError, OXApiError)
    assert issubclass(OXDllError, OXApiError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

