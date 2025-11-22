"""
常量定义模块

定义所有常量（字符串长度、业务代码等）。
映射自 C++ 头文件 OXTradeApiConst.h
"""

# ============================================================================
# 字符串长度常量（映射自 OXTradeApiConst.h）
# ============================================================================

# 基础信息长度
OX_ERRORINFO_LENGTH = 128
OX_ACCOUNT_LENGTH = 24  # 2023-09-14 从 16 增加到 24
OX_PASSWORD_LENGTH = 16
OX_RESERVED_LENGTH = 256

# 交易相关长度
OX_BOARDID_LENGTH = 4
OX_SYMBOL_LENGTH = 36  # 2022-12-21 从 12 增加到 36
OX_ORDERID_LENGTH = 16
OX_QUERYPOS_LENGTH = 36

# 账号和价格长度
OX_TRDACCT_LENGTH = 24  # 2023-06-27 从 16 增加到 24
OX_ORDERPRICE_LENGTH = 16
OX_CUSTCODE_LENGTH = 24  # 2023-09-14 从 16 增加到 24
OX_CASHNO_LENGTH = 16

# 期权相关长度
OX_OPTNUM_LENGTH = 12
OX_OPTUNDLCODE_LENGTH = 12
OX_STKPBU_LENGTH = 8
OX_ORDERTIME_LENGTH = 36

# 执行信息长度
OX_EXEINFO_LENGTH = 128
OX_FILLEDAMT_LENGTH = 24

# 账户资金长度
OX_ACCOUNTWORTH_LENGTH = 24
OX_FUNDVALUE_LENGTH = 24
OX_MARKETVALUE_LENGTH = 24
OX_FUNDPREBALANCE_LENGTH = 24
OX_FUNDBALANCE_LENGTH = 24
OX_AVAIABLE_LENGTH = 24

# 股票信息长度
OX_STKNAME_LENGTH = 16
OX_STKBCOST_LENGTH = 24
OX_STKBCOSTRLT_LENGTH = 24
OX_STKPLAMT_LENGTH = 24
OX_STKPLAMTRLT_LENGTH = 24
OX_MKTVA_LENGTH = 24
OX_COSTPRICE_LENGTH = 16
OX_PROINCOME_LENGTH = 24
OX_STKCALMKTVALE_LENGTH = 2
OX_CURRENTPRICE_LENGTH = 16
OX_PROFITPRICE_LENGTH = 16

# 价格和收入长度
OX_AVERAGEPRICE_LENGTH = 16
OX_INCOME_LENGTH = 24

# 交易序号长度
OX_TRADESN_LENGTH = 36

# 成交信息长度
OX_FILLEDPRICE_LENGTH = 16
OX_FILLEDTIME_LENGTH = 12

# 返回消息长度
OX_RETMESSAGE_LENGTH = 128

# 子账户代码长度
OX_SUBACCTCODE_LENGTH = 12
OX_OPTTRDACCT_LENGTH = 24

# 期权代码和名称长度
OX_OPTCODE_LENGTH = 36
OX_OPTNAME_LENGTH = 36

# ETF 价格信息长度
OX_ETF_PRICE_INFO = 10240
OX_STRATEGY_TEXT = 32768

# 返回信息长度
OX_RET_INFO_LENGTH = 256

# 信用交易长度
OX_CREDIT_DOUBLE_LENGTH = 24

# 委托相关长度
OX_ORDER_REF_LENGTH = 33

# 期权成本和利润长度
OX_OPTBCOST_LENGTH = 32
OX_OPTBCOSTRLT_LENGTH = 32
OX_OPTPLAMT_LENGTH = 32
OX_OPTPLAMTRLT_LENGTH = 32
OX_OPTMKTVAL_LENGTH = 32
OX_OPTPREMIUM_LENGTH = 32
OX_OPTMARGIN_LENGTH = 32
OX_OPTCVDASSET_LENGTH = 32
OX_OPTCLSPROFIT_LENGTH = 32
OX_SUMCLSPROFIT_LENGTH = 32
OX_OPTFLOATPROFIT_LENGTH = 32
OX_TOTALPROFIT_LENGTH = 32

# ETF 相关长度
OX_ETFCASHRATIO_LENGTH = 16
OX_ETFESTMCASH_LENGTH = 16
OX_ETFCASHCOMP_LENGTH = 16
OX_ETFNAVPERCU_LENGTH = 16
OX_ETFNAV_LENGTH = 16
OX_ETFOVERFLOWRATE_LENGTH = 16
OX_REDEMPTIONINSTEADAMT_LENGTH = 16
OX_CREATIONINSTEADAMT_LENGTH = 16
OX_ETFDISCOUNTRATE_LENGTH = 16

# 交易扩展信息长度
OX_TRD_EXT_INFO_LENGTH = 512

# 批量委托最大数量
MAX_ORDERS_COUNT = 500

# ============================================================================
# 业务代码常量
# ============================================================================

# 股票业务代码
STK_BIZ_BUY = 100              # 买入
STK_BIZ_SELL = 101             # 卖出
STK_BIZ_ETF_CREATION = 181     # ETF 申购
STK_BIZ_ETF_REDEMPTION = 182   # ETF 赎回

# 信用交易业务代码
STK_BIZ_GUARD_BUY = 700        # 担保品买入
STK_BIZ_GUARD_SELL = 701       # 担保品卖出
STK_BIZ_CREDIT_BUY = 702       # 融资买入
STK_BIZ_CREDIT_SELL = 703      # 融券卖出
STK_BIZ_CREDIT_REPAY = 704     # 融资还款
STK_BIZ_CREDIT_STOCK_REPAY = 705  # 融券还券

# 委托类型
ORDER_TYPE_LIMIT = 100         # 限价单
ORDER_TYPE_MKT = 121           # 最优成交剩余撤销（市价单）

# ============================================================================
# 板块代码常量
# ============================================================================

# 交易板块代码
BOARD_SH = "10"                # 上海
BOARD_SZ = "00"                # 深圳

# ============================================================================
# 货币类型常量
# ============================================================================

CURRENCY_CNY = '0'             # 人民币
CURRENCY_USD = '1'             # 美元
CURRENCY_HKD = '2'             # 港币

# ============================================================================
# 交易所代码常量
# ============================================================================

EXCHANGE_SH = '1'              # 上海证券交易所
EXCHANGE_SZ = '0'              # 深圳证券交易所

# ============================================================================
# 账户状态常量
# ============================================================================

ACCOUNT_STATUS_NORMAL = '0'    # 正常
ACCOUNT_STATUS_FROZEN = '1'    # 冻结
ACCOUNT_STATUS_CANCELLED = '2' # 注销
