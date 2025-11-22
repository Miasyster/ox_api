"""
下单功能示例代码

演示如何使用 stock_ox API 进行下单操作。
"""

import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.constants import STK_BIZ_BUY, STK_BIZ_SELL


class MyTradeSpi(OXTradeSpi):
    """自定义交易回调接口"""
    
    def on_rsp_logon(self, request, error, is_last, field):
        """登录响应回调"""
        if error and error.get('ErrorId', 0) != 0:
            print(f"登录失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"登录成功: Account={field.get('Account', '') if field else ''}")
    
    def on_rtn_order(self, field):
        """委托回报回调"""
        if field:
            print(f"\n[委托回报]")
            print(f"  委托编号: {field.get('OrderNo', '')}")
            print(f"  证券代码: {field.get('Symbol', '')}")
            print(f"  委托数量: {field.get('OrderQty', 0)}")
            print(f"  委托价格: {field.get('OrderPrice', '0')}")
            print(f"  委托状态: {field.get('OrderState', '')}")
            print(f"  成交数量: {field.get('FilledQty', 0)}")
            print(f"  撤单数量: {field.get('CanceledQty', 0)}")
            if field.get('ErrorId', 0) != 0:
                print(f"  错误信息: {field.get('ExeInfo', '')}")
    
    def on_rtn_order_filled(self, field):
        """成交回报回调"""
        if field:
            print(f"\n[成交回报]")
            print(f"  委托编号: {field.get('OrderNo', '')}")
            print(f"  证券代码: {field.get('Symbol', '')}")
            print(f"  成交数量: {field.get('FilledQty', 0)}")
            print(f"  成交价格: {field.get('FilledPrice', '0')}")
            print(f"  成交金额: {field.get('FilledAmt', '0')}")
            print(f"  成交日期: {field.get('FilledDate', 0)}")
            print(f"  成交时间: {field.get('FilledTime', '')}")


def main():
    """主函数"""
    print("=" * 60)
    print("下单功能示例")
    print("=" * 60)
    
    # 创建 API 实例
    api = OXTradeApi()
    
    try:
        # 初始化 API
        print("\n[步骤 1] 初始化 API...")
        api.init()
        print("✓ API 初始化成功")
        
        # 创建并注册回调接口
        print("\n[步骤 2] 注册回调接口...")
        spi = MyTradeSpi()
        api.register_spi(spi)
        print("✓ 回调接口注册成功")
        
        # 登录
        print("\n[步骤 3] 登录账户...")
        account = '110060035050'
        password = '111111'
        account_type = AccountType.CREDIT
        
        # 注意：在测试环境中，登录会自动设置账户信息
        # 在实际使用中，账户信息会从登录响应中获取
        api.login(account, password, account_type, timeout=5.0)
        print(f"✓ 账户 {account} 登录成功")
        
        # 确保账户信息已设置
        if not api._account:
            api._account = account
            api._acct_type = account_type
        
        # 下单
        print("\n[步骤 4] 下单...")
        trdacct = 'A197407210'  # 股东账号
        board_id = '10'  # 上海交易所
        symbol = '600000'  # 证券代码
        price = 10.50  # 委托价格
        quantity = 100  # 委托数量（股）
        stk_biz = STK_BIZ_BUY  # 买入
        order_ref = 'ORDER001'  # 客户委托信息
        
        request_id = api.order(
            trdacct=trdacct,
            board_id=board_id,
            symbol=symbol,
            price=price,
            quantity=quantity,
            stk_biz=stk_biz,
            order_ref=order_ref
        )
        
        print(f"✓ 下单成功，请求编号: {request_id}")
        print(f"  股东账号: {trdacct}")
        print(f"  证券代码: {symbol}")
        print(f"  委托价格: {price}")
        print(f"  委托数量: {quantity}")
        print(f"  委托方向: {'买入' if stk_biz == STK_BIZ_BUY else '卖出'}")
        
        # 等待委托回报
        print("\n[步骤 5] 等待委托回报...")
        import time
        time.sleep(0.3)
        
        print("\n[步骤 6] 示例完成")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 停止 API
        print("\n[清理] 停止 API...")
        api.stop()
        print("✓ API 已停止")


if __name__ == "__main__":
    main()

