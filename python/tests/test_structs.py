"""
结构体测试

测试结构体内存布局、创建和转换功能。
"""

import sys
import os
import struct
from ctypes import sizeof, addressof, c_int

import pytest

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_ox.structs import (
    CRspErrorField,
    COXReqLogonField,
    COXRspLogonField,
    COXReqTradeAcctField,
    COXRspTradeAcctField
)
from stock_ox.constants import (
    OX_ERRORINFO_LENGTH,
    OX_ACCOUNT_LENGTH,
    OX_PASSWORD_LENGTH,
    OX_RESERVED_LENGTH,
    OX_CUSTCODE_LENGTH,
    OX_BOARDID_LENGTH,
    OX_TRDACCT_LENGTH
)
from stock_ox.utils import encode_str


class TestCRspErrorField:
    """测试错误响应结构体"""
    
    def test_structure_size(self):
        """测试结构体大小"""
        # C++ 结构体大小：int(4) + char[128](128) = 132
        # 使用 pack(1) 时，大小为 132
        expected_size = 4 + OX_ERRORINFO_LENGTH  # 4 (int) + 128 (char array)
        assert sizeof(CRspErrorField) == expected_size
    
    def test_structure_creation(self):
        """测试结构体创建"""
        from ctypes import sizeof
        error = CRspErrorField()
        assert error.ErrorId == 0
        # 通过结构体总大小验证数组长度
        # CRspErrorField: int(4) + char[128](128) = 132
        expected_total_size = 4 + OX_ERRORINFO_LENGTH
        assert sizeof(error) == expected_total_size
    
    def test_structure_assignment(self):
        """测试结构体赋值"""
        error = CRspErrorField()
        error.ErrorId = 1001
        error.ErrorInfo = b'Test error message\x00'
        
        assert error.ErrorId == 1001
        assert error.ErrorInfo[:19] == b'Test error message'
    
    def test_to_dict(self):
        """测试转换为字典"""
        error = CRspErrorField()
        error.ErrorId = 1001
        error.ErrorInfo = encode_str('测试错误信息')
        
        result = error.to_dict()
        assert result['ErrorId'] == 1001
        assert '测试错误信息' in result['ErrorInfo']
    
    def test_structure_memory_layout(self):
        """测试内存布局"""
        error = CRspErrorField()
        error.ErrorId = 0x12345678
        error.ErrorInfo = b'Test\x00'
        
        # 验证 ErrorId 值
        assert error.ErrorId == 0x12345678
        # 这只是基本验证，实际内存布局取决于系统字节序


