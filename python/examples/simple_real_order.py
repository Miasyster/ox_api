"""
简化版真实股票下单脚本

用于快速进行真实的股票下单操作。
使用配置文件中的账户信息进行登录和下单。

⚠️ 警告：这是真实的交易系统，所有操作都会产生真实的交易！
"""

import sys
import os
import time
import threading
import configparser
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.constants import (
    STK_BIZ_BUY, STK_BIZ_SELL,
    ORDER_TYPE_LIMIT, ORDER_TYPE_MKT,
    BOARD_SH, BOARD_SZ
)
from stock_ox.exceptions import (
    OXConnectionError, OXLoginError, OXOrderError, OXDllError
)


class SimpleOrderSpi(OXTradeSpi):
    """简化的下单回调接口"""
    
    def __init__(self):
        super().__init__()
        self.login_success = False
        self.login_error = None
        self.login_event = threading.Event()
        self.order_received = False
    
    def on_connected(self) -> int:
        print("✓ 已连接到交易服务器")
        return 0
    
    def on_disconnected(self) -> int:
        print("⚠ 已断开与交易服务器的连接")
        return 0
    
    def on_rsp_logon(self, request, error, is_last, field):
        """登录响应回调"""
        if error and error.get('ErrorId', 0) != 0:
            self.login_success = False
            self.login_error = error.get('ErrorInfo', '未知错误')
            print(f"❌ 登录失败: {self.login_error}")
        else:
            self.login_success = True
            account = field.get('Account', '') if field else ''
            print(f"✓ 登录成功! 资金账号: {account}")
        
        self.login_event.set()
    
    def on_rtn_order(self, field):
        """委托回报回调"""
        if not field:
            return
        
        self.order_received = True
        order_no = field.get('OrderNo', '')
        symbol = field.get('Symbol', '')
        order_state = field.get('OrderState', '')
        filled_qty = field.get('FilledQty', 0)
        
        print(f"\n[委托回报] 委托编号: {order_no}")
        print(f"  证券代码: {symbol}")
        print(f"  委托状态: {order_state}")
        print(f"  成交数量: {filled_qty} 股")
    
    def on_rtn_order_filled(self, field):
        """成交回报回调"""
        if not field:
            return
        
        order_no = field.get('OrderNo', '')
        symbol = field.get('Symbol', '')
        filled_qty = field.get('FilledQty', 0)
        filled_price = field.get('FilledPrice', '0')
        
        print(f"\n[成交回报] 委托编号: {order_no}")
        print(f"  证券代码: {symbol}")
        print(f"  成交数量: {filled_qty} 股")
        print(f"  成交价格: {filled_price} 元")
    
    def on_rsp_cancel_ticket(self, request, error, field):
        """撤单响应回调"""
        if error and error.get('ErrorId', 0) != 0:
            print(f"❌ 撤单失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            print(f"✓ 撤单成功")


def load_config(config_path=None):
    """从配置文件加载账户信息"""
    if config_path is None:
        # 自动查找配置文件
        current_dir = Path(__file__).parent.parent.parent
        config_path = current_dir / 'bin' / 'config' / 'config.ini'
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    
    if 'user' not in config:
        raise ValueError("配置文件中缺少 [user] 节点")
    
    user_config = config['user']
    
    return {
        'account': user_config.get('acct', ''),
        'password': user_config.get('password', ''),
        'acct_type': user_config.get('acct_type', '0'),
        'sh_trade_account': user_config.get('sh_trade_account', ''),
        'sz_trade_account': user_config.get('sz_trade_account', ''),
    }


def simple_order():
    """简化的真实下单函数"""
    print("=" * 60)
    print("简化版真实股票下单系统")
    print("=" * 60)
    print("\n⚠ 警告: 这是一个真实的交易系统!")
    print("   所有操作都会产生真实的交易!")
    
    confirm = input("\n确认继续? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消操作")
        return
    
    try:
        # 加载配置
        print("\n正在加载配置文件...")
        config = load_config()
        
        if not config.get('account') or not config.get('password'):
            raise ValueError("配置文件中缺少账户或密码信息")
        
        # 创建 API 和 SPI
        api = OXTradeApi()
        spi = SimpleOrderSpi()
        
        # 初始化 API
        print("正在初始化 API...")
        api.init()
        print("✓ API 初始化成功")
        
        # 注册回调接口
        api.register_spi(spi)
        print("✓ 回调接口注册成功")
        
        # 登录
        print("\n正在登录账户...")
        account = config['account']
        password = config['password']
        acct_type_str = config.get('acct_type', '0')
        
        # 转换账户类型
        type_map = {
            '0': AccountType.STOCK,
            '1': AccountType.OPTION,
            '2': AccountType.FUTURE,
            '3': AccountType.CREDIT
        }
        account_type = type_map.get(acct_type_str, AccountType.STOCK)
        
        api.login(account, password, account_type, timeout=30.0)
        
        # 等待登录回调
        if spi.login_event.wait(timeout=30.0):
            if not spi.login_success:
                print(f"\n❌ 登录失败: {spi.login_error or '未知错误'}")
                return
        else:
            print("\n❌ 登录超时")
            return
        
        print("\n" + "=" * 60)
        print("登录成功，可以开始下单")
        print("=" * 60)
        
        # 输入下单信息
        print("\n请输入下单信息:")
        
        # 交易方向
        print("\n交易方向:")
        print("  1 - 买入")
        print("  2 - 卖出")
        direction = input("请选择 (1/2): ").strip()
        stk_biz = STK_BIZ_BUY if direction == '1' else STK_BIZ_SELL
        
        # 交易板块
        print("\n交易板块:")
        print("  1 - 上海 (600xxx, 688xxx)")
        print("  2 - 深圳 (000xxx, 001xxx, 002xxx, 300xxx)")
        board_choice = input("请选择 (1/2): ").strip()
        board_id = BOARD_SH if board_choice == '1' else BOARD_SZ
        
        # 股东账号
        if board_id == BOARD_SH:
            trdacct = input(f"上海股东账号 (默认: {config.get('sh_trade_account', '')}): ").strip()
            if not trdacct:
                trdacct = config.get('sh_trade_account', '')
        else:
            trdacct = input(f"深圳股东账号 (默认: {config.get('sz_trade_account', '')}): ").strip()
            if not trdacct:
                trdacct = config.get('sz_trade_account', '')
        
        # 证券代码
        symbol = input("证券代码 (如 600000): ").strip()
        
        # 委托类型
        print("\n委托类型:")
        print("  1 - 限价单")
        print("  2 - 市价单")
        order_type = input("请选择 (1/2, 默认 1): ").strip() or '1'
        stk_biz_action = ORDER_TYPE_LIMIT if order_type == '1' else ORDER_TYPE_MKT
        
        # 委托价格
        price = 0.0
        if order_type == '1':
            price_str = input("委托价格 (元): ").strip()
            try:
                price = float(price_str)
            except ValueError:
                print("⚠ 价格格式错误，使用 0")
                price = 0.0
        
        # 委托数量
        quantity_str = input("委托数量 (股): ").strip()
        try:
            quantity = int(quantity_str)
        except ValueError:
            print("⚠ 数量格式错误，使用 100")
            quantity = 100
        
        # 确认信息
        print("\n" + "=" * 60)
        print("下单信息确认:")
        print("=" * 60)
        print(f"交易方向: {'买入' if direction == '1' else '卖出'}")
        print(f"交易板块: {'上海' if board_choice == '1' else '深圳'}")
        print(f"股东账号: {trdacct}")
        print(f"证券代码: {symbol}")
        print(f"委托类型: {'限价单' if order_type == '1' else '市价单'}")
        if order_type == '1':
            print(f"委托价格: {price} 元")
        print(f"委托数量: {quantity} 股")
        print("=" * 60)
        
        confirm = input("\n确认下单? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消下单")
            return
        
        # 下单
        print("\n正在发送下单请求...")
        try:
            request_id = api.order(
                trdacct=trdacct,
                board_id=board_id,
                symbol=symbol,
                price=price,
                quantity=quantity,
                stk_biz=stk_biz,
                stk_biz_action=stk_biz_action,
                order_ref='SIMPLE_ORDER'
            )
            print(f"✓ 下单请求已发送，请求编号: {request_id}")
            print("等待委托回报...")
            
            # 等待回报
            time.sleep(3.0)
            
            if spi.order_received:
                print("\n✓ 已收到委托回报")
            else:
                print("\n⚠ 未收到委托回报（可能还在处理中）")
            
        except OXOrderError as e:
            print(f"\n❌ 下单失败: {e}")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        
    except FileNotFoundError as e:
        print(f"\n❌ 配置文件错误: {e}")
        print("   请确保配置文件存在: ox_api/bin/config/config.ini")
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
    except OXDllError as e:
        print(f"\n❌ DLL 加载错误: {e}")
        print("   请确保 DLL 文件存在且路径正确")
    except OXConnectionError as e:
        print(f"\n❌ 连接错误: {e}")
    except OXLoginError as e:
        print(f"\n❌ 登录错误: {e}")
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 停止 API
        print("\n正在停止 API...")
        try:
            api.stop()
            print("✓ API 已停止")
        except:
            pass
        print("\n感谢使用!")


if __name__ == "__main__":
    simple_order()

