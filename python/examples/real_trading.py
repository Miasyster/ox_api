"""
真实股票交易脚本

用于进行真实的股票下单操作。支持从配置文件读取账户信息或手动输入。
请确保您已经正确配置了账户信息，并且了解交易风险。

使用前请仔细阅读:
1. 确保您已经安装了所有依赖
2. 确保 DLL 文件已正确配置
3. 确保账户信息正确
4. 了解交易风险，谨慎操作
"""

import sys
import os
import time
import threading
import configparser
from pathlib import Path
from typing import Optional, Dict

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
from stock_ox.exceptions import (
    OXConnectionError, OXLoginError, OXOrderError, OXDllError
)


class RealTradingSpi(OXTradeSpi):
    """真实交易回调接口"""
    
    def __init__(self):
        super().__init__()
        self.login_success = False
        self.login_error = None
        self.login_event = None
        self.orders = {}  # 存储订单信息 {request_id: order_info}
        self.filled_orders = []  # 存储成交订单
        self.cancel_results = {}  # 存储撤单结果
    
    def set_login_event(self, event):
        """设置登录事件"""
        self.login_event = event
    
    def on_connected(self) -> int:
        """连接建立回调"""
        print("\n[连接] 已连接到交易服务器")
        return 0
    
    def on_disconnected(self) -> int:
        """连接断开回调"""
        print("\n[连接] 已断开与交易服务器的连接")
        return 0
    
    def on_rsp_logon(self, request, error, is_last, field):
        """登录响应回调"""
        print("\n" + "=" * 60)
        print("[登录响应]")
        print("=" * 60)
        
        if error and error.get('ErrorId', 0) != 0:
            error_info = error.get('ErrorInfo', '未知错误')
            print(f"❌ 登录失败!")
            print(f"   错误代码: {error.get('ErrorId', 0)}")
            print(f"   错误信息: {error_info}")
            self.login_success = False
            self.login_error = error_info
        else:
            if field:
                account = field.get('Account', '')
                cust_code = field.get('CustCode', '')
                acct_type = field.get('AcctType', '')
                
                print(f"✓ 登录成功!")
                print(f"   资金账号: {account}")
                if cust_code:
                    print(f"   客户代码: {cust_code}")
                print(f"   账户类型: {self._format_acct_type(acct_type)}")
                
                self.login_success = True
                self.login_error = None
            else:
                print("⚠ 登录响应为空")
                self.login_success = False
        
        if self.login_event:
            self.login_event.set()
    
    def on_rtn_order(self, field):
        """委托回报回调"""
        if not field:
            return
        
        print("\n" + "-" * 60)
        print("[委托回报]")
        print("-" * 60)
        
        order_no = field.get('OrderNo', '')
        symbol = field.get('Symbol', '')
        board_id = field.get('BoardId', '')
        order_qty = field.get('OrderQty', 0)
        order_price = field.get('OrderPrice', '0')
        order_state = field.get('OrderState', '')
        filled_qty = field.get('FilledQty', 0)
        canceled_qty = field.get('CanceledQty', 0)
        error_id = field.get('ErrorId', 0)
        exe_info = field.get('ExeInfo', '')
        
        print(f"委托编号: {order_no}")
        print(f"证券代码: {symbol}")
        print(f"交易板块: {self._format_board(board_id)}")
        print(f"委托数量: {order_qty} 股")
        print(f"委托价格: {order_price} 元")
        print(f"委托状态: {self._format_order_state(order_state)}")
        print(f"成交数量: {filled_qty} 股")
        print(f"撤单数量: {canceled_qty} 股")
        
        if error_id != 0:
            print(f"⚠ 错误代码: {error_id}")
            if exe_info:
                print(f"   错误信息: {exe_info}")
        
        # 保存订单信息
        if order_no:
            self.orders[order_no] = field
    
    def on_rtn_order_filled(self, field):
        """成交回报回调"""
        if not field:
            return
        
        print("\n" + "-" * 60)
        print("[成交回报]")
        print("-" * 60)
        
        order_no = field.get('OrderNo', '')
        symbol = field.get('Symbol', '')
        filled_qty = field.get('FilledQty', 0)
        filled_price = field.get('FilledPrice', '0')
        filled_amt = field.get('FilledAmt', '0')
        filled_date = field.get('FilledDate', 0)
        filled_time = field.get('FilledTime', '')
        
        print(f"委托编号: {order_no}")
        print(f"证券代码: {symbol}")
        print(f"成交数量: {filled_qty} 股")
        print(f"成交价格: {filled_price} 元")
        print(f"成交金额: {filled_amt} 元")
        if filled_date:
            print(f"成交日期: {filled_date}")
        if filled_time:
            print(f"成交时间: {filled_time}")
        
        # 保存成交信息
        self.filled_orders.append(field)
    
    def on_rsp_cancel_ticket(self, request, error, field):
        """撤单响应回调"""
        print("\n" + "-" * 60)
        print("[撤单响应]")
        print("-" * 60)
        
        if error and error.get('ErrorId', 0) != 0:
            error_info = error.get('ErrorInfo', '未知错误')
            print(f"❌ 撤单失败!")
            print(f"   错误代码: {error.get('ErrorId', 0)}")
            print(f"   错误信息: {error_info}")
            self.cancel_results[request] = {'success': False, 'error': error_info}
        else:
            if field:
                order_no = field.get('OrderNo', '')
                order_state = field.get('OrderState', '')
                print(f"✓ 撤单成功!")
                print(f"   委托编号: {order_no}")
                print(f"   委托状态: {self._format_order_state(order_state)}")
                self.cancel_results[request] = {'success': True, 'field': field}
            else:
                print("⚠ 撤单响应为空")
                self.cancel_results[request] = {'success': False, 'error': '响应为空'}
    
    def on_rsp_batch_order(self, request, error, field):
        """批量下单响应回调"""
        print("\n[批量下单响应]")
        if error and error.get('ErrorId', 0) != 0:
            print(f"❌ 批量下单失败: {error.get('ErrorInfo', '未知错误')}")
        else:
            if field:
                total_count = field.get('TotalCount', 0)
                print(f"✓ 批量下单成功，总订单数: {total_count}")
    
    def _format_acct_type(self, acct_type: str) -> str:
        """格式化账户类型"""
        type_map = {
            '0': '现货',
            '1': '期权',
            '2': '期货',
            '3': '信用交易'
        }
        return type_map.get(acct_type, f'未知({acct_type})')
    
    def _format_board(self, board_id: str) -> str:
        """格式化交易板块"""
        board_map = {
            BOARD_SH: '上海',
            BOARD_SZ: '深圳'
        }
        return board_map.get(board_id, f'未知({board_id})')
    
    def _format_order_state(self, order_state: str) -> str:
        """格式化委托状态"""
        state_map = {
            '0': '未报',
            '1': '正报',
            '2': '已报',
            '3': '已报撤单',
            '4': '部成待撤',
            '5': '部成部分撤',
            '6': '已撤',
            '7': '部成成交',
            '8': '已成交',
            '9': '废单',
            'A': '报盘等待',
            'B': '报盘确认'
        }
        return state_map.get(order_state, f'未知({order_state})')