class TestCOXReqLogonField:
    """测试登录请求结构体"""
    
    def test_structure_size(self):
        """测试结构体大小"""
        # C++ 结构体大小（pack(1)）：
        # char(1) + char[24](24) + char[16](16) + char[256](256) = 297
        expected_size = 1 + OX_ACCOUNT_LENGTH + OX_PASSWORD_LENGTH + OX_RESERVED_LENGTH
        assert sizeof(COXReqLogonField) == expected_size
    
    def test_structure_creation(self):
        """测试结构体创建"""
        from ctypes import sizeof
        req = COXReqLogonField()
        # 检查结构体总大小
        expected_size = 1 + OX_ACCOUNT_LENGTH + OX_PASSWORD_LENGTH + OX_RESERVED_LENGTH
        assert sizeof(req) == expected_size
    
    def test_structure_assignment(self):
        """测试结构体赋值"""
        from ctypes import addressof, string_at, memmove
        req = COXReqLogonField()
        req.AcctType = ord('0')  # 现货账户
        account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        password_bytes = encode_str('111111')[:OX_PASSWORD_LENGTH].ljust(OX_PASSWORD_LENGTH, b'\x00')
        
        # 使用 addressof 和 memmove 安全地复制字节
        struct_addr = addressof(req)
        # Account 在结构体中的偏移：AcctType(1) = 1
        account_offset = 1
        account_addr = struct_addr + account_offset
        # Password 偏移：AcctType(1) + Account(24) = 25
        password_offset = 1 + OX_ACCOUNT_LENGTH
        password_addr = struct_addr + password_offset
        
        memmove(account_addr, account_bytes, OX_ACCOUNT_LENGTH)
        memmove(password_addr, password_bytes, OX_PASSWORD_LENGTH)
        
        # AcctType 是 c_char，值可能是字节或整数
        assert req.AcctType == ord('0') or req.AcctType == b'0' or (isinstance(req.AcctType, bytes) and req.AcctType[0] == ord('0'))
        account_data = string_at(account_addr, OX_ACCOUNT_LENGTH)
        assert account_data[:12] == encode_str('110060035050')
    
    def test_from_dict(self):
        """测试从字典创建"""
        from ctypes import addressof, string_at
        data = {
            'AcctType': '0',
            'Account': '110060035050',
            'Password': '111111'
        }
        req = COXReqLogonField.from_dict(data)
        
        # AcctType 是 c_char，可能是整数或字节
        assert req.AcctType == ord('0') or req.AcctType == b'0'
        struct_addr = addressof(req)
        account_addr = struct_addr + 1  # AcctType(1)
        password_addr = struct_addr + 1 + OX_ACCOUNT_LENGTH  # AcctType(1) + Account(24)
        account_data = string_at(account_addr, OX_ACCOUNT_LENGTH)
        password_data = string_at(password_addr, OX_PASSWORD_LENGTH)
        assert account_data[:12] == encode_str('110060035050')
        assert password_data[:6] == encode_str('111111')
    
    def test_to_dict(self):
        """测试转换为字典"""
        from ctypes import addressof, memmove, string_at
        req = COXReqLogonField()
        req.AcctType = ord('0')
        account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        password_bytes = encode_str('111111')[:OX_PASSWORD_LENGTH].ljust(OX_PASSWORD_LENGTH, b'\x00')
        
        struct_addr = addressof(req)
        account_addr = struct_addr + 1  # AcctType(1)
        password_addr = struct_addr + 1 + OX_ACCOUNT_LENGTH  # AcctType(1) + Account(24)
        memmove(account_addr, account_bytes, OX_ACCOUNT_LENGTH)
        memmove(password_addr, password_bytes, OX_PASSWORD_LENGTH)
        
        result = req.to_dict()
        assert result['AcctType'] == '0' or ord(result['AcctType']) == ord('0')
        assert '110060035050' in result['Account']
        assert '111111' in result['Password']


class TestCOXRspLogonField:
    """测试登录响应结构体"""
    
    def test_structure_size(self):
        """测试结构体大小"""
        # C++ 结构体大小（pack(1)）：
        # int(4) + char[24](24) + char(1) + char[24](24) = 53
        expected_size = 4 + OX_CUSTCODE_LENGTH + 1 + OX_ACCOUNT_LENGTH
        assert sizeof(COXRspLogonField) == expected_size
    
    def test_structure_creation(self):
        """测试结构体创建"""
        from ctypes import sizeof
        resp = COXRspLogonField()
        assert resp.IntOrg == 0
        # 检查结构体总大小
        expected_size = 4 + OX_CUSTCODE_LENGTH + 1 + OX_ACCOUNT_LENGTH
        assert sizeof(resp) == expected_size
    
    def test_structure_assignment(self):
        """测试结构体赋值"""
        from ctypes import addressof, memmove, string_at
        resp = COXRspLogonField()
        resp.IntOrg = 12345
        cust_code_bytes = encode_str('CUST001')[:OX_CUSTCODE_LENGTH].ljust(OX_CUSTCODE_LENGTH, b'\x00')
        account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        resp.AcctType = ord('0')
        
        struct_addr = addressof(resp)
        cust_code_offset = 4  # IntOrg(4)
        account_offset = 4 + OX_CUSTCODE_LENGTH + 1  # IntOrg(4) + CustCode(24) + AcctType(1)
        
        memmove(struct_addr + cust_code_offset, cust_code_bytes, OX_CUSTCODE_LENGTH)
        memmove(struct_addr + account_offset, account_bytes, OX_ACCOUNT_LENGTH)
        
        assert resp.IntOrg == 12345
        cust_code_data = string_at(struct_addr + cust_code_offset, OX_CUSTCODE_LENGTH)
        assert cust_code_data[:7] == encode_str('CUST001')
        assert resp.AcctType == ord('0') or resp.AcctType == b'0'
    
    def test_to_dict(self):
        """测试转换为字典"""
        from ctypes import addressof, memmove
        resp = COXRspLogonField()
        resp.IntOrg = 12345
        cust_code_bytes = encode_str('CUST001')[:OX_CUSTCODE_LENGTH].ljust(OX_CUSTCODE_LENGTH, b'\x00')
        account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        resp.AcctType = ord('0')
        
        struct_addr = addressof(resp)
        cust_code_offset = 4  # IntOrg(4)
        account_offset = 4 + OX_CUSTCODE_LENGTH + 1  # IntOrg(4) + CustCode(24) + AcctType(1)
        
        memmove(struct_addr + cust_code_offset, cust_code_bytes, OX_CUSTCODE_LENGTH)
        memmove(struct_addr + account_offset, account_bytes, OX_ACCOUNT_LENGTH)
        
        result = resp.to_dict()
        assert result['IntOrg'] == 12345
        assert 'CUST001' in result['CustCode']
        assert result['AcctType'] == '0' or ord(result['AcctType']) == ord('0')
        assert '110060035050' in result['Account']


