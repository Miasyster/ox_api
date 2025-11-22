"""
数据结构定义模块

使用 ctypes.Structure 定义所有 C++ 结构体。
"""

from ctypes import Structure, c_char, c_int, c_int32, c_int64, c_uint32, c_uint64, c_uint16, byref, sizeof
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


class COXReqOrderTicketField(Structure):
    """下单请求结构体
    
    对应 C++ 结构体：
    struct COXReqOrderTicketField {
        OXAccountType  AcctType;       // 账户类型(必需)
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号(必需)
        char Trdacct[OX_TRDACCT_LENGTH];    // 股东账号
        char BoardId[OX_BOARDID_LENGTH];    // 交易板块
        int  StkBiz;                        // 证券业务
        int  StkBizAction;                  // 证券业务指令
        char Symbol[OX_SYMBOL_LENGTH];      // 证券代码
        uint32_t OrderQty;                  // 委托数量
        char OrderPrice[OX_ORDERPRICE_LENGTH]; // 委托价格
        char OrderRef[OX_ORDER_REF_LENGTH]; // 客户委托信息
        char TrdCodeCls;                    // 交易代码分类
        char TrdExInfo[OX_TRD_EXT_INFO_LENGTH]; // 委托扩展信息
    };
    """
    _pack_ = 1
    _fields_ = [
        ('AcctType', c_char),           # OXAccountType (char)
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('Trdacct', c_char * OX_TRDACCT_LENGTH),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('StkBiz', c_int),
        ('StkBizAction', c_int),
        ('Symbol', c_char * OX_SYMBOL_LENGTH),
        ('OrderQty', c_uint32),
        ('OrderPrice', c_char * OX_ORDERPRICE_LENGTH),
        ('OrderRef', c_char * OX_ORDER_REF_LENGTH),
        ('TrdCodeCls', c_char),
        ('TrdExInfo', c_char * OX_TRD_EXT_INFO_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account)),
            'Trdacct': decode_str(bytes(self.Trdacct)),
            'BoardId': decode_str(bytes(self.BoardId)),
            'StkBiz': self.StkBiz,
            'StkBizAction': self.StkBizAction,
            'Symbol': decode_str(bytes(self.Symbol)),
            'OrderQty': self.OrderQty,
            'OrderPrice': decode_str(bytes(self.OrderPrice)),
            'OrderRef': decode_str(bytes(self.OrderRef)),
            'TrdCodeCls': chr(self.TrdCodeCls) if isinstance(self.TrdCodeCls, int) else self.TrdCodeCls.decode('utf-8') if isinstance(self.TrdCodeCls, bytes) else self.TrdCodeCls,
            'TrdExInfo': decode_str(bytes(self.TrdExInfo)),
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建结构体"""
        from ctypes import addressof, memmove
        from .utils import encode_str, format_price
        obj = cls()
        acct_type = data.get('AcctType', '0')
        obj.AcctType = acct_type[0] if isinstance(acct_type, bytes) else ord(acct_type)
        
        struct_addr = addressof(obj)
        offset = 1  # AcctType(1)
        
        # Account
        account_str = data.get('Account', '')
        account_bytes = encode_str(account_str)[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        memmove(struct_addr + offset, account_bytes, OX_ACCOUNT_LENGTH)
        offset += OX_ACCOUNT_LENGTH
        
        # Trdacct
        trdacct_str = data.get('Trdacct', '')
        trdacct_bytes = encode_str(trdacct_str)[:OX_TRDACCT_LENGTH].ljust(OX_TRDACCT_LENGTH, b'\x00')
        memmove(struct_addr + offset, trdacct_bytes, OX_TRDACCT_LENGTH)
        offset += OX_TRDACCT_LENGTH
        
        # BoardId
        boardid_str = data.get('BoardId', '')
        boardid_bytes = encode_str(boardid_str)[:OX_BOARDID_LENGTH].ljust(OX_BOARDID_LENGTH, b'\x00')
        memmove(struct_addr + offset, boardid_bytes, OX_BOARDID_LENGTH)
        offset += OX_BOARDID_LENGTH
        
        # StkBiz, StkBizAction
        obj.StkBiz = data.get('StkBiz', 100)
        obj.StkBizAction = data.get('StkBizAction', 100)
        offset += 8  # StkBiz(4) + StkBizAction(4)
        
        # Symbol
        symbol_str = data.get('Symbol', '')
        symbol_bytes = encode_str(symbol_str)[:OX_SYMBOL_LENGTH].ljust(OX_SYMBOL_LENGTH, b'\x00')
        memmove(struct_addr + offset, symbol_bytes, OX_SYMBOL_LENGTH)
        offset += OX_SYMBOL_LENGTH
        
        # OrderQty
        obj.OrderQty = data.get('OrderQty', 0)
        offset += 4  # OrderQty(4)
        
        # OrderPrice
        order_price = data.get('OrderPrice', '0')
        if isinstance(order_price, (int, float)):
            order_price = format_price(order_price)
        price_bytes = encode_str(order_price)[:OX_ORDERPRICE_LENGTH].ljust(OX_ORDERPRICE_LENGTH, b'\x00')
        memmove(struct_addr + offset, price_bytes, OX_ORDERPRICE_LENGTH)
        offset += OX_ORDERPRICE_LENGTH
        
        # OrderRef
        order_ref = data.get('OrderRef', '')
        order_ref_bytes = encode_str(order_ref)[:OX_ORDER_REF_LENGTH].ljust(OX_ORDER_REF_LENGTH, b'\x00')
        memmove(struct_addr + offset, order_ref_bytes, OX_ORDER_REF_LENGTH)
        offset += OX_ORDER_REF_LENGTH
        
        # TrdCodeCls
        trd_code_cls = data.get('TrdCodeCls', '\x00')
        if isinstance(trd_code_cls, bytes):
            obj.TrdCodeCls = trd_code_cls[0] if len(trd_code_cls) > 0 else 0
        elif isinstance(trd_code_cls, str):
            obj.TrdCodeCls = ord(trd_code_cls[0]) if len(trd_code_cls) > 0 else 0
        else:
            obj.TrdCodeCls = trd_code_cls if trd_code_cls is not None else 0
        offset += 1
        
        # TrdExInfo
        trd_ex_info = data.get('TrdExInfo', '')
        trd_ex_info_bytes = encode_str(trd_ex_info)[:OX_TRD_EXT_INFO_LENGTH].ljust(OX_TRD_EXT_INFO_LENGTH, b'\x00')
        memmove(struct_addr + offset, trd_ex_info_bytes, OX_TRD_EXT_INFO_LENGTH)
        
        return obj


class COXOrderTicket(Structure):
    """委托回报结构体
    
    对应 C++ 结构体：
    struct COXOrderTicket {
        OXAccountType  AcctType;       // 账户类型
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号
        char Trdacct[OX_TRDACCT_LENGTH];    // 股东账号
        char BoardId[OX_BOARDID_LENGTH];    // 交易板块
        int  StkBiz;                        // 证券业务
        int  StkBizAction;                  // 证券业务指令
        char Symbol[OX_SYMBOL_LENGTH];      // 证券代码
        char OrderRef[OX_ORDER_REF_LENGTH]; // 客户委托信息
        uint32_t OrderQty;                  // 委托数量
        char OrderPrice[OX_ORDERPRICE_LENGTH]; // 委托价格
        int32_t InsertDate;                 // 委托日期
        char InsertTime[OX_ORDERTIME_LENGTH]; // 委托时间
        int64_t OrderNo;                    // 委托编号
        char OrderState;                    // 委托状态
        int32_t ErrorId;                    // 错误ID
        char ExeInfo[OX_EXEINFO_LENGTH];    // 执行信息
        int64_t FilledQty;                  // 成交数量
        int64_t CanceledQty;                // 撤单数量
        char FilledAmt[OX_FILLEDAMT_LENGTH]; // 成交金额
    };
    """
    _pack_ = 1
    _fields_ = [
        ('AcctType', c_char),
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('Trdacct', c_char * OX_TRDACCT_LENGTH),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('StkBiz', c_int),
        ('StkBizAction', c_int),
        ('Symbol', c_char * OX_SYMBOL_LENGTH),
        ('OrderRef', c_char * OX_ORDER_REF_LENGTH),
        ('OrderQty', c_uint32),
        ('OrderPrice', c_char * OX_ORDERPRICE_LENGTH),
        ('InsertDate', c_int32),
        ('InsertTime', c_char * OX_ORDERTIME_LENGTH),
        ('OrderNo', c_int64),
        ('OrderState', c_char),
        ('ErrorId', c_int32),
        ('ExeInfo', c_char * OX_EXEINFO_LENGTH),
        ('FilledQty', c_int64),
        ('CanceledQty', c_int64),
        ('FilledAmt', c_char * OX_FILLEDAMT_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account)),
            'Trdacct': decode_str(bytes(self.Trdacct)),
            'BoardId': decode_str(bytes(self.BoardId)),
            'StkBiz': self.StkBiz,
            'StkBizAction': self.StkBizAction,
            'Symbol': decode_str(bytes(self.Symbol)),
            'OrderRef': decode_str(bytes(self.OrderRef)),
            'OrderQty': self.OrderQty,
            'OrderPrice': decode_str(bytes(self.OrderPrice)),
            'InsertDate': self.InsertDate,
            'InsertTime': decode_str(bytes(self.InsertTime)),
            'OrderNo': self.OrderNo,
            'OrderState': chr(self.OrderState) if isinstance(self.OrderState, int) else self.OrderState.decode('utf-8') if isinstance(self.OrderState, bytes) else self.OrderState,
            'ErrorId': self.ErrorId,
            'ExeInfo': decode_str(bytes(self.ExeInfo)),
            'FilledQty': self.FilledQty,
            'CanceledQty': self.CanceledQty,
            'FilledAmt': decode_str(bytes(self.FilledAmt)),
        }


class COXOrderFilledField(Structure):
    """成交回报结构体
    
    对应 C++ 结构体：
    struct COXOrderFilledField {
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号
        char Trdacct[OX_TRDACCT_LENGTH];    // 股东账号
        char Symbol[OX_SYMBOL_LENGTH];      // 证券代码
        char ExchangeId;                    // 交易所
        char BoardId[OX_BOARDID_LENGTH];    // 交易板块
        int  StkBiz;                        // 证券业务
        int  StkBizAction;                  // 证券业务指令
        char TradeSn[OX_TRADESN_LENGTH];    // 成交序号
        int64_t OrderNo;                    // 委托编号
        char OrderRef[OX_ORDER_REF_LENGTH]; // 客户委托信息
        int64_t FilledQty;                  // 成交数量
        char FilledPrice[OX_FILLEDPRICE_LENGTH]; // 成交价格
        char FilledAmt[OX_FILLEDAMT_LENGTH]; // 成交金额
        int32_t FilledDate;                 // 成交日期
        char FilledTime[OX_FILLEDTIME_LENGTH]; // 成交时间
        int32_t ErrorId;                    // 错误ID
        char RetMessage[OX_RETMESSAGE_LENGTH]; // 返回消息
    };
    """
    _pack_ = 1
    _fields_ = [
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('Trdacct', c_char * OX_TRDACCT_LENGTH),
        ('Symbol', c_char * OX_SYMBOL_LENGTH),
        ('ExchangeId', c_char),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('StkBiz', c_int),
        ('StkBizAction', c_int),
        ('TradeSn', c_char * OX_TRADESN_LENGTH),
        ('OrderNo', c_int64),
        ('OrderRef', c_char * OX_ORDER_REF_LENGTH),
        ('FilledQty', c_int64),
        ('FilledPrice', c_char * OX_FILLEDPRICE_LENGTH),
        ('FilledAmt', c_char * OX_FILLEDAMT_LENGTH),
        ('FilledDate', c_int32),
        ('FilledTime', c_char * OX_FILLEDTIME_LENGTH),
        ('ErrorId', c_int32),
        ('RetMessage', c_char * OX_RETMESSAGE_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'Account': decode_str(bytes(self.Account)),
            'Trdacct': decode_str(bytes(self.Trdacct)),
            'Symbol': decode_str(bytes(self.Symbol)),
            'ExchangeId': chr(self.ExchangeId) if isinstance(self.ExchangeId, int) else self.ExchangeId.decode('utf-8') if isinstance(self.ExchangeId, bytes) else self.ExchangeId,
            'BoardId': decode_str(bytes(self.BoardId)),
            'StkBiz': self.StkBiz,
            'StkBizAction': self.StkBizAction,
            'TradeSn': decode_str(bytes(self.TradeSn)),
            'OrderNo': self.OrderNo,
            'OrderRef': decode_str(bytes(self.OrderRef)),
            'FilledQty': self.FilledQty,
            'FilledPrice': decode_str(bytes(self.FilledPrice)),
            'FilledAmt': decode_str(bytes(self.FilledAmt)),
            'FilledDate': self.FilledDate,
            'FilledTime': decode_str(bytes(self.FilledTime)),
            'ErrorId': self.ErrorId,
            'RetMessage': decode_str(bytes(self.RetMessage)),
        }


class COXReqCancelTicketField(Structure):
    """撤单请求结构体
    
    对应 C++ 结构体：
    struct COXReqCancelTicketField {
        OXAccountType  AcctType;       // 账户类型(必需)
        char Account[OX_ACCOUNT_LENGTH];    // 资金账号(必需)
        char BoardId[OX_BOARDID_LENGTH];    // 交易板块
        uint32_t  OrderDate;                // 委托日期
        int64_t   OrderNo;                  // 委托号
    };
    """
    _pack_ = 1
    _fields_ = [
        ('AcctType', c_char),           # OXAccountType (char)
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('OrderDate', c_uint32),
        ('OrderNo', c_int64),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account)),
            'BoardId': decode_str(bytes(self.BoardId)),
            'OrderDate': self.OrderDate,
            'OrderNo': self.OrderNo,
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
        offset = 1  # AcctType(1)
        
        # Account
        account_str = data.get('Account', '')
        account_bytes = encode_str(account_str)[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        memmove(struct_addr + offset, account_bytes, OX_ACCOUNT_LENGTH)
        offset += OX_ACCOUNT_LENGTH
        
        # BoardId
        boardid_str = data.get('BoardId', '')
        boardid_bytes = encode_str(boardid_str)[:OX_BOARDID_LENGTH].ljust(OX_BOARDID_LENGTH, b'\x00')
        memmove(struct_addr + offset, boardid_bytes, OX_BOARDID_LENGTH)
        offset += OX_BOARDID_LENGTH
        
        # OrderDate, OrderNo
        obj.OrderDate = data.get('OrderDate', 0)
        obj.OrderNo = data.get('OrderNo', 0)
        
        return obj


class COXRspCancelTicketField(Structure):
    """撤单响应结构体
    
    对应 C++ 结构体：
    struct COXRspCancelTicketField {
        char Account[OX_ACCOUNT_LENGTH];    // 资产账号
        char BoardId[OX_BOARDID_LENGTH];    // 交易板块
        uint32_t OrderDate;                 // 委托日期
        int64_t  OrderNo;                   // 委托号
        char OrderState;                    // 委托状态
        char ExeInfo[OX_EXEINFO_LENGTH];    // 执行信息
        int  StkBiz;                        // 证券业务
        int  StkBizAction;                  // 证券业务指令
        char Symbol[OX_SYMBOL_LENGTH];      // 证券代码
    };
    """
    _pack_ = 1
    _fields_ = [
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('OrderDate', c_uint32),
        ('OrderNo', c_int64),
        ('OrderState', c_char),
        ('ExeInfo', c_char * OX_EXEINFO_LENGTH),
        ('StkBiz', c_int),
        ('StkBizAction', c_int),
        ('Symbol', c_char * OX_SYMBOL_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'Account': decode_str(bytes(self.Account)),
            'BoardId': decode_str(bytes(self.BoardId)),
            'OrderDate': self.OrderDate,
            'OrderNo': self.OrderNo,
            'OrderState': chr(self.OrderState) if isinstance(self.OrderState, int) else self.OrderState.decode('utf-8') if isinstance(self.OrderState, bytes) else self.OrderState,
            'ExeInfo': decode_str(bytes(self.ExeInfo)),
            'StkBiz': self.StkBiz,
            'StkBizAction': self.StkBizAction,
            'Symbol': decode_str(bytes(self.Symbol)),
        }


class COXOrderItem(Structure):
    """订单项结构体
    
    对应 C++ 结构体：
    struct COXOrderItem {
        char Trdacct[OX_TRDACCT_LENGTH];       // 股东账号
        char BoardId[OX_BOARDID_LENGTH];       // 交易板块
        int  StkBiz;                           // 证券业务
        int  StkBizAction;                     // 证券业务指令
        char Symbol[OX_SYMBOL_LENGTH];         // 证券代码
        uint32_t OrderQty;                     // 委托数量
        char OrderPrice[OX_ORDERPRICE_LENGTH]; // 委托价格
        char OrderRef[OX_ORDER_REF_LENGTH];    // 客户委托信息
    };
    """
    _pack_ = 1
    _fields_ = [
        ('Trdacct', c_char * OX_TRDACCT_LENGTH),
        ('BoardId', c_char * OX_BOARDID_LENGTH),
        ('StkBiz', c_int),
        ('StkBizAction', c_int),
        ('Symbol', c_char * OX_SYMBOL_LENGTH),
        ('OrderQty', c_uint32),
        ('OrderPrice', c_char * OX_ORDERPRICE_LENGTH),
        ('OrderRef', c_char * OX_ORDER_REF_LENGTH),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        return {
            'Trdacct': decode_str(bytes(self.Trdacct)),
            'BoardId': decode_str(bytes(self.BoardId)),
            'StkBiz': self.StkBiz,
            'StkBizAction': self.StkBizAction,
            'Symbol': decode_str(bytes(self.Symbol)),
            'OrderQty': self.OrderQty,
            'OrderPrice': decode_str(bytes(self.OrderPrice)),
            'OrderRef': decode_str(bytes(self.OrderRef)),
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建结构体"""
        from ctypes import addressof, memmove
        from .utils import encode_str, format_price
        obj = cls()
        
        struct_addr = addressof(obj)
        offset = 0
        
        # Trdacct
        trdacct_str = data.get('Trdacct', '')
        trdacct_bytes = encode_str(trdacct_str)[:OX_TRDACCT_LENGTH].ljust(OX_TRDACCT_LENGTH, b'\x00')
        memmove(struct_addr + offset, trdacct_bytes, OX_TRDACCT_LENGTH)
        offset += OX_TRDACCT_LENGTH
        
        # BoardId
        boardid_str = data.get('BoardId', '')
        boardid_bytes = encode_str(boardid_str)[:OX_BOARDID_LENGTH].ljust(OX_BOARDID_LENGTH, b'\x00')
        memmove(struct_addr + offset, boardid_bytes, OX_BOARDID_LENGTH)
        offset += OX_BOARDID_LENGTH
        
        # StkBiz, StkBizAction
        obj.StkBiz = data.get('StkBiz', 100)
        obj.StkBizAction = data.get('StkBizAction', 100)
        offset += 8  # StkBiz(4) + StkBizAction(4)
        
        # Symbol
        symbol_str = data.get('Symbol', '')
        symbol_bytes = encode_str(symbol_str)[:OX_SYMBOL_LENGTH].ljust(OX_SYMBOL_LENGTH, b'\x00')
        memmove(struct_addr + offset, symbol_bytes, OX_SYMBOL_LENGTH)
        offset += OX_SYMBOL_LENGTH
        
        # OrderQty
        obj.OrderQty = data.get('OrderQty', 0)
        offset += 4  # OrderQty(4)
        
        # OrderPrice
        order_price = data.get('OrderPrice', '0')
        if isinstance(order_price, (int, float)):
            order_price = format_price(order_price)
        price_bytes = encode_str(order_price)[:OX_ORDERPRICE_LENGTH].ljust(OX_ORDERPRICE_LENGTH, b'\x00')
        memmove(struct_addr + offset, price_bytes, OX_ORDERPRICE_LENGTH)
        offset += OX_ORDERPRICE_LENGTH
        
        # OrderRef
        order_ref = data.get('OrderRef', '')
        order_ref_bytes = encode_str(order_ref)[:OX_ORDER_REF_LENGTH].ljust(OX_ORDER_REF_LENGTH, b'\x00')
        memmove(struct_addr + offset, order_ref_bytes, OX_ORDER_REF_LENGTH)
        
        return obj


