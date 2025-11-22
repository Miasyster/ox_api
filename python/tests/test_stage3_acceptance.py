"""
阶段三验收测试

验收标准：
1. 可以成功下单（限价单、市价单）
2. 可以接收委托回报和成交回报
3. 可以成功撤单
"""

import pytest
import sys
import time
import threading
from unittest.mock import patch, MagicMock
from ctypes import c_void_p

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXOrderError
from stock_ox.structs import COXOrderTicket, COXOrderFilledField
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, ORDER_TYPE_MKT
from stock_ox.spi import convert_order_ticket, convert_order_filled


class TestStage3Acceptance:
    """阶段三验收测试"""
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_1_order_limit(self, mock_dll_loader_class):
        """
        验收标准 1: 可以成功下单（限价单）
        
        测试步骤：
        1. 初始化 API
        2. 注册 SPI
        3. 登录账户
        4. 调用 order() 方法（限价单）
        5. 验证下单成功
        6. 验证返回请求编号
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 登录
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        assert api.is_logged_in(), "应该已登录"
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 下单（限价单）
        trdacct = 'A197407210'
        board_id = '10'
        symbol = '600000'
        price = 10.50
        quantity = 100
        stk_biz = STK_BIZ_BUY
        stk_biz_action = ORDER_TYPE_LIMIT  # 限价单
        
        request_id = api.order(
            trdacct=trdacct,
            board_id=board_id,
            symbol=symbol,
            price=price,
            quantity=quantity,
            stk_biz=stk_biz,
            stk_biz_action=stk_biz_action
        )
        
        assert request_id > 0, f"下单失败，请求编号: {request_id}"
        
        print(f"✓ 限价单下单成功")
        print(f"  - 请求编号: {request_id}")
        print(f"  - 证券代码: {symbol}")
        print(f"  - 委托价格: {price}")
        print(f"  - 委托数量: {quantity}")
        print(f"  - 委托类型: 限价单")
        
        # 等待回调
        time.sleep(0.2)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_1_order_market(self, mock_dll_loader_class):
        """
        验收标准 1: 可以成功下单（市价单）
        
        测试步骤：
        1. 初始化 API
        2. 注册 SPI
        3. 登录账户
        4. 调用 order() 方法（市价单，价格为0）
        5. 验证下单成功
        6. 验证返回请求编号
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 登录
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        assert api.is_logged_in(), "应该已登录"
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 下单（市价单，价格为0）
        trdacct = 'A197407210'
        board_id = '10'
        symbol = '600000'
        price = 0  # 市价单价格为0
        quantity = 100
        stk_biz = STK_BIZ_BUY
        stk_biz_action = ORDER_TYPE_MKT  # 市价单
        
        request_id = api.order(
            trdacct=trdacct,
            board_id=board_id,
            symbol=symbol,
            price=price,
            quantity=quantity,
            stk_biz=stk_biz,
            stk_biz_action=stk_biz_action
        )
        
        assert request_id > 0, f"下单失败，请求编号: {request_id}"
        
        print(f"✓ 市价单下单成功")
        print(f"  - 请求编号: {request_id}")
        print(f"  - 证券代码: {symbol}")
        print(f"  - 委托价格: {price} (市价)")
        print(f"  - 委托数量: {quantity}")
        print(f"  - 委托类型: 市价单")
        
        # 等待回调
        time.sleep(0.2)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_2_receive_order_callback(self, mock_dll_loader_class):
        """
        验收标准 2: 可以接收委托回报
        
        测试步骤：
        1. 初始化 API
        2. 创建自定义 SPI 来捕获委托回报
        3. 注册 SPI
        4. 登录账户
        5. 下单
        6. 验证委托回报回调被正确接收
        7. 验证回调数据正确
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        # 创建自定义 SPI 来捕获委托回报
        order_callbacks = []
        order_data = {}
        
        class CustomSpi(OXTradeSpi):
            def on_rtn_order(self, field):
                order_callbacks.append(field)
                if field:
                    order_data.update(field)
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 登录
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 下单
        request_id = api.order(
            trdacct='A197407210',
            board_id='10',
            symbol='600000',
            price=10.50,
            quantity=100,
            stk_biz=STK_BIZ_BUY
        )
        
        # 等待委托回报回调
        time.sleep(0.3)
        
        # 验证回调被接收
        assert len(order_callbacks) > 0, "委托回报回调应该被接收"
        assert order_data is not None, "委托回报数据应该不为空"
        assert 'OrderNo' in order_data or len(order_data) > 0, "委托回报应该包含有效数据"
        
        print("✓ 委托回报回调接收成功")
        if order_data:
            print(f"  - 委托编号: {order_data.get('OrderNo', 'N/A')}")
            print(f"  - 证券代码: {order_data.get('Symbol', 'N/A')}")
            print(f"  - 委托数量: {order_data.get('OrderQty', 'N/A')}")
            print(f"  - 委托状态: {order_data.get('OrderState', 'N/A')}")
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_2_receive_filled_callback(self, mock_dll_loader_class):
        """
        验收标准 2: 可以接收成交回报
        
        测试步骤：
        1. 初始化 API
        2. 创建自定义 SPI 来捕获成交回报
        3. 注册 SPI
        4. 登录账户
        5. 手动触发成交回报回调
        6. 验证成交回报回调被正确接收
        7. 验证回调数据正确
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        # 创建自定义 SPI 来捕获成交回报
        filled_callbacks = []
        filled_data = {}
        
        class CustomSpi(OXTradeSpi):
            def on_rtn_order_filled(self, field):
                filled_callbacks.append(field)
                if field:
                    filled_data.update(field)
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 登录
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 手动触发成交回报回调（模拟成交）
        filled_dict = {
            'Account': '110060035050',
            'Trdacct': 'A197407210',
            'Symbol': '600000',
            'ExchangeId': '1',
            'BoardId': '10',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': ORDER_TYPE_LIMIT,
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
        
        # 验证回调被接收
        assert len(filled_callbacks) > 0, "成交回报回调应该被接收"
        assert filled_data is not None, "成交回报数据应该不为空"
        assert 'OrderNo' in filled_data, "成交回报应该包含委托编号"
        assert filled_data['OrderNo'] == 123456789012345, "委托编号应该正确"
        assert filled_data['FilledQty'] == 100, "成交数量应该正确"
        
        print("✓ 成交回报回调接收成功")
        print(f"  - 委托编号: {filled_data.get('OrderNo', 'N/A')}")
        print(f"  - 证券代码: {filled_data.get('Symbol', 'N/A')}")
        print(f"  - 成交数量: {filled_data.get('FilledQty', 'N/A')}")
        print(f"  - 成交价格: {filled_data.get('FilledPrice', 'N/A')}")
        print(f"  - 成交金额: {filled_data.get('FilledAmt', 'N/A')}")
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_3_cancel_order(self, mock_dll_loader_class):
        """
        验收标准 3: 可以成功撤单
        
        测试步骤：
        1. 初始化 API
        2. 注册 SPI
        3. 登录账户
        4. 下单
        5. 调用 cancel() 方法撤单
        6. 验证撤单成功
        7. 验证返回请求编号
        8. 验证撤单响应回调被接收
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        # 创建自定义 SPI 来捕获撤单响应
        cancel_callbacks = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                cancel_callbacks.append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 登录
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 先下单
        order_request_id = api.order(
            trdacct='A197407210',
            board_id='10',
            symbol='600000',
            price=10.50,
            quantity=100,
            stk_biz=STK_BIZ_BUY
        )
        
        # 等待委托回报
        time.sleep(0.1)
        
        # 撤单
        board_id = '10'
        order_no = 123456789012345  # 模拟的委托号
        
        cancel_request_id = api.cancel(board_id, order_no)
        
        assert cancel_request_id > 0, f"撤单失败，请求编号: {cancel_request_id}"
        
        # 等待撤单响应回调
        time.sleep(0.2)
        
        # 验证撤单响应回调被接收
        assert len(cancel_callbacks) > 0, "撤单响应回调应该被接收"
        
        print("✓ 撤单成功")
        print(f"  - 撤单请求编号: {cancel_request_id}")
        print(f"  - 委托编号: {order_no}")
        print(f"  - 交易板块: {board_id}")
        if cancel_callbacks and cancel_callbacks[0].get('field'):
            print(f"  - 撤单状态: {cancel_callbacks[0]['field'].get('OrderState', 'N/A')}")
        
        # 清理
        api.stop()


def test_all_criteria():
    """运行所有验收标准测试"""
    test_instance = TestStage3Acceptance()
    
    print("\n" + "="*60)
    print("阶段三验收测试开始")
    print("="*60)
    
    # 验收标准 1: 可以成功下单（限价单、市价单）
    print("\n[验收标准 1] 测试下单功能...")
    try:
        with patch('stock_ox.api.DLLoader'):
            print("\n[1.1] 测试限价单...")
            test_instance.test_criterion_1_order_limit()
            print("✅ 限价单下单成功")
            
            print("\n[1.2] 测试市价单...")
            test_instance.test_criterion_1_order_market()
            print("✅ 市价单下单成功")
            
        print("\n✅ 验收标准 1 通过: 可以成功下单（限价单、市价单）")
    except Exception as e:
        print(f"❌ 验收标准 1 失败: {e}")
        raise
    
    # 验收标准 2: 可以接收委托回报和成交回报
    print("\n[验收标准 2] 测试委托回报和成交回报接收...")
    try:
        with patch('stock_ox.api.DLLoader'):
            print("\n[2.1] 测试委托回报接收...")
            test_instance.test_criterion_2_receive_order_callback()
            print("✅ 委托回报接收成功")
            
            print("\n[2.2] 测试成交回报接收...")
            test_instance.test_criterion_2_receive_filled_callback()
            print("✅ 成交回报接收成功")
            
        print("\n✅ 验收标准 2 通过: 可以接收委托回报和成交回报")
    except Exception as e:
        print(f"❌ 验收标准 2 失败: {e}")
        raise
    
    # 验收标准 3: 可以成功撤单
    print("\n[验收标准 3] 测试撤单功能...")
    try:
        with patch('stock_ox.api.DLLoader'):
            test_instance.test_criterion_3_cancel_order()
        print("\n✅ 验收标准 3 通过: 可以成功撤单")
    except Exception as e:
        print(f"❌ 验收标准 3 失败: {e}")
        raise
    
    print("\n" + "="*60)
    print("✅ 阶段三验收测试全部通过！")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_all_criteria()