def load_config(config_path: Optional[str] = None) -> Dict:
    """从配置文件加载账户信息
    
    Args:
        config_path: 配置文件路径，如果为 None 则自动查找
        
    Returns:
        配置字典，包含账户信息
    """
    if config_path is None:
        # 自动查找配置文件
        current_dir = Path(__file__).parent.parent.parent
        config_path = current_dir / 'bin' / 'config' / 'config.ini'
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    
    if 'user' not in config:
        return {}
    
    user_config = config['user']
    
    return {
        'account': user_config.get('acct', ''),
        'password': user_config.get('password', ''),
        'acct_type': user_config.get('acct_type', '0'),
        'sh_trade_account': user_config.get('sh_trade_account', ''),
        'sz_trade_account': user_config.get('sz_trade_account', ''),
    }


def get_account_type(acct_type_str: str) -> AccountType:
    """将字符串转换为账户类型"""
    type_map = {
        '0': AccountType.STOCK,
        '1': AccountType.OPTION,
        '2': AccountType.FUTURE,
        '3': AccountType.CREDIT
    }
    return type_map.get(acct_type_str, AccountType.STOCK)


def input_account_info() -> Dict:
    """手动输入账户信息"""
    print("\n" + "=" * 60)
    print("请输入账户信息")
    print("=" * 60)
    
    account = input("资金账号: ").strip()
    password = input("密码: ").strip()
    
    print("\n账户类型:")
    print("  0 - 现货")
    print("  1 - 期权")
    print("  2 - 期货")
    print("  3 - 信用交易")
    acct_type_str = input("请选择账户类型 (默认 0): ").strip() or '0'
    
    sh_trade_account = input("上海股东账号 (可选): ").strip()
    sz_trade_account = input("深圳股东账号 (可选): ").strip()
    
    return {
        'account': account,
        'password': password,
        'acct_type': acct_type_str,
        'sh_trade_account': sh_trade_account,
        'sz_trade_account': sz_trade_account,
    }