class TestCOXReqTradeAcctField:
    """测试交易账号请求结构体"""
    
    def test_structure_size(self):
        """测试结构体大小"""
        # C++ 结构体大小（pack(1)）：
        # char(1) + char[24](24) = 25
        expected_size = 1 + OX_ACCOUNT_LENGTH
        assert sizeof(COXReqTradeAcctField) == expected_size
    
    def test_structure_creation(self):
        """测试结构体创建"""
        from ctypes import sizeof
        req = COXReqTradeAcctField()
        # 检查结构体总大小
        expected_size = 1 + OX_ACCOUNT_LENGTH
        assert sizeof(req) == expected_size
    
    def test_from_dict(self):
        """测试从字典创建"""
        from ctypes import addressof, string_at
        data = {
            'AcctType': '0',
            'Account': '110060035050'
        }
        req = COXReqTradeAcctField.from_dict(data)
        
        assert req.AcctType == ord('0') or req.AcctType == b'0'
        struct_addr = addressof(req)
        account_addr = struct_addr + 1  # AcctType(1)
        account_data = string_at(account_addr, OX_ACCOUNT_LENGTH)
        assert account_data[:12] == encode_str('110060035050')
    
    def test_to_dict(self):
        """测试转换为字典"""
        from ctypes import addressof, memmove
        req = COXReqTradeAcctField()
        req.AcctType = ord('0')
        account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        
        struct_addr = addressof(req)
        account_addr = struct_addr + 1  # AcctType(1)
        memmove(account_addr, account_bytes, OX_ACCOUNT_LENGTH)
        
        result = req.to_dict()
        assert result['AcctType'] == '0' or ord(result['AcctType']) == ord('0')
        assert '110060035050' in result['Account']


