"""
数据结构定义模块

使用 ctypes.Structure 定义所有 C++ 结构体。
"""

from ctypes import Structure, c_char, c_int, c_int32, c_int64, c_uint32, c_uint64, byref
from .constants import *


class CRspErrorField(Structure):
    """错误响应结构体
    
    对应 C++ 结构体：
    struct CRspErrorField {
        int  ErrorId;
        char ErrorInfo[OX_ERRORINFO_LENGTH];
    };
    """
    _pack_ = 1
    _fields_ = [
        ('ErrorId', c_int),
        ('ErrorInfo', c_char * OX_ERRORINFO_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'ErrorId': self.ErrorId,
            'ErrorInfo': decode_str(bytes(self.ErrorInfo))
        }


class COXReqLogonField(Structure):
    """登录请求结构体
    
    对应 C++ 结构体：
    struct COXReqLogonField {
        OXAccountType  AcctType;       // 账户类型(必需)
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号(必需)
        char Password[OX_PASSWORD_LENGTH];  // 交易密码(必需)
        char Reserved[OX_RESERVED_LENGTH];  // 保留字段
    };
    """
    _pack_ = 1
    _fields_ = [
        ('AcctType', c_char),           # OXAccountType (char)
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('Password', c_char * OX_PASSWORD_LENGTH),
        ('Reserved', c_char * OX_RESERVED_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account)),
            'Password': decode_str(bytes(self.Password)),
            'Reserved': decode_str(bytes(self.Reserved))
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建结构体"""
        from ctypes import addressof, memmove
        from .utils import encode_str
        obj = cls()
        acct_type = data.get('AcctType', '0')
        obj.AcctType = acct_type[0] if isinstance(acct_type, bytes) else ord(acct_type)
        
        struct_addr = addressof(obj)
        account_offset = 1  # AcctType(1)
        password_offset = 1 + OX_ACCOUNT_LENGTH  # AcctType(1) + Account(24)
        reserved_offset = 1 + OX_ACCOUNT_LENGTH + OX_PASSWORD_LENGTH  # AcctType(1) + Account(24) + Password(16)
        
        account_str = data.get('Account', '')
        account_bytes = encode_str(account_str)[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        memmove(struct_addr + account_offset, account_bytes, OX_ACCOUNT_LENGTH)
        
        password_str = data.get('Password', '')
        password_bytes = encode_str(password_str)[:OX_PASSWORD_LENGTH].ljust(OX_PASSWORD_LENGTH, b'\x00')
        memmove(struct_addr + password_offset, password_bytes, OX_PASSWORD_LENGTH)
        
        reserved_bytes = b'\x00' * OX_RESERVED_LENGTH
        memmove(struct_addr + reserved_offset, reserved_bytes, OX_RESERVED_LENGTH)
        
        return obj


class COXRspLogonField(Structure):
    """登录响应结构体
    
    对应 C++ 结构体：
    struct COXRspLogonField {
        int  IntOrg;                    // 内部组织
        char CustCode[OX_CUSTCODE_LENGTH];   // 客户代码
        OXAccountType  AcctType;        // 账户类型(必需)
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号(必需)
    };
    """
    _pack_ = 1
    _fields_ = [
        ('IntOrg', c_int),
        ('CustCode', c_char * OX_CUSTCODE_LENGTH),
        ('AcctType', c_char),           # OXAccountType (char)
        ('Account', c_char * OX_ACCOUNT_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'IntOrg': self.IntOrg,
            'CustCode': decode_str(bytes(self.CustCode)),
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account))
        }


class COXReqTradeAcctField(Structure):
    """交易账号请求结构体
    
    对应 C++ 结构体：
    struct COXReqTradeAcctField {
        OXAccountType  AcctType;       // 账户类型(必需)
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号(必需)
    };
    """
    _pack_ = 1
    _fields_ = [
        ('AcctType', c_char),           # OXAccountType (char)
        ('Account', c_char * OX_ACCOUNT_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account))
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建结构体"""
        from ctypes import addressof, memmove
        from .utils import encode_str
        obj = cls()
        acct_type = data.get('AcctType', '0')
        obj.AcctType = acct_type[0] if isinstance(acct_type, bytes) else ord(acct_type)
        
        struct_addr = addressof(obj)
        account_offset = 1  # AcctType(1)
        
        account_str = data.get('Account', '')
        account_bytes = encode_str(account_str)[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        memmove(struct_addr + account_offset, account_bytes, OX_ACCOUNT_LENGTH)
        
        return obj


class COXRspTradeAcctField(Structure):
    """交易账号响应结构体
    
    对应 C++ 结构体：
    struct COXRspTradeAcctField {
        char CustCode[OX_CUSTCODE_LENGTH];     // 客户代码
        char Account[OX_ACCOUNT_LENGTH];       // 资金账号
        char ExchangeId;                       // 交易所
        char BoardId[OX_BOARDID_LENGTH];       // 交易板块
        char TrdAcctStatus;                    // 账号状态
        char TrdAcct[OX_TRDACCT_LENGTH];       // 证券账号
        char TrdAcctType;                      // 交易账号类型
    };
    """
    _pack_ = 1
    _fields_ = [
        ('CustCode', c_char * OX_CUSTCODE_LENGTH),
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('ExchangeId', c_char),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('TrdAcctStatus', c_char),
        ('TrdAcct', c_char * OX_TRDACCT_LENGTH),
        ('TrdAcctType', c_char),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'CustCode': decode_str(bytes(self.CustCode)),
            'Account': decode_str(bytes(self.Account)),
            'ExchangeId': chr(self.ExchangeId) if isinstance(self.ExchangeId, int) else self.ExchangeId.decode('utf-8') if isinstance(self.ExchangeId, bytes) else self.ExchangeId,
            'BoardId': decode_str(bytes(self.BoardId)),
            'TrdAcctStatus': chr(self.TrdAcctStatus) if isinstance(self.TrdAcctStatus, int) else self.TrdAcctStatus.decode('utf-8') if isinstance(self.TrdAcctStatus, bytes) else self.TrdAcctStatus,
            'TrdAcct': decode_str(bytes(self.TrdAcct)),
            'TrdAcctType': chr(self.TrdAcctType) if isinstance(self.TrdAcctType, int) else self.TrdAcctType.decode('utf-8') if isinstance(self.TrdAcctType, bytes) else self.TrdAcctType,
        }
