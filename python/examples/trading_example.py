"""
基础交易示例代码

演示如何使用 stock_ox API 进行完整的交易操作，包括：
1. API 初始化
2. 账户登录
3. 下单（限价单、市价单）
4. 接收委托回报和成交回报
5. 撤单
6. 批量下单
"""

import sys
import os
import time

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.constants import (
    STK_BIZ_BUY, STK_BIZ_SELL,
    ORDER_TYPE_LIMIT, ORDER_TYPE_MKT,
    BOARD_SH, BOARD_SZ
)
from stock_ox.exceptions import OXConnectionError, OXLoginError, OXOrderError


class TradingSpi(OXTradeSpi):
    """自定义交易回调接口"""
    
    def __init__(self):
        super().__init__()
        self.order_callbacks = []
        self.filled_callbacks = []
        self.cancel_callbacks = []
    
    def on_rsp_logon(self, request, error, is_last, field):
        """登录响应回调"""
        print(f"\n[登录响应] 请求编号: {request}, 是否最后一条: {is_last}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 登录失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            account = field.get('Account', '') if field else ''
            print(f"  ✓ 登录成功: Account={account}")
            if field:
                print(f"    客户代码: {field.get('CustCode', '')}")
                print(f"    账户类型: {field.get('AcctType', '')}")
    
    def on_rtn_order(self, field):
        """委托回报回调"""
        if field:
            self.order_callbacks.append(field)
            print(f"\n[委托回报]")
            print(f"  委托编号: {field.get('OrderNo', 'N/A')}")
            print(f"  证券代码: {field.get('Symbol', 'N/A')}")
            print(f"  交易板块: {field.get('BoardId', 'N/A')}")
            print(f"  委托数量: {field.get('OrderQty', 0)}")
            print(f"  委托价格: {field.get('OrderPrice', '0')}")
            print(f"  委托状态: {field.get('OrderState', 'N/A')}")
            print(f"  成交数量: {field.get('FilledQty', 0)}")
            print(f"  撤单数量: {field.get('CanceledQty', 0)}")
            if field.get('ErrorId', 0) != 0:
                print(f"  错误信息: {field.get('ExeInfo', '')}")
    
    def on_rtn_order_filled(self, field):
        """成交回报回调"""
        if field:
            self.filled_callbacks.append(field)
            print(f"\n[成交回报]")
            print(f"  委托编号: {field.get('OrderNo', 'N/A')}")
            print(f"  证券代码: {field.get('Symbol', 'N/A')}")
            print(f"  成交数量: {field.get('FilledQty', 0)}")
            print(f"  成交价格: {field.get('FilledPrice', '0')}")
            print(f"  成交金额: {field.get('FilledAmt', '0')}")
            print(f"  成交日期: {field.get('FilledDate', 0)}")
            print(f"  成交时间: {field.get('FilledTime', '')}")
    
    def on_rsp_cancel_ticket(self, request, error, field):
        """撤单响应回调"""
        self.cancel_callbacks.append({
            'request': request,
            'error': error,
            'field': field
        })
        print(f"\n[撤单响应] 请求编号: {request}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 撤单失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"  ✓ 撤单成功")
            if field:
                print(f"    委托编号: {field.get('OrderNo', 'N/A')}")
                print(f"    撤单状态: {field.get('OrderState', 'N/A')}")
    
    def on_rsp_batch_order(self, request, error, field):
        """批量下单响应回调"""
        print(f"\n[批量下单响应] 请求编号: {request}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 批量下单失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"  ✓ 批量下单成功")
            if field:
                total_count = field.get('TotalCount', 0)
                print(f"    总订单数: {total_count}")


def example_basic_trading():
    """基础交易示例：下单和撤单"""
    print("=" * 60)
    print("基础交易示例：下单和撤单")
    print("=" * 60)
    
    # 创建 API 实例
    api = OXTradeApi()
    spi = TradingSpi()
    
    try:
        # 步骤 1: 初始化 API
        print("\n[步骤 1] 初始化 API...")
        api.init()
        print("✓ API 初始化成功")
        
        # 步骤 2: 注册回调接口
        print("\n[步骤 2] 注册回调接口...")
        api.register_spi(spi)
        print("✓ 回调接口注册成功")
        
        # 步骤 3: 登录账户
        print("\n[步骤 3] 登录账户...")
        account = '110060035050'
        password = '111111'
        account_type = AccountType.CREDIT
        
        api.login(account, password, account_type, timeout=5.0)
        print(f"✓ 账户 {account} 登录成功")
        
        # 确保账户信息已设置（在实际环境中，这些信息会从登录响应中获取）
        if not api._account:
            api._account = account
            api._acct_type = account_type
        
        # 模拟登录响应
        api.spi.on_rsp_logon(1, None, True, {
            'IntOrg': 12345,
            'CustCode': 'CUST001',
            'AcctType': account_type.value,
            'Account': account
        })
        time.sleep(0.1)
        
        # 步骤 4: 下单（限价单）
        print("\n[步骤 4] 下单（限价单）...")
        trdacct = 'A197407210'  # 股东账号
        board_id = BOARD_SH  # 上海交易所
        symbol = '600000'  # 证券代码
        price = 10.50  # 委托价格
        quantity = 100  # 委托数量（股）
        stk_biz = STK_BIZ_BUY  # 买入
        stk_biz_action = ORDER_TYPE_LIMIT  # 限价单
        
        order_request_id = api.order(
            trdacct=trdacct,
            board_id=board_id,
            symbol=symbol,
            price=price,
            quantity=quantity,
            stk_biz=stk_biz,
            stk_biz_action=stk_biz_action,
            order_ref='ORDER001'
        )
        
        print(f"✓ 下单成功，请求编号: {order_request_id}")
        print(f"  股东账号: {trdacct}")
        print(f"  交易板块: {board_id} (上海)")
        print(f"  证券代码: {symbol}")
        print(f"  委托价格: {price}")
        print(f"  委托数量: {quantity}")
        print(f"  委托类型: 限价单")
        print(f"  委托方向: 买入")
        
        # 等待委托回报
        print("\n[步骤 5] 等待委托回报...")
        time.sleep(0.3)
        
        # 模拟成交回报
        print("\n[步骤 6] 模拟成交回报...")
        filled_dict = {
            'Account': account,
            'Trdacct': trdacct,
            'Symbol': symbol,
            'ExchangeId': '1',
            'BoardId': board_id,
            'StkBiz': stk_biz,
            'StkBizAction': stk_biz_action,
            'TradeSn': 'TRADE001',
            'OrderNo': 123456789012345,
            'OrderRef': 'ORDER001',
            'FilledQty': 100,
            'FilledPrice': '10.50',
            'FilledAmt': '1050.00',
            'FilledDate': 20240101,
            'FilledTime': '14:30:00',
            'ErrorId': 0,
            'RetMessage': '',
        }
        api.spi.on_rtn_order_filled(filled_dict)
        time.sleep(0.1)
        
        # 步骤 7: 撤单（模拟）
        print("\n[步骤 7] 撤单示例...")
        order_no = 123456789012345
        cancel_request_id = api.cancel(board_id, order_no)
        print(f"✓ 撤单请求已发送，请求编号: {cancel_request_id}")
        print(f"  委托编号: {order_no}")
        
        # 等待撤单响应
        print("\n[步骤 8] 等待撤单响应...")
        time.sleep(0.2)
        
        print("\n✓ 基础交易示例完成")
        
    except OXConnectionError as e:
        print(f"\n❌ 连接错误: {e}")
    except OXLoginError as e:
        print(f"\n❌ 登录错误: {e}")
    except OXOrderError as e:
        print(f"\n❌ 交易错误: {e}")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 停止 API
        print("\n[清理] 停止 API...")
        api.stop()
        print("✓ API 已停止")


def example_market_order():
    """市价单示例"""
    print("\n" + "=" * 60)
    print("市价单示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = TradingSpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 市价单（价格为0）
        print("\n[市价单] 下单...")
        request_id = api.order(
            trdacct='A197407210',
            board_id=BOARD_SH,
            symbol='600000',
            price=0,  # 市价单价格为0
            quantity=100,
            stk_biz=STK_BIZ_BUY,
            stk_biz_action=ORDER_TYPE_MKT  # 市价单
        )
        
        print(f"✓ 市价单下单成功，请求编号: {request_id}")
        print(f"  委托类型: 市价单")
        
        time.sleep(0.2)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def example_batch_order():
    """批量下单示例"""
    print("\n" + "=" * 60)
    print("批量下单示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = TradingSpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 批量下单
        print("\n[批量下单] 准备订单列表...")
        order_list = [
            {
                'Trdacct': 'A197407210',
                'BoardId': BOARD_SH,
                'Symbol': '600000',
                'OrderPrice': 10.50,
                'OrderQty': 100,
                'OrderRef': 'BATCH001',
            },
            {
                'Trdacct': 'A197407210',
                'BoardId': BOARD_SH,
                'Symbol': '600001',
                'OrderPrice': 11.00,
                'OrderQty': 200,
                'OrderRef': 'BATCH002',
            },
        ]
        
        request_id = api.batch_order(
            order_list=order_list,
            stk_biz=STK_BIZ_BUY,
            stk_biz_action=ORDER_TYPE_LIMIT
        )
        
        print(f"✓ 批量下单成功，请求编号: {request_id}")
        print(f"  订单数量: {len(order_list)}")
        for i, order in enumerate(order_list, 1):
            print(f"  订单 {i}: {order['Symbol']} x {order['OrderQty']} @ {order['OrderPrice']}")
        
        time.sleep(0.2)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def example_context_manager():
    """使用上下文管理器的示例"""
    print("\n" + "=" * 60)
    print("使用上下文管理器的示例")
    print("=" * 60)
    
    spi = TradingSpi()
    
    try:
        # 使用上下文管理器，自动初始化和清理
        with OXTradeApi() as api:
            api.register_spi(spi)
            api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
            
            if not api._account:
                api._account = '110060035050'
                api._acct_type = AccountType.CREDIT
            
            print("\n[下单] 使用上下文管理器...")
            request_id = api.order(
                trdacct='A197407210',
                board_id=BOARD_SH,
                symbol='600000',
                price=10.50,
                quantity=100
            )
            
            print(f"✓ 下单成功，请求编号: {request_id}")
            time.sleep(0.2)
        
        # 上下文管理器退出后，API 自动停止
        print("✓ API 已自动停止")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def example_different_boards():
    """不同交易板块示例"""
    print("\n" + "=" * 60)
    print("不同交易板块示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = TradingSpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 上海市场
        print("\n[上海市场] 下单...")
        sh_request_id = api.order(
            trdacct='A197407210',
            board_id=BOARD_SH,
            symbol='600000',
            price=10.50,
            quantity=100
        )
        print(f"✓ 上海市场下单成功，请求编号: {sh_request_id}")
        
        time.sleep(0.1)
        
        # 深圳市场
        print("\n[深圳市场] 下单...")
        sz_request_id = api.order(
            trdacct='0000035074',
            board_id=BOARD_SZ,
            symbol='000001',
            price=12.00,
            quantity=100
        )
        print(f"✓ 深圳市场下单成功，请求编号: {sz_request_id}")
        
        time.sleep(0.2)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("stock_ox 基础交易示例")
    print("=" * 60)
    
    # 示例 1: 基础交易（下单和撤单）
    example_basic_trading()
    
    # 示例 2: 市价单
    example_market_order()
    
    # 示例 3: 批量下单
    example_batch_order()
    
    # 示例 4: 使用上下文管理器
    example_context_manager()
    
    # 示例 5: 不同交易板块
    example_different_boards()
    
    print("\n" + "=" * 60)
    print("所有示例完成")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

