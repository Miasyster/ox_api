"""
回调接口测试模块

测试回调接口和数据转换功能。
"""

import pytest
from ctypes import POINTER, byref, c_int, c_bool
from stock_ox.spi import (
    OXTradeSpi,
    OnConnectedCallback,
    OnDisconnectedCallback,
    OnRspLogonCallback,
    OnRspTradeAccountsCallback,
    convert_error_field,
    convert_rsp_field,
)
from stock_ox.structs import (
    CRspErrorField,
    COXRspLogonField,
    COXRspTradeAcctField,
)
from stock_ox.utils import encode_str


class TestOXTradeSpi:
    """测试 OXTradeSpi 基类"""
    
    def test_spi_creation(self):
        """测试回调接口创建"""
        spi = OXTradeSpi()
        assert spi is not None
    
    def test_on_connected(self):
        """测试连接建立回调"""
        spi = OXTradeSpi()
        result = spi.on_connected()
        assert result == 0
    
    def test_on_disconnected(self):
        """测试连接断开回调"""
        spi = OXTradeSpi()
        result = spi.on_disconnected()
        assert result == 0
    
    def test_on_rsp_logon_default(self):
        """测试登录响应回调默认实现"""
        spi = OXTradeSpi()
        # 默认实现应该不抛出异常
        spi.on_rsp_logon(123, None, True, None)
        spi.on_rsp_logon(123, {'ErrorId': 1}, False, {'Account': 'test'})
    
    def test_on_rsp_trade_accounts_default(self):
        """测试交易账户响应回调默认实现"""
        spi = OXTradeSpi()
        # 默认实现应该不抛出异常
        spi.on_rsp_trade_accounts(123, None, True, None)
        spi.on_rsp_trade_accounts(123, {'ErrorId': 1}, False, {'TrdAcct': 'test'})


class TestCallbackTypeDefinitions:
    """测试回调函数类型定义"""
    
    def test_on_connected_callback_type(self):
        """测试 OnConnected 回调类型"""
        assert OnConnectedCallback is not None
    
    def test_on_disconnected_callback_type(self):
        """测试 OnDisconnected 回调类型"""
        assert OnDisconnectedCallback is not None
    
    def test_on_rsp_logon_callback_type(self):
        """测试 OnRspLogon 回调类型"""
        assert OnRspLogonCallback is not None
    
    def test_on_rsp_trade_accounts_callback_type(self):
        """测试 OnRspTradeAccounts 回调类型"""
        assert OnRspTradeAccountsCallback is not None


class TestConvertErrorField:
    """测试错误字段转换"""
    
    def test_convert_error_field_none(self):
        """测试 None 指针转换"""
        result = convert_error_field(None)
        assert result is None
    
    def test_convert_error_field_valid(self):
        """测试有效错误字段转换"""
        error = CRspErrorField()
        error.ErrorId = 1001
        error_bytes = encode_str("错误信息")[:128].ljust(128, b'\x00')
        from ctypes import memmove, addressof, sizeof
        # 正确方式：ErrorInfo 是一个 c_char 数组，可以直接使用 memmove
        memmove(addressof(error) + sizeof(c_int), error_bytes, 128)
        
        # 直接传递结构体实例
        result = convert_error_field(error)
        
        assert result is not None
        assert result['ErrorId'] == 1001
        assert len(result['ErrorInfo']) > 0
    
    def test_convert_error_field_zero_error_id(self):
        """测试错误 ID 为 0 的转换"""
        error = CRspErrorField()
        error.ErrorId = 0
        error_bytes = encode_str("成功")[:128].ljust(128, b'\x00')
        from ctypes import memmove, addressof, sizeof
        memmove(addressof(error) + sizeof(c_int), error_bytes, 128)
        
        # 直接传递结构体实例
        result = convert_error_field(error)
        
        assert result is not None
        assert result['ErrorId'] == 0
        assert len(result['ErrorInfo']) > 0