def input_order_info(default_trdacct_sh: str = '', default_trdacct_sz: str = '') -> Dict:
    """输入下单信息"""
    print("\n" + "=" * 60)
    print("请输入下单信息")
    print("=" * 60)
    
    # 选择交易方向
    print("\n交易方向:")
    print("  1 - 买入")
    print("  2 - 卖出")
    direction = input("请选择交易方向 (1/2): ").strip()
    stk_biz = STK_BIZ_BUY if direction == '1' else STK_BIZ_SELL
    direction_name = "买入" if direction == '1' else "卖出"
    
    # 选择交易板块
    print("\n交易板块:")
    print("  1 - 上海 (600xxx, 688xxx)")
    print("  2 - 深圳 (000xxx, 001xxx, 002xxx, 300xxx)")
    board_choice = input("请选择交易板块 (1/2): ").strip()
    board_id = BOARD_SH if board_choice == '1' else BOARD_SZ
    board_name = "上海" if board_choice == '1' else "深圳"
    
    # 根据板块选择股东账号
    if board_id == BOARD_SH:
        trdacct = input(f"上海股东账号 (默认: {default_trdacct_sh}): ").strip() or default_trdacct_sh
    else:
        trdacct = input(f"深圳股东账号 (默认: {default_trdacct_sz}): ").strip() or default_trdacct_sz
    
    symbol = input("证券代码 (如 600000): ").strip()
    
    # 选择委托类型
    print("\n委托类型:")
    print("  1 - 限价单")
    print("  2 - 市价单")
    order_type = input("请选择委托类型 (1/2, 默认 1): ").strip() or '1'
    stk_biz_action = ORDER_TYPE_LIMIT if order_type == '1' else ORDER_TYPE_MKT
    
    price = 0.0
    if order_type == '1':
        price_str = input("委托价格 (元): ").strip()
        try:
            price = float(price_str)
        except ValueError:
            print("⚠ 价格格式错误，使用 0")
            price = 0.0
    else:
        print("市价单价格自动设为 0")
    
    quantity_str = input("委托数量 (股): ").strip()
    try:
        quantity = int(quantity_str)
    except ValueError:
        print("⚠ 数量格式错误，使用 100")
        quantity = 100
    
    order_ref = input("客户委托信息 (可选): ").strip()
    
    print("\n下单信息确认:")
    print(f"  交易方向: {direction_name}")
    print(f"  交易板块: {board_name}")
    print(f"  股东账号: {trdacct}")
    print(f"  证券代码: {symbol}")
    print(f"  委托类型: {'限价单' if order_type == '1' else '市价单'}")
    if order_type == '1':
        print(f"  委托价格: {price} 元")
    print(f"  委托数量: {quantity} 股")
    if order_ref:
        print(f"  委托信息: {order_ref}")
    
    confirm = input("\n确认下单? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消下单")
        return None
    
    return {
        'trdacct': trdacct,
        'board_id': board_id,
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'stk_biz': stk_biz,
        'stk_biz_action': stk_biz_action,
        'order_ref': order_ref,
    }