class COXReqBatchOrderTicketField(Structure):
    """批量下单请求结构体
    
    对应 C++ 结构体：
    struct COXReqBatchOrderTicketField {
        OXAccountType  AcctType;               // 账户类型(必需)
        char Account[OX_ACCOUNT_LENGTH];       // 资金账号(必需)
        int  StkBiz;                           // 证券业务
        int  StkBizAction;                     // 证券业务指令
        uint16_t TotalCount;                   // 委托数量
        COXOrderItem orderArray[MAX_ORDERS_COUNT];  // 委托信息
    };
    """
    _pack_ = 1
    _fields_ = [
        ('AcctType', c_char),           # OXAccountType (char)
        ('Account', c_char * OX_ACCOUNT_LENGTH),
        ('StkBiz', c_int),
        ('StkBizAction', c_int),
        ('TotalCount', c_uint16),
        ('orderArray', COXOrderItem * MAX_ORDERS_COUNT),
    ]
    
    def to_dict(self):
        """转换为字典"""
        from .utils import decode_str
        order_list = []
        for i in range(self.TotalCount):
            if i < MAX_ORDERS_COUNT:
                order_list.append(self.orderArray[i].to_dict())
        
        return {
            'AcctType': chr(self.AcctType) if isinstance(self.AcctType, int) else self.AcctType.decode('utf-8') if isinstance(self.AcctType, bytes) else self.AcctType,
            'Account': decode_str(bytes(self.Account)),
            'StkBiz': self.StkBiz,
            'StkBizAction': self.StkBizAction,
            'TotalCount': self.TotalCount,
            'orderArray': order_list,
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
        offset = 1  # AcctType(1)
        
        # Account
        account_str = data.get('Account', '')
        account_bytes = encode_str(account_str)[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
        memmove(struct_addr + offset, account_bytes, OX_ACCOUNT_LENGTH)
        offset += OX_ACCOUNT_LENGTH
        
        # StkBiz, StkBizAction
        obj.StkBiz = data.get('StkBiz', 100)
        obj.StkBizAction = data.get('StkBizAction', 100)
        offset += 8  # StkBiz(4) + StkBizAction(4)
        
        # TotalCount and orderArray
        order_list = data.get('orderArray', [])
        total_count = min(len(order_list), MAX_ORDERS_COUNT)
        obj.TotalCount = total_count
        
        # 复制订单数组
        order_array_offset = offset + 2  # TotalCount(2)
        for i in range(total_count):
            order_item = COXOrderItem.from_dict(order_list[i])
            memmove(struct_addr + order_array_offset + i * sizeof(COXOrderItem),
                   addressof(order_item), sizeof(COXOrderItem))
        
        return obj
