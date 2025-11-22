"""
查询功能示例代码

演示如何使用 stock_ox API 进行查询操作。

注意：查询功能将在阶段四实现，本示例为占位示例。
待查询功能实现后，可以取消注释并完善本示例。
"""

import sys
import os
import time

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXQueryError


class QuerySpi(OXTradeSpi):
    """自定义查询回调接口"""
    
    def on_rsp_query_balance(self, request, error, is_last, field):
        """资金查询响应回调"""
        print(f"\n[资金查询响应] 请求编号: {request}, 是否最后一条: {is_last}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 查询失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"  ✓ 查询成功")
            if field:
                print(f"    可用资金: {field.get('Available', '0')}")
                print(f"    总资产: {field.get('TotalAsset', '0')}")
                print(f"    持仓市值: {field.get('MarketValue', '0')}")
    
    def on_rsp_query_positions(self, request, error, is_last, field):
        """持仓查询响应回调"""
        print(f"\n[持仓查询响应] 请求编号: {request}, 是否最后一条: {is_last}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 查询失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"  ✓ 查询成功")
            if field:
                print(f"    证券代码: {field.get('Symbol', 'N/A')}")
                print(f"    持仓数量: {field.get('PositionQty', 0)}")
                print(f"    可用数量: {field.get('AvailableQty', 0)}")
                print(f"    持仓成本: {field.get('CostPrice', '0')}")
                print(f"    当前价格: {field.get('CurrentPrice', '0')}")
                print(f"    盈亏: {field.get('ProfitLoss', '0')}")
    
    def on_rsp_query_orders(self, request, error, is_last, field):
        """委托查询响应回调"""
        print(f"\n[委托查询响应] 请求编号: {request}, 是否最后一条: {is_last}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 查询失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"  ✓ 查询成功")
            if field:
                print(f"    委托编号: {field.get('OrderNo', 'N/A')}")
                print(f"    证券代码: {field.get('Symbol', 'N/A')}")
                print(f"    委托数量: {field.get('OrderQty', 0)}")
                print(f"    委托价格: {field.get('OrderPrice', '0')}")
                print(f"    委托状态: {field.get('OrderState', 'N/A')}")
                print(f"    成交数量: {field.get('FilledQty', 0)}")
    
    def on_rsp_query_trade_accounts(self, request, error, is_last, field):
        """股东账号查询响应回调"""
        print(f"\n[股东账号查询响应] 请求编号: {request}, 是否最后一条: {is_last}")
        if error and error.get('ErrorId', 0) != 0:
            print(f"  ❌ 查询失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"  ✓ 查询成功")
            if field:
                print(f"    股东账号: {field.get('Trdacct', 'N/A')}")
                print(f"    交易板块: {field.get('BoardId', 'N/A')}")
                print(f"    账户类型: {field.get('AccountType', 'N/A')}")


def example_query_balance():
    """资金查询示例"""
    print("=" * 60)
    print("资金查询示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = QuerySpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        print("\n[资金查询] 查询账户资金...")
        
        # 注意：查询功能尚未实现，以下代码为示例模板
        # 待阶段四实现后，取消注释并测试
        """
        request_id = api.query_balance()
        print(f"✓ 资金查询请求已发送，请求编号: {request_id}")
        
        # 等待查询响应
        time.sleep(1.0)
        """
        
        print("⚠️  查询功能尚未实现（阶段四）")
        print("  查询功能实现后，将支持以下查询：")
        print("    - query_balance() - 查询资金")
        print("    - query_positions() - 查询持仓")
        print("    - query_orders() - 查询委托")
        print("    - query_filled_details() - 查询成交明细")
        print("    - query_trade_accounts() - 查询股东账号")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def example_query_positions():
    """持仓查询示例"""
    print("\n" + "=" * 60)
    print("持仓查询示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = QuerySpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        print("\n[持仓查询] 查询账户持仓...")
        
        # 注意：查询功能尚未实现，以下代码为示例模板
        """
        request_id = api.query_positions()
        print(f"✓ 持仓查询请求已发送，请求编号: {request_id}")
        
        # 等待查询响应
        time.sleep(1.0)
        """
        
        print("⚠️  查询功能尚未实现（阶段四）")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def example_query_orders():
    """委托查询示例"""
    print("\n" + "=" * 60)
    print("委托查询示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = QuerySpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        print("\n[委托查询] 查询当日委托...")
        
        # 注意：查询功能尚未实现，以下代码为示例模板
        """
        # 查询当日委托
        request_id = api.query_orders()
        print(f"✓ 委托查询请求已发送，请求编号: {request_id}")
        
        # 等待查询响应
        time.sleep(1.0)
        """
        
        print("⚠️  查询功能尚未实现（阶段四）")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def example_query_trade_accounts():
    """股东账号查询示例"""
    print("\n" + "=" * 60)
    print("股东账号查询示例")
    print("=" * 60)
    
    api = OXTradeApi()
    spi = QuerySpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=5.0)
        
        print("\n[股东账号查询] 查询账户股东账号...")
        
        # 注意：查询功能尚未实现，以下代码为示例模板
        """
        request_id = api.query_trade_accounts()
        print(f"✓ 股东账号查询请求已发送，请求编号: {request_id}")
        
        # 等待查询响应
        time.sleep(1.0)
        """
        
        print("⚠️  查询功能尚未实现（阶段四）")
        print("  待阶段四实现后，将支持查询账户关联的所有股东账号")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        api.stop()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("stock_ox 查询功能示例")
    print("=" * 60)
    print("\n注意：查询功能将在阶段四实现")
    print("本示例展示了查询功能的预期使用方式")
    print("=" * 60)
    
    # 示例 1: 资金查询
    example_query_balance()
    
    # 示例 2: 持仓查询
    example_query_positions()
    
    # 示例 3: 委托查询
    example_query_orders()
    
    # 示例 4: 股东账号查询
    example_query_trade_accounts()
    
    print("\n" + "=" * 60)
    print("查询功能示例完成")
    print("=" * 60)
    print("\n待查询功能实现后，可以取消注释示例代码并测试")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

