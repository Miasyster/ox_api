"""
类型枚举模块

定义 Python 枚举类，提供类型转换函数。
"""

from enum import Enum


class AccountType(Enum):
    """账户类型枚举"""
    STOCK = '0'     # 现货
    OPTION = '1'    # 期权
    FUTURE = '2'    # 期货
    CREDIT = '3'    # 信用交易


class OrderState(Enum):
    """委托状态枚举"""
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
    REPORT_WAITING = 'A'        # 报盘等待
    REPORT_ACK = 'B'            # 报盘确认
    NEED_SEND = 'N'             # 需报送
    DIVIDEND_CANCELED = 'D'     # 红利息止
    EXPIRED = 'E'               # 过期终止
    TRIGGER_AGAIN = 'T'         # 再次触发


class ExchangeId(Enum):
    """交易所枚举"""
    SH = '1'        # 上海
    SZ = '0'        # 深圳

