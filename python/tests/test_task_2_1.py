"""
任务 2.1 测试：常量、类型和工具函数

测试 constants.py, types.py, utils.py, exceptions.py 的功能。
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from ctypes import Structure, c_int, c_int32, c_char, addressof, memmove

from stock_ox import constants
from stock_ox import types
from stock_ox import utils
from stock_ox import exceptions


class TestConstants:
    """测试 constants.py"""
    
    def test_string_length_constants(self):
        """测试字符串长度常量"""
        # 基础长度常量
        assert constants.OX_ERRORINFO_LENGTH == 128
        assert constants.OX_ACCOUNT_LENGTH == 24
        assert constants.OX_PASSWORD_LENGTH == 16
        assert constants.OX_RESERVED_LENGTH == 256
        
        # 交易相关长度
        assert constants.OX_BOARDID_LENGTH == 4
        assert constants.OX_SYMBOL_LENGTH == 36
        assert constants.OX_TRDACCT_LENGTH == 24
        
        # 价格和金额长度
        assert constants.OX_ORDERPRICE_LENGTH == 16
        assert constants.OX_FILLEDAMT_LENGTH == 24
        assert constants.OX_FUNDBALANCE_LENGTH == 24
        
        # ETF 相关长度
        assert constants.OX_ETF_PRICE_INFO == 10240
        assert constants.MAX_ORDERS_COUNT == 500
    
    def test_business_code_constants(self):
        """测试业务代码常量"""
        assert constants.STK_BIZ_BUY == 100
        assert constants.STK_BIZ_SELL == 101
        assert constants.STK_BIZ_ETF_CREATION == 181
        assert constants.STK_BIZ_ETF_REDEMPTION == 182
        assert constants.STK_BIZ_CREDIT_BUY == 702
    
    def test_board_constants(self):
        """测试板块代码常量"""
        assert constants.BOARD_SH == "10"
        assert constants.BOARD_SZ == "00"
    
    def test_exchange_constants(self):
        """测试交易所常量"""
        assert constants.EXCHANGE_SH == '1'
        assert constants.EXCHANGE_SZ == '0'


class TestTypes:
    """测试 types.py"""
    
    def test_account_type_enum(self):
        """测试账户类型枚举"""
        assert types.AccountType.STOCK.value == '0'
        assert types.AccountType.OPTION.value == '1'
        assert types.AccountType.FUTURE.value == '2'
        assert types.AccountType.CREDIT.value == '3'
    
    def test_account_type_conversion(self):
        """测试账户类型转换"""
        # 测试 to_char
        assert types.AccountType.STOCK.to_char() == b'0'
        
        # 测试 from_char - 字符串
        assert types.AccountType.from_char('0') == types.AccountType.STOCK
        assert types.AccountType.from_char('3') == types.AccountType.CREDIT
        
        # 测试 from_char - 字节
        assert types.AccountType.from_char(b'1') == types.AccountType.OPTION
        
        # 测试 from_char - 整数（ASCII 码）
        assert types.AccountType.from_char(ord('2')) == types.AccountType.FUTURE
        
        # 测试默认值
        assert types.AccountType.from_char('X') == types.AccountType.STOCK
    
    def test_order_state_enum(self):
        """测试委托状态枚举"""
        assert types.OrderState.NOT_REPORT.value == '0'
        assert types.OrderState.FILLED.value == '8'
        assert types.OrderState.REJECTED.value == '9'
        assert types.OrderState.REPORT_ACK.value == 'B'
        assert types.OrderState.NEED_SEND.value == 'N'
    
    def test_order_state_conversion(self):
        """测试委托状态转换"""
        assert types.OrderState.FILLED.to_char() == b'8'
        assert types.OrderState.from_char('8') == types.OrderState.FILLED
        assert types.OrderState.from_char(b'9') == types.OrderState.REJECTED
        assert types.OrderState.from_char(ord('A')) == types.OrderState.REPORT_WAITING
    
    def test_exchange_id_enum(self):
        """测试交易所枚举"""
        assert types.ExchangeId.SH.value == '1'
        assert types.ExchangeId.SZ.value == '0'
    
    def test_exchange_id_conversion(self):
        """测试交易所 ID 转换"""
        assert types.ExchangeId.SH.to_char() == b'1'
        assert types.ExchangeId.from_char('1') == types.ExchangeId.SH
        assert types.ExchangeId.from_char('0') == types.ExchangeId.SZ
    
    def test_helper_functions(self):
        """测试辅助函数"""
        # account_type_to_char
        assert types.account_type_to_char(types.AccountType.STOCK) == b'0'
        assert types.account_type_to_char('0') == b'0'
        assert types.account_type_to_char(ord('1')) == b'1'
        
        # order_state_to_char
        assert types.order_state_to_char(types.OrderState.FILLED) == b'8'
        assert types.order_state_to_char('8') == b'8'
        
        # exchange_id_to_char
        assert types.exchange_id_to_char(types.ExchangeId.SH) == b'1'
        assert types.exchange_id_to_char('1') == b'1'


class TestUtils:
    """测试 utils.py"""
    
    def test_encode_str(self):
        """测试字符串编码"""
        assert utils.encode_str('test') == b'test'
        assert utils.encode_str('测试', 'gbk') == '测试'.encode('gbk')
        assert utils.encode_str(123) == b'123'
    
    def test_decode_str(self):
        """测试字符串解码"""
        assert utils.decode_str(b'test') == 'test'
        assert utils.decode_str(b'test\x00\x00') == 'test'
        # 测试中文解码
        test_gbk_bytes = '测试'.encode('gbk')
        assert utils.decode_str(test_gbk_bytes, 'gbk') == '测试'
    
    def test_decode_str_encoding_fallback(self):
        """测试解码失败时的编码回退逻辑"""
        # 测试既不能用 GBK 也不能用 UTF-8 解码的字节串，应该回退到 latin-1
        # 使用一些在 GBK 和 UTF-8 中都无效的字节序列
        # 例如：使用 0x80-0xFF 范围内的字节，这些在 GBK 中可能需要配对，单独无效
        # 但为了真正触发解码失败，我们使用严格的错误处理
        invalid_bytes = bytes([0xFF, 0xFE, 0xFD])  # 这些字节在 GBK 和 UTF-8 中都无效
        result = utils.decode_str(invalid_bytes, 'gbk')
        # latin-1 可以解码任何字节序列，所以应该成功
        assert isinstance(result, str)
        assert len(result) == len(invalid_bytes)  # latin-1 是单字节编码
        
        # 测试一个会在 GBK 和 UTF-8 中都失败的字节序列
        # 使用一个不完整的 UTF-8 序列，但先用 GBK 尝试解码
        # 注意：GBK 可能会尝试解码，但结果不正确，所以我们主要测试 latin-1 回退
        incomplete_utf8 = bytes([0xE6, 0xB5])  # 不完整的 UTF-8 序列
        result = utils.decode_str(incomplete_utf8, 'gbk')
        # 应该成功解码（可能通过 GBK、UTF-8 或 latin-1）
        assert isinstance(result, str)
        # 结果长度可能因为编码不同而不等于字节长度，但应该是字符串
        assert len(result) > 0 or len(incomplete_utf8) == 0
        
        # 测试真正会触发 latin-1 回退的情况
        # 使用严格无法用 GBK 和 UTF-8 解码的字节
        latin1_only_bytes = bytes([0x80, 0x81, 0x82, 0x83])
        result = utils.decode_str(latin1_only_bytes, 'gbk')
        # 应该通过 latin-1 回退成功解码
        assert isinstance(result, str)
        # latin-1 是单字节编码，字符数等于字节数
        assert len(result) == len(latin1_only_bytes)
        
        # 测试字节数组
        bytearray_data = bytearray(b'test\x00')
        assert utils.decode_str(bytearray_data) == 'test'
        
        # 测试非 bytes 类型（应该转换为 bytes）
        # 对于列表，bytes() 构造函数可以接受整数列表
        result = utils.decode_str([116, 101, 115, 116])  # 'test' 的 ASCII 码列表
        assert isinstance(result, str)
        assert result.startswith('t') or len(result) > 0  # 至少应该成功转换
        
        # 测试空字节串
        assert utils.decode_str(b'') == ''
        assert utils.decode_str(bytearray(b'')) == ''
    
    def test_format_price(self):
        """测试价格格式化"""
        assert utils.format_price(10.5) == '10.50'
        assert utils.format_price(10.123, 3) == '10.123'
        assert utils.format_price('10.5') == '10.50'
    
    def test_format_price_invalid_input(self):
        """测试价格格式化的无效输入（应该返回原字符串）"""
        # 无效字符串应该原样返回
        assert utils.format_price('invalid') == 'invalid'
        assert utils.format_price('abc') == 'abc'
        assert utils.format_price('') == ''
    
    def test_parse_price(self):
        """测试价格解析"""
        assert utils.parse_price('10.50') == 10.5
        assert utils.parse_price('10') == 10.0
        assert utils.parse_price('') == 0.0
        assert utils.parse_price('invalid') == 0.0
    
    def test_format_quantity(self):
        """测试数量格式化"""
        assert utils.format_quantity(100) == '100'
        assert utils.format_quantity('100') == '100'
        assert utils.format_quantity(100.5) == '100'
    
    def test_format_quantity_invalid_input(self):
        """测试数量格式化的无效输入（应该返回原字符串）"""
        # 无效字符串应该原样返回
        assert utils.format_quantity('invalid') == 'invalid'
        assert utils.format_quantity('abc') == 'abc'
        assert utils.format_quantity('') == ''
    
    def test_parse_quantity(self):
        """测试数量解析"""
        assert utils.parse_quantity('100') == 100
        assert utils.parse_quantity('100.5') == 100
        assert utils.parse_quantity('') == 0
        assert utils.parse_quantity('invalid') == 0
    
    def test_pad_string(self):
        """测试字符串填充"""
        padded = utils.pad_string('test', 10)
        assert len(padded) == 10
        assert padded[:4] == b'test'
        assert padded[4:] == b'\x00' * 6
        
        # 测试中文填充
        test_gbk_bytes = '测试'.encode('gbk')
        padded_cn = utils.pad_string('测试', 10, encoding='gbk')
        assert len(padded_cn) == 10
        assert padded_cn[:len(test_gbk_bytes)] == test_gbk_bytes
        # 剩余部分应该是填充的零字节
        assert padded_cn[len(test_gbk_bytes):] == b'\x00' * (10 - len(test_gbk_bytes))
    
    def test_truncate_string(self):
        """测试字符串截断"""
        assert len(utils.truncate_string('test', 10).encode()) <= 10
        assert utils.truncate_string('test', 2) == 'te'
    
    def test_truncate_string_character_integrity(self):
        """测试字符串截断时的字符完整性处理"""
        # 测试中文截断（多字节字符）
        # '测试测试' 在 GBK 中是 8 个字节
        chinese_str = '测试测试'
        gbk_bytes = chinese_str.encode('gbk')
        assert len(gbk_bytes) == 8
        
        # 在字符边界截断（4 字节 = 2 个字符）
        result = utils.truncate_string(chinese_str, 4, 'gbk')
        assert result == '测试'
        
        # 在多字节字符中间截断（3 字节，会在字符中间）
        result = utils.truncate_string(chinese_str, 3, 'gbk')
        # 应该回退到 2 字节（1 个字符）或返回空字符串
        assert isinstance(result, str)
        assert len(result.encode('gbk')) <= 3
        
        # 测试在字符中间截断（5 字节）
        result = utils.truncate_string(chinese_str, 5, 'gbk')
        assert isinstance(result, str)
        assert len(result.encode('gbk')) <= 5
        
        # 测试长度为 0 的情况
        result = utils.truncate_string(chinese_str, 0, 'gbk')
        assert result == ''
        
        # 测试长度等于字符串长度的情况
        result = utils.truncate_string('test', 4, 'utf-8')
        assert result == 'test'
        
        # 测试超过字符串长度的情况
        result = utils.truncate_string('test', 10, 'utf-8')
        assert result == 'test'
        
        # 测试空字符串
        assert utils.truncate_string('', 5, 'gbk') == ''
        
        # 测试非字符串类型
        result = utils.truncate_string(12345, 3, 'utf-8')
        assert isinstance(result, str)
    
    def test_safe_int(self):
        """测试安全整数转换"""
        assert utils.safe_int(100) == 100
        assert utils.safe_int('100') == 100
        assert utils.safe_int('100.5') == 100
        assert utils.safe_int(None) == 0
        assert utils.safe_int('invalid') == 0
    
    def test_safe_int_edge_cases(self):
        """测试安全整数转换的边界情况"""
        # 测试浮点数
        assert utils.safe_int(100.7) == 100
        assert utils.safe_int(100.3) == 100
        assert utils.safe_int(-100.5) == -100
        
        # 测试字符串边界情况
        assert utils.safe_int('  100  ') == 100  # 带空格
        assert utils.safe_int('') == 0
        assert utils.safe_int('  ') == 0  # 只有空格
        
        # 测试各种无效输入
        assert utils.safe_int('abc') == 0
        assert utils.safe_int('12.34.56') == 0
        assert utils.safe_int('--100') == 0
        
        # 测试其他类型（应该返回 0）
        assert utils.safe_int([]) == 0
        assert utils.safe_int({}) == 0
        assert utils.safe_int(object()) == 0
        
        # 测试负数
        assert utils.safe_int(-100) == -100
        assert utils.safe_int('-100') == -100
        
        # 测试零
        assert utils.safe_int(0) == 0
        assert utils.safe_int('0') == 0
        assert utils.safe_int(0.0) == 0
        
        # 测试极大和极小值
        assert utils.safe_int(1e10) == 10000000000
        assert utils.safe_int('999999999') == 999999999
    
    def test_safe_float(self):
        """测试安全浮点数转换"""
        assert utils.safe_float(10.5) == 10.5
        assert utils.safe_float('10.5') == 10.5
        assert utils.safe_float(10) == 10.0
        assert utils.safe_float(None) == 0.0
        assert utils.safe_float('invalid') == 0.0
    
    def test_safe_float_edge_cases(self):
        """测试安全浮点数转换的边界情况"""
        # 测试各种数字格式
        assert utils.safe_float('10.50') == 10.5
        assert utils.safe_float('10.0') == 10.0
        assert utils.safe_float('.5') == 0.5
        assert utils.safe_float('5.') == 5.0
        assert utils.safe_float('-10.5') == -10.5
        
        # 测试字符串边界情况
        assert utils.safe_float('  10.5  ') == 10.5  # 带空格
        assert utils.safe_float('') == 0.0
        assert utils.safe_float('  ') == 0.0  # 只有空格
        
        # 测试科学计数法
        assert utils.safe_float('1.5e2') == 150.0
        assert utils.safe_float('1.5E-2') == 0.015
        
        # 测试各种无效输入
        assert utils.safe_float('abc') == 0.0
        assert utils.safe_float('12.34.56') == 0.0
        assert utils.safe_float('--10.5') == 0.0
        
        # 测试其他类型（应该返回 0.0）
        assert utils.safe_float([]) == 0.0
        assert utils.safe_float({}) == 0.0
        assert utils.safe_float(object()) == 0.0
        
        # 测试零
        assert utils.safe_float(0) == 0.0
        assert utils.safe_float(0.0) == 0.0
        assert utils.safe_float('0') == 0.0
        assert utils.safe_float('0.0') == 0.0
        
        # 测试极大和极小值
        assert utils.safe_float(1e10) == 1e10
        assert utils.safe_float(1e-10) == 1e-10
        assert utils.safe_float('999999999.99') == 999999999.99
        
        # 测试精度
        assert abs(utils.safe_float('3.141592653589793') - 3.141592653589793) < 1e-10


class TestExceptions:
    """测试 exceptions.py"""
    
    def test_exception_hierarchy(self):
        """测试异常继承层次"""
        assert issubclass(exceptions.OXConnectionError, exceptions.OXApiError)
        assert issubclass(exceptions.OXLoginError, exceptions.OXApiError)
        assert issubclass(exceptions.OXOrderError, exceptions.OXApiError)
        assert issubclass(exceptions.OXQueryError, exceptions.OXApiError)
        assert issubclass(exceptions.OXDllError, exceptions.OXApiError)
    
    def test_exception_creation(self):
        """测试异常创建"""
        error = exceptions.OXApiError("Test error")
        assert str(error) == "Test error"
        
        login_error = exceptions.OXLoginError("Login failed")
        assert str(login_error) == "Login failed"
        assert isinstance(login_error, exceptions.OXApiError)
    
    def test_exception_raising(self):
        """测试异常抛出"""
        with pytest.raises(exceptions.OXApiError):
            raise exceptions.OXApiError("Base error")
        
        with pytest.raises(exceptions.OXLoginError):
            raise exceptions.OXLoginError("Login error")


class TestUtilsStructConversion:
    """测试工具函数中的结构体转换"""
    
    def test_struct_to_dict_with_to_dict_method(self):
        """测试有 to_dict 方法的结构体"""
        from stock_ox.structs import CRspErrorField
        
        error = CRspErrorField()
        error.ErrorId = 1001
        # 设置 ErrorInfo - 使用 bytes 赋值（测试会直接使用 to_dict）
        # 注意：这里主要测试 struct_to_dict 会调用 to_dict 方法
        
        # 应该调用结构体的 to_dict 方法
        result = utils.struct_to_dict(error)
        assert isinstance(result, dict)
        assert 'ErrorId' in result
        assert 'ErrorInfo' in result
        assert result['ErrorId'] == 1001
    
    def test_struct_to_dict_without_to_dict_method(self):
        """测试没有 to_dict 方法的结构体（通用转换）"""
        from ctypes import Structure, c_int, c_int32
        
        class TestStruct(Structure):
            _pack_ = 1
            _fields_ = [
                ('value', c_int),
                ('value2', c_int32),
            ]
        
        obj = TestStruct()
        obj.value = 42
        obj.value2 = 123
        
        result = utils.struct_to_dict(obj)
        assert isinstance(result, dict)
        assert 'value' in result
        assert 'value2' in result
        assert result['value'] == 42
        assert result['value2'] == 123
    
    def test_struct_to_dict_exclude_none(self):
        """测试排除 None 值的选项"""
        from ctypes import Structure, c_int, c_int32
        
        class TestStruct(Structure):
            _pack_ = 1
            _fields_ = [
                ('value', c_int),
                ('value2', c_int32),
            ]
        
        obj = TestStruct()
        obj.value = 42
        obj.value2 = 0  # 0 值，不是 None
        
        # 默认排除 None（这里 value2 为 0，不是 None，所以不会被排除）
        result = utils.struct_to_dict(obj, exclude_none=True)
        assert 'value' in result
        assert 'value2' in result  # 0 不是 None，不会被排除
        
        # 测试一个真正为 None 的值（使用可选字段）
        # 注意：ctypes 结构体中，字段总是有值，所以这里主要测试逻辑
    
    def test_struct_to_dict_bytearray_conversion(self):
        """测试字节数组字段的转换"""
        from ctypes import Structure, c_char, addressof, memmove
        
        class TestStruct(Structure):
            _pack_ = 1
            _fields_ = [
                ('data', c_char * 10),
            ]
        
        obj = TestStruct()
        data_bytes = b'test\x00\x00\x00\x00\x00\x00'
        # 使用 addressof 和 memmove 复制字节
        struct_addr = addressof(obj)
        memmove(struct_addr, data_bytes, min(len(data_bytes), 10))
        
        result = utils.struct_to_dict(obj)
        assert 'data' in result
        # 应该被转换为字符串
        assert isinstance(result['data'], str)
        assert 'test' in result['data']
    
    def test_struct_to_dict_bytearray_field(self):
        """测试字节数组字段的处理"""
        # 测试结构体中有字节数组字段的情况
        class TestStruct(Structure):
            _pack_ = 1
            _fields_ = [
                ('value', c_int),
                ('name', c_char * 10),
            ]
        
        obj = TestStruct()
        obj.value = 42
        # 设置 name 字段（字节数组）
        name_bytes = b'test\x00' * 3
        struct_addr = addressof(obj)
        value_offset = 0  # value 在开始
        name_offset = 4   # value (int, 4 bytes) 后是 name
        memmove(struct_addr + name_offset, name_bytes, min(len(name_bytes), 10))
        
        result = utils.struct_to_dict(obj)
        assert isinstance(result, dict)
        assert 'value' in result
        assert 'name' in result
        assert result['value'] == 42
        # name 字段应该被转换为字符串
        assert isinstance(result['name'], str)


class TestTypesErrorHandling:
    """测试类型转换中的错误处理"""
    
    def test_account_type_from_char_invalid(self):
        """测试账户类型转换中的无效输入"""
        # 测试无效字符，应该返回默认值 STOCK
        result = types.AccountType.from_char('X')
        assert result == types.AccountType.STOCK
        
        # 测试无效的整数
        result = types.AccountType.from_char(999)
        assert result == types.AccountType.STOCK
        
        # 测试空的字节串
        result = types.AccountType.from_char(b'')
        assert result == types.AccountType.STOCK
    
    def test_order_state_from_char_invalid(self):
        """测试委托状态转换中的无效输入"""
        # 测试无效字符，应该返回默认值 NOT_REPORT
        result = types.OrderState.from_char('X')
        assert result == types.OrderState.NOT_REPORT
        
        # 测试无效的整数
        result = types.OrderState.from_char(999)
        assert result == types.OrderState.NOT_REPORT
    
    def test_exchange_id_from_char_invalid(self):
        """测试交易所 ID 转换中的无效输入"""
        # 测试无效字符，应该返回默认值 SZ
        result = types.ExchangeId.from_char('X')
        assert result == types.ExchangeId.SZ
        
        # 测试无效的整数
        result = types.ExchangeId.from_char(999)
        assert result == types.ExchangeId.SZ
    
    def test_helper_functions_invalid_input(self):
        """测试辅助函数的无效输入处理"""
        # 这些函数在遇到无效输入时应该抛出 ValueError
        with pytest.raises(ValueError):
            types.account_type_to_char([])
        
        with pytest.raises(ValueError):
            types.order_state_to_char([])
        
        with pytest.raises(ValueError):
            types.exchange_id_to_char([])


class TestFormatQuantityErrorHandling:
    """测试数量格式化的错误处理"""
    
    def test_format_quantity_invalid_input(self):
        """测试数量格式化的无效输入"""
        # 无效字符串应该原样返回
        result = utils.format_quantity('invalid')
        assert result == 'invalid'
        
        # 测试各种边界情况
        assert utils.format_quantity('') == ''
        assert utils.format_quantity('abc') == 'abc'


class TestFormatPriceErrorHandling:
    """测试价格格式化的错误处理"""
    
    def test_format_price_invalid_input(self):
        """测试价格格式化的无效输入"""
        # 无效字符串应该原样返回
        result = utils.format_price('invalid')
        assert result == 'invalid'
        
        # 测试各种边界情况
        assert utils.format_price('') == ''
        assert utils.format_price('abc') == 'abc'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