class TestConvertRspField:
    """测试响应字段转换"""
    
    def test_convert_rsp_field_none(self):
        """测试 None 指针转换"""
        result = convert_rsp_field(None)
        assert result is None
    
    def test_convert_rsp_field_logon(self):
        """测试登录响应字段转换"""
        field = COXRspLogonField()
        field.IntOrg = 12345
        field_bytes = encode_str("CUST001")[:24].ljust(24, b'\x00')
        from ctypes import memmove, addressof, sizeof
        # CustCode 在 IntOrg (4 bytes) 之后
        memmove(addressof(field) + sizeof(c_int), field_bytes, 24)
        field.AcctType = ord('0')
        account_bytes = encode_str("110060035050")[:24].ljust(24, b'\x00')
        # Account 在 IntOrg (4) + CustCode (24) + AcctType (1) = 29 之后
        memmove(addressof(field) + sizeof(c_int) + 24 + 1, account_bytes, 24)
        
        # 直接传递结构体实例
        result = convert_rsp_field(field)
        
        assert result is not None
        assert result['IntOrg'] == 12345
        assert result['AcctType'] == '0'
        assert len(result['CustCode']) > 0
        assert len(result['Account']) > 0
    
    def test_convert_rsp_field_trade_account(self):
        """测试交易账户响应字段转换"""
        field = COXRspTradeAcctField()
        custcode_bytes = encode_str("CUST002")[:24].ljust(24, b'\x00')
        from ctypes import memmove, addressof, sizeof
        # 使用结构体基地址 + 偏移量的方式
        offset = 0
        memmove(addressof(field) + offset, custcode_bytes, 24)
        offset += 24
        account_bytes = encode_str("110060035050")[:24].ljust(24, b'\x00')
        memmove(addressof(field) + offset, account_bytes, 24)
        offset += 24
        field.ExchangeId = ord('1')
        offset += 1
        boardid_bytes = encode_str("01")[:4].ljust(4, b'\x00')
        memmove(addressof(field) + offset, boardid_bytes, 4)
        offset += 4
        field.TrdAcctStatus = ord('1')
        offset += 1
        tracct_bytes = encode_str("A197407210")[:24].ljust(24, b'\x00')
        memmove(addressof(field) + offset, tracct_bytes, 24)
        offset += 24
        field.TrdAcctType = ord('1')
        
        # 直接传递结构体实例
        result = convert_rsp_field(field)
        
        assert result is not None
        assert result['ExchangeId'] == '1'
        assert result['TrdAcctStatus'] == '1'
        assert result['TrdAcctType'] == '1'
        assert len(result['CustCode']) > 0
        assert len(result['Account']) > 0
        assert len(result['BoardId']) > 0
        assert len(result['TrdAcct']) > 0


class TestCustomSpi:
    """测试自定义回调接口"""
    
    def test_custom_spi_override(self):
        """测试自定义 SPI 重写回调方法"""
        callback_called = []
        
        class CustomSpi(OXTradeSpi):
            def on_connected(self):
                callback_called.append('connected')
                return 1  # 返回非 0 值
            
            def on_rsp_logon(self, request, error, is_last, field):
                callback_called.append(('logon', request, error, is_last, field))
        
        spi = CustomSpi()
        result = spi.on_connected()
        assert result == 1
        assert 'connected' in callback_called
        
        spi.on_rsp_logon(123, None, True, {'Account': 'test'})
        assert ('logon', 123, None, True, {'Account': 'test'}) in callback_called
    
    def test_custom_spi_error_handling(self):
        """测试自定义 SPI 错误处理"""
        errors = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_logon(self, request, error, is_last, field):
                if error and error.get('ErrorId', 0) != 0:
                    errors.append(error)
        
        spi = CustomSpi()
        spi.on_rsp_logon(123, {'ErrorId': 1001, 'ErrorInfo': '登录失败'}, True, None)
        
        assert len(errors) == 1
        assert errors[0]['ErrorId'] == 1001
    
    def test_custom_spi_field_handling(self):
        """测试自定义 SPI 字段处理"""
        fields = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_trade_accounts(self, request, error, is_last, field):
                if field and not error:
                    fields.append(field)
        
        spi = CustomSpi()
        spi.on_rsp_trade_accounts(123, None, True, {'TrdAcct': 'A197407210'})
        spi.on_rsp_trade_accounts(123, {'ErrorId': 1}, True, None)
        
        assert len(fields) == 1
        assert fields[0]['TrdAcct'] == 'A197407210'