def real_trading():
    """真实交易主函数"""
    print("=" * 60)
    print("真实股票交易系统")
    print("=" * 60)
    print("\n⚠ 警告: 这是一个真实的交易系统!")
    print("   请确保您了解交易风险，谨慎操作!")
    print("   建议先在模拟环境中测试!")
    
    confirm = input("\n确认继续? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消操作")
        return
    
    # 加载配置
    print("\n" + "-" * 60)
    print("加载配置")
    print("-" * 60)
    
    config = load_config()
    use_config = False
    
    if config and config.get('account') and config.get('password'):
        print("发现配置文件，包含账户信息")
        use_config_file = input("使用配置文件中的账户信息? (y/n): ").strip().lower()
        if use_config_file != 'y':
            config = input_account_info()
        else:
            use_config = True
    else:
        print("未找到配置文件或配置不完整")
        config = input_account_info()
    
    # 创建 API 和 SPI
    api = OXTradeApi()
    spi = RealTradingSpi()
    
    try:
        # 初始化 API
        print("\n" + "-" * 60)
        print("初始化 API")
        print("-" * 60)
        api.init()
        print("✓ API 初始化成功")
        
        # 注册回调接口
        api.register_spi(spi)
        print("✓ 回调接口注册成功")
        
        # 登录
        print("\n" + "-" * 60)
        print("登录账户")
        print("-" * 60)
        
        account = config['account']
        password = config['password']
        account_type = get_account_type(config['acct_type'])
        
        login_event = threading.Event()
        spi.set_login_event(login_event)
        
        api.login(account, password, account_type, timeout=30.0)
        
        # 等待登录回调
        if login_event.wait(timeout=30.0):
            if not spi.login_success:
                print(f"\n❌ 登录失败: {spi.login_error or '未知错误'}")
                return
        else:
            print("\n❌ 登录超时")
            return
        
        print("\n✓ 登录成功，可以开始交易")
        
        # 交易循环
        while True:
            print("\n" + "=" * 60)
            print("交易菜单")
            print("=" * 60)
            print("  1 - 下单")
            print("  2 - 撤单")
            print("  3 - 查看订单")
            print("  4 - 退出")
            
            choice = input("\n请选择操作 (1-4): ").strip()
            
            if choice == '1':
                # 下单
                order_info = input_order_info(
                    config.get('sh_trade_account', ''),
                    config.get('sz_trade_account', '')
                )
                
                if order_info:
                    try:
                        request_id = api.order(
                            trdacct=order_info['trdacct'],
                            board_id=order_info['board_id'],
                            symbol=order_info['symbol'],
                            price=order_info['price'],
                            quantity=order_info['quantity'],
                            stk_biz=order_info['stk_biz'],
                            stk_biz_action=order_info['stk_biz_action'],
                            order_ref=order_info['order_ref']
                        )
                        print(f"\n✓ 下单请求已发送，请求编号: {request_id}")
                        print("   等待委托回报...")
                        time.sleep(1.0)  # 等待回报
                    except OXOrderError as e:
                        print(f"\n❌ 下单失败: {e}")
                    except Exception as e:
                        print(f"\n❌ 错误: {e}")
            
            elif choice == '2':
                # 撤单
                board_id = input("交易板块 (10-上海, 00-深圳): ").strip()
                order_no_str = input("委托编号: ").strip()
                try:
                    order_no = int(order_no_str)
                    request_id = api.cancel(board_id, order_no)
                    print(f"\n✓ 撤单请求已发送，请求编号: {request_id}")
                    print("   等待撤单响应...")
                    time.sleep(1.0)  # 等待响应
                except ValueError:
                    print("\n❌ 委托编号格式错误")
                except OXOrderError as e:
                    print(f"\n❌ 撤单失败: {e}")
                except Exception as e:
                    print(f"\n❌ 错误: {e}")
            
            elif choice == '3':
                # 查看订单
                print("\n" + "-" * 60)
                print("订单列表")
                print("-" * 60)
                if spi.orders:
                    for order_no, order_info in spi.orders.items():
                        print(f"\n委托编号: {order_no}")
                        print(f"  证券代码: {order_info.get('Symbol', '')}")
                        print(f"  委托数量: {order_info.get('OrderQty', 0)} 股")
                        print(f"  委托价格: {order_info.get('OrderPrice', '0')} 元")
                        print(f"  委托状态: {order_info.get('OrderState', '')}")
                else:
                    print("暂无订单")
                
                if spi.filled_orders:
                    print("\n成交订单:")
                    for filled in spi.filled_orders:
                        print(f"\n委托编号: {filled.get('OrderNo', '')}")
                        print(f"  证券代码: {filled.get('Symbol', '')}")
                        print(f"  成交数量: {filled.get('FilledQty', 0)} 股")
                        print(f"  成交价格: {filled.get('FilledPrice', '0')} 元")
            
            elif choice == '4':
                # 退出
                print("\n正在退出...")
                break
            
            else:
                print("\n⚠ 无效选择，请重试")
    
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
        api.stop()
        print("✓ API 已停止")
        print("\n感谢使用!")


if __name__ == "__main__":
    real_trading()

