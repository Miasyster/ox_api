"""
常量定义模块

定义所有常量（字符串长度、业务代码等）。
"""

# 字符串长度常量
OX_ERRORINFO_LENGTH = 128
OX_ACCOUNT_LENGTH = 24
OX_PASSWORD_LENGTH = 16
OX_RESERVED_LENGTH = 256
OX_BOARDID_LENGTH = 4
OX_SYMBOL_LENGTH = 36
OX_ORDERID_LENGTH = 16
OX_QUERYPOS_LENGTH = 36
OX_TRDACCT_LENGTH = 24
OX_ORDERPRICE_LENGTH = 16
OX_CUSTCODE_LENGTH = 24
OX_CASHNO_LENGTH = 16

# 业务代码
STK_BIZ_BUY = 100              # 买入
STK_BIZ_SELL = 101             # 卖出
STK_BIZ_ETF_CREATION = 181     # ETF 申购
STK_BIZ_ETF_REDEMPTION = 182   # ETF 赎回
STK_BIZ_GUARD_BUY = 700        # 担保品买入
STK_BIZ_GUARD_SELL = 701       # 担保品卖出
STK_BIZ_CREDIT_BUY = 702       # 融资买入
STK_BIZ_CREDIT_SELL = 703      # 融券卖出

# 委托类型
ORDER_TYPE_LIMIT = 100         # 限价单
ORDER_TYPE_MKT = 121           # 最优成交剩余撤销（市价单）

# 板块代码
BOARD_SH = "10"                # 上海
BOARD_SZ = "00"                # 深圳