class TestCOXRspTradeAcctField:
    """测试交易账号响应结构体"""
    
    def test_structure_size(self):
        """测试结构体大小"""
        # C++ 结构体大小（pack(1)）：
        # char[24](24) + char[24](24) + char(1) + char[4](4) + char(1) + char[24](24) + char(1) = 79
        expected_size = (
            OX_CUSTCODE_LENGTH +
            OX_ACCOUNT_LENGTH +
            1 +  # ExchangeId
            OX_BOARDID_LENGTH +
            1 +  # TrdAcctStatus
            OX_TRDACCT_LENGTH +
            1    # TrdAcctType
        )
        assert sizeof(COXRspTradeAcctField) == expected_size
    
    def test_structure_creation(self):
        """测试结构体创建"""
        from ctypes import sizeof
        resp = COXRspTradeAcctField()
        # 检查结构体总大小
        expected_size = (
            OX_CUSTCODE_LENGTH +
            OX_ACCOUNT_LENGTH +
            1 +  # ExchangeId
            OX_BOARDID_LENGTH +
            1 +  # TrdAcctStatus
            OX_TRDACCT_LENGTH +
            1    # TrdAcctType
        )
        assert sizeof(resp) == expected_size
    
    def test_to_dict(self):
        """测试转换为字典"""
        from ctypes import addressof, memmove
        resp = COXRspTradeAcctField()
        
        # 设置字符串字段
        cust_code_bytes = encode_str('CUST001')[:OX_CUSTCODE_LENGTH].ljust(OX_CUSTCODE_LENGTH, b'\x00')
        account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        board_id_bytes = encode_str('10')[:OX_BOARDID_LENGTH].ljust(OX_BOARDID_LENGTH, b'\x00')
        trd_acct_bytes = encode_str('A197407210')[:OX_TRDACCT_LENGTH].ljust(OX_TRDACCT_LENGTH, b'\x00')
        
        struct_addr = addressof(resp)
        cust_code_offset = 0  # 第一个字段
        account_offset = OX_CUSTCODE_LENGTH  # CustCode(24)
        board_id_offset = OX_CUSTCODE_LENGTH + OX_ACCOUNT_LENGTH + 1  # CustCode(24) + Account(24) + ExchangeId(1)
        trd_acct_offset = OX_CUSTCODE_LENGTH + OX_ACCOUNT_LENGTH + 1 + OX_BOARDID_LENGTH + 1  # 前面字段 + BoardId(4) + TrdAcctStatus(1)
        
        memmove(struct_addr + cust_code_offset, cust_code_bytes, OX_CUSTCODE_LENGTH)
        memmove(struct_addr + account_offset, account_bytes, OX_ACCOUNT_LENGTH)
        memmove(struct_addr + board_id_offset, board_id_bytes, OX_BOARDID_LENGTH)
        memmove(struct_addr + trd_acct_offset, trd_acct_bytes, OX_TRDACCT_LENGTH)
        
        resp.ExchangeId = ord('1')  # 上海
        resp.TrdAcctStatus = ord('0')
        resp.TrdAcctType = ord('0')
        
        result = resp.to_dict()
        assert 'CUST001' in result['CustCode']
        assert '110060035050' in result['Account']
        assert result['ExchangeId'] == '1' or ord(result['ExchangeId']) == ord('1')
        assert '10' in result['BoardId']


class TestStructMemoryLayout:
    """测试结构体内存布局"""
    
    def test_error_field_layout(self):
        """测试错误响应结构体内存布局"""
        error = CRspErrorField()
        error.ErrorId = 0x12345678
        error.ErrorInfo = b'Test\x00'
        
        # 验证结构体大小
        assert sizeof(CRspErrorField) == 4 + OX_ERRORINFO_LENGTH
    
    def test_logon_req_layout(self):
        """测试登录请求结构体内存布局"""
        req = COXReqLogonField()
        
        # 验证结构体大小
        expected_size = 1 + OX_ACCOUNT_LENGTH + OX_PASSWORD_LENGTH + OX_RESERVED_LENGTH
        assert sizeof(COXReqLogonField) == expected_size
    
    def test_logon_rsp_layout(self):
        """测试登录响应结构体内存布局"""
        resp = COXRspLogonField()
        
        # 验证结构体大小
        expected_size = 4 + OX_CUSTCODE_LENGTH + 1 + OX_ACCOUNT_LENGTH
        assert sizeof(COXRspLogonField) == expected_size
    
    def test_pack_alignment(self):
        """测试 pack(1) 内存对齐"""
        # 所有结构体都应该使用 _pack_ = 1（1 字节对齐）
        # 验证没有额外填充
        
        # CRspErrorField: int(4) + char[128](128) = 132 (无填充)
        assert sizeof(CRspErrorField) == 4 + OX_ERRORINFO_LENGTH
        
        # COXReqLogonField: char(1) + char[24](24) + char[16](16) + char[256](256) = 297 (无填充)
        assert sizeof(COXReqLogonField) == 1 + OX_ACCOUNT_LENGTH + OX_PASSWORD_LENGTH + OX_RESERVED_LENGTH
        
        # COXRspLogonField: int(4) + char[24](24) + char(1) + char[24](24) = 53 (无填充)
        assert sizeof(COXRspLogonField) == 4 + OX_CUSTCODE_LENGTH + 1 + OX_ACCOUNT_LENGTH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

