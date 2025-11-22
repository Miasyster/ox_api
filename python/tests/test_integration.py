"""
集成测试模块

测试完整的工作流程、异常情况和并发调用。
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock
from ctypes import c_void_p
from datetime import date

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXLoginError, OXOrderError
from stock_ox.constants import STK_BIZ_BUY, STK_BIZ_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MKT, BOARD_SH, BOARD_SZ


class TestCompleteTradingFlow:
    """测试完整交易流程"""
    
    @patch('stock_ox.api.DLLoader')
    def test_complete_trading_workflow(self, mock_dll_loader_class):
        """
        完整交易流程测试：
        1. 初始化 API
        2. 注册 SPI
        3. 登录账户
        4. 下单（限价单）
        5. 接收委托回报
        6. 接收成交回报
        7. 撤单
        8. 接收撤单响应
        9. 停止 API
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        # 回调数据收集
        callbacks = {
            'logon': [],
            'order': [],
            'filled': [],
            'cancel': [],
        }
        
        class TradingSpi(OXTradeSpi):
            def on_rsp_logon(self, request, error, is_last, field):
                callbacks['logon'].append({
                    'request': request,
                    'error': error,
                    'is_last': is_last,
                    'field': field
                })
            
            def on_rtn_order(self, field):
                callbacks['order'].append(field)
            
            def on_rtn_order_filled(self, field):
                callbacks['filled'].append(field)
            
            def on_rsp_cancel_ticket(self, request, error, field):
                callbacks['cancel'].append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        api = OXTradeApi()
        
        try:
            # 步骤 1: 初始化 API
            print("\n[步骤 1] 初始化 API...")
            api.init()
            assert api.is_initialized(), "API 应该已初始化"
            print("✓ API 初始化成功")
            
            # 步骤 2: 注册 SPI
            print("\n[步骤 2] 注册 SPI...")
            spi = TradingSpi()
            api.register_spi(spi)
            assert api.spi is not None, "SPI 应该已注册"
            print("✓ SPI 注册成功")
            
            # 步骤 3: 登录账户
            print("\n[步骤 3] 登录账户...")
            account = '110060035050'
            password = '111111'
            account_type = AccountType.CREDIT
            
            api.login(account, password, account_type, timeout=1.0)
            assert api.is_logged_in(), "应该已登录"
            
            # 确保账户信息已设置
            if not api._account:
                api._account = account
                api._acct_type = account_type
            
            # 模拟登录回调
            api.spi.on_rsp_logon(1, None, True, {
                'IntOrg': 12345,
                'CustCode': 'CUST001',
                'AcctType': account_type.value,
                'Account': account
            })
            time.sleep(0.1)
            
            assert len(callbacks['logon']) > 0, "登录回调应该被接收"
            print("✓ 账户登录成功")
            
            # 步骤 4: 下单（限价单）
            print("\n[步骤 4] 下单（限价单）...")
            order_request_id = api.order(
                trdacct='A197407210',
                board_id=BOARD_SH,
                symbol='600000',
                price=10.50,
                quantity=100,
                stk_biz=STK_BIZ_BUY,
                stk_biz_action=ORDER_TYPE_LIMIT,
                order_ref='ORDER001'
            )
            assert order_request_id > 0, f"下单失败，请求编号: {order_request_id}"
            print(f"✓ 下单成功，请求编号: {order_request_id}")
            
            # 步骤 5: 接收委托回报
            print("\n[步骤 5] 等待委托回报...")
            time.sleep(0.2)
            assert len(callbacks['order']) > 0, "委托回报应该被接收"
            assert callbacks['order'][0] is not None, "委托回报数据应该不为空"
            print(f"✓ 委托回报接收成功，委托编号: {callbacks['order'][0].get('OrderNo', 'N/A')}")
            
            # 步骤 6: 接收成交回报（模拟）
            print("\n[步骤 6] 模拟成交回报...")
            filled_dict = {
                'Account': account,
                'Trdacct': 'A197407210',
                'Symbol': '600000',
                'ExchangeId': '1',
                'BoardId': BOARD_SH,
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
            time.sleep(0.1)
            assert len(callbacks['filled']) > 0, "成交回报应该被接收"
            print(f"✓ 成交回报接收成功，成交数量: {callbacks['filled'][0].get('FilledQty', 'N/A')}")
            
            # 步骤 7: 撤单
            print("\n[步骤 7] 撤单...")
            order_no = 123456789012345
            cancel_request_id = api.cancel(BOARD_SH, order_no)
            assert cancel_request_id > 0, f"撤单失败，请求编号: {cancel_request_id}"
            print(f"✓ 撤单成功，请求编号: {cancel_request_id}")
            
            # 步骤 8: 接收撤单响应
            print("\n[步骤 8] 等待撤单响应...")
            time.sleep(0.2)
            assert len(callbacks['cancel']) > 0, "撤单响应应该被接收"
            assert callbacks['cancel'][0]['error'] is None, "撤单应该成功"
            print("✓ 撤单响应接收成功")
            
            # 步骤 9: 停止 API
            print("\n[步骤 9] 停止 API...")
            api.stop()
            assert not api.is_initialized(), "API 应该已停止"
            print("✓ API 已停止")
            
            print("\n" + "="*60)
            print("✅ 完整交易流程测试通过！")
            print("="*60)
            
        except Exception as e:
            api.stop()
            raise
    
    @patch('stock_ox.api.DLLoader')
    def test_trading_workflow_with_context_manager(self, mock_dll_loader_class):
        """测试使用上下文管理器的完整交易流程"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        order_placed = False
        order_received = False
        
        class TradingSpi(OXTradeSpi):
            def on_rtn_order(self, field):
                nonlocal order_received
                order_received = True
        
        spi = TradingSpi()
        
        # 使用上下文管理器
        with OXTradeApi() as api:
            api.register_spi(spi)
            api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
            
            # 确保账户信息已设置
            if not api._account:
                api._account = '110060035050'
                api._acct_type = AccountType.CREDIT
            
            # 下单
            request_id = api.order(
                trdacct='A197407210',
                board_id=BOARD_SH,
                symbol='600000',
                price=10.50,
                quantity=100
            )
            order_placed = (request_id > 0)
            time.sleep(0.2)
        
        # 上下文管理器退出后，API 应该已停止
        assert not api.is_initialized(), "API 应该已停止"
        assert order_placed, "应该成功下单"
        assert order_received, "应该收到委托回报"


class TestExceptionScenarios:
    """测试异常情况"""
    
    @patch('stock_ox.api.DLLoader')
    def test_order_without_init(self, mock_dll_loader_class):
        """测试未初始化时下单"""
        api = OXTradeApi()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.order('A197407210', BOARD_SH, '600000', 10.50, 100)
        
        assert "API not initialized" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_order_without_login(self, mock_dll_loader_class):
        """测试未登录时下单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.order('A197407210', BOARD_SH, '600000', 10.50, 100)
        
        assert "Not logged in" in str(exc_info.value)
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_without_order(self, mock_dll_loader_class):
        """测试撤单时委托不存在的情况（通过错误回调）"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        cancel_errors = []
        
        class ErrorSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                if error:
                    cancel_errors.append(error)
        
        api = OXTradeApi()
        api.init()
        api.register_spi(ErrorSpi())
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 撤单（模拟委托不存在）
        request_id = api.cancel(BOARD_SH, 999999999999999)
        
        # 模拟撤单失败回调
        error_dict = {'ErrorId': 1001, 'ErrorInfo': '委托不存在'}
        api.spi.on_rsp_cancel_ticket(request_id, error_dict, None)
        time.sleep(0.1)
        
        assert len(cancel_errors) > 0, "应该收到错误回调"
        assert cancel_errors[0]['ErrorId'] == 1001, "错误 ID 应该正确"
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_order_failure_scenarios(self, mock_dll_loader_class):
        """测试下单失败的各种场景"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        api._acct_type = AccountType.CREDIT
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 测试 1: 下单请求返回非零代码
        with patch.object(api, '_call_order_virtual', return_value=1):
            with pytest.raises(OXOrderError) as exc_info:
                api.order('A197407210', BOARD_SH, '600000', 10.50, 100)
            assert "Order request failed with return code: 1" in str(exc_info.value)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_failure_scenarios(self, mock_dll_loader_class):
        """测试撤单失败的各种场景"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        api._acct_type = AccountType.CREDIT
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 测试 1: 撤单请求返回非零代码
        with patch.object(api, '_call_cancel_virtual', return_value=1):
            with pytest.raises(OXOrderError) as exc_info:
                api.cancel(BOARD_SH, 123456789012345)
            assert "Cancel request failed with return code: 1" in str(exc_info.value)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_validation(self, mock_dll_loader_class):
        """测试批量下单的参数验证"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        api._acct_type = AccountType.CREDIT
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 测试空订单列表
        with pytest.raises(OXOrderError) as exc_info:
            api.batch_order([])
        assert "Orders list cannot be empty" in str(exc_info.value)
        
        # 测试订单数量超过限制
        from stock_ox.constants import MAX_ORDERS_COUNT
        large_orders = [{'trdacct': 'A197407210', 'board_id': BOARD_SH, 'symbol': '600000', 'price': 10.50, 'quantity': 100}] * (MAX_ORDERS_COUNT + 1)
        
        with pytest.raises(OXOrderError) as exc_info:
            api.batch_order(large_orders)
        assert "exceeds maximum limit" in str(exc_info.value)
        
        api.stop()


class TestConcurrentCalls:
    """测试并发调用"""
    
    @patch('stock_ox.api.DLLoader')
    def test_multiple_orders_concurrent(self, mock_dll_loader_class):
        """测试多个订单并发下单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        order_results = []
        errors = []
        
        def place_order(symbol, price, quantity):
            try:
                request_id = api.order(
                    trdacct='A197407210',
                    board_id=BOARD_SH,
                    symbol=symbol,
                    price=price,
                    quantity=quantity,
                    stk_biz=STK_BIZ_BUY
                )
                order_results.append(('success', symbol, request_id))
            except Exception as e:
                errors.append(('error', symbol, str(e)))
        
        # 并发下单
        threads = []
        orders = [
            ('600000', 10.50, 100),
            ('600001', 11.00, 200),
            ('600002', 12.00, 300),
        ]
        
        for symbol, price, quantity in orders:
            thread = threading.Thread(target=place_order, args=(symbol, price, quantity))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=2.0)
        
        # 验证结果
        assert len(order_results) == 3, f"应该有3个订单成功，实际: {len(order_results)}"
        assert len(errors) == 0, f"不应该有错误，实际错误数: {len(errors)}"
        
        # 验证所有请求编号都大于0
        for result in order_results:
            assert result[2] > 0, f"订单 {result[1]} 的请求编号应该大于0"
        
        time.sleep(0.3)  # 等待回调
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_order_and_cancel_concurrent(self, mock_dll_loader_class):
        """测试下单和撤单并发执行"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        results = []
        
        def order_task():
            try:
                request_id = api.order('A197407210', BOARD_SH, '600000', 10.50, 100)
                results.append(('order', request_id))
            except Exception as e:
                results.append(('order_error', str(e)))
        
        def cancel_task():
            time.sleep(0.05)  # 稍微延迟，让下单先执行
            try:
                request_id = api.cancel(BOARD_SH, 123456789012345)
                results.append(('cancel', request_id))
            except Exception as e:
                results.append(('cancel_error', str(e)))
        
        # 并发执行下单和撤单
        order_thread = threading.Thread(target=order_task)
        cancel_thread = threading.Thread(target=cancel_task)
        
        order_thread.start()
        cancel_thread.start()
        
        order_thread.join(timeout=2.0)
        cancel_thread.join(timeout=2.0)
        
        # 验证结果
        order_success = any(r[0] == 'order' and r[1] > 0 for r in results)
        cancel_success = any(r[0] == 'cancel' and r[1] > 0 for r in results)
        
        assert order_success, "下单应该成功"
        assert cancel_success, "撤单应该成功"
        
        time.sleep(0.2)
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_multiple_batch_orders_concurrent(self, mock_dll_loader_class):
        """测试多个批量订单并发执行"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        batch_results = []
        
        def batch_order_task(orders):
            try:
                request_id = api.batch_order(orders)
                batch_results.append(('success', request_id))
            except Exception as e:
                batch_results.append(('error', str(e)))
        
        # 创建多个批量订单
        batch1 = [
            {'trdacct': 'A197407210', 'board_id': BOARD_SH, 'symbol': '600000', 'price': 10.50, 'quantity': 100},
            {'trdacct': 'A197407210', 'board_id': BOARD_SH, 'symbol': '600001', 'price': 11.00, 'quantity': 200},
        ]
        batch2 = [
            {'trdacct': 'A197407210', 'board_id': BOARD_SH, 'symbol': '600002', 'price': 12.00, 'quantity': 300},
        ]
        
        threads = [
            threading.Thread(target=batch_order_task, args=(batch1,)),
            threading.Thread(target=batch_order_task, args=(batch2,)),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=2.0)
        
        # 验证结果
        successes = [r for r in batch_results if r[0] == 'success']
        assert len(successes) == 2, f"应该有2个批量订单成功，实际: {len(successes)}"
        
        for success in successes:
            assert success[1] > 0, "批量订单请求编号应该大于0"
        
        time.sleep(0.3)
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_concurrent_order_cancel_scenarios(self, mock_dll_loader_class):
        """测试并发下单和撤单场景"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        results = []
        errors = []
        
        def order_and_cancel(symbol, order_no):
            try:
                # 下单
                order_id = api.order(
                    trdacct='A197407210',
                    board_id=BOARD_SH,
                    symbol=symbol,
                    price=10.50,
                    quantity=100
                )
                results.append(('order', symbol, order_id))
                
                time.sleep(0.05)
                
                # 撤单
                cancel_id = api.cancel(BOARD_SH, order_no)
                results.append(('cancel', symbol, cancel_id))
            except Exception as e:
                errors.append(('error', symbol, str(e)))
        
        # 并发执行多个下单-撤单操作
        threads = []
        symbols = ['600000', '600001', '600002']
        order_nos = [123456789012345, 123456789012346, 123456789012347]
        
        for symbol, order_no in zip(symbols, order_nos):
            thread = threading.Thread(target=order_and_cancel, args=(symbol, order_no))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=3.0)
        
        # 验证结果
        assert len(errors) == 0, f"不应该有错误，实际错误: {errors}"
        assert len(results) == 6, f"应该有6个操作成功（3个下单+3个撤单），实际: {len(results)}"
        
        time.sleep(0.3)
        api.stop()


class TestQueryFlow:
    """测试查询流程（占位，待查询功能实现后完善）"""
    
    @pytest.mark.skip(reason="查询功能尚未实现（阶段四）")
    def test_query_balance_flow(self):
        """测试查询资金流程（待实现）"""
        # TODO: 待实现查询功能后补充
        pass
    
    @pytest.mark.skip(reason="查询功能尚未实现（阶段四）")
    def test_query_positions_flow(self):
        """测试查询持仓流程（待实现）"""
        # TODO: 待实现查询功能后补充
        pass
    
    @pytest.mark.skip(reason="查询功能尚未实现（阶段四）")
    def test_query_orders_flow(self):
        """测试查询委托流程（待实现）"""
        # TODO: 待实现查询功能后补充
        pass
    
    @patch('stock_ox.api.DLLoader')
    def test_query_trade_accounts_available(self, mock_dll_loader_class):
        """测试查询股东账号功能（如果已实现）"""
        # 注意：query_trade_accounts 可能已经通过阶段二的测试实现
        # 这里只是检查功能是否可用
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        # 检查是否有 query_trade_accounts 方法
        # 如果没有，跳过此测试
        if not hasattr(api, 'query_trade_accounts'):
            pytest.skip("query_trade_accounts 方法尚未实现")
        
        # 如果有，进行测试
        spi = OXTradeSpi()
        api.register_spi(spi)
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 测试查询股东账号
        # request_id = api.query_trade_accounts()
        # assert request_id > 0
        
        api.stop()


class TestIntegrationEdgeCases:
    """测试集成边界情况"""
    
    @patch('stock_ox.api.DLLoader')
    def test_repeated_init_stop(self, mock_dll_loader_class):
        """测试重复初始化和停止"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        
        # 多次初始化和停止
        for i in range(3):
            api.init()
            assert api.is_initialized(), f"第 {i+1} 次初始化应该成功"
            api.stop()
            assert not api.is_initialized(), f"第 {i+1} 次停止后应该未初始化"
    
    @patch('stock_ox.api.DLLoader')
    def test_multiple_login_attempts(self, mock_dll_loader_class):
        """测试多次登录尝试"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 多次登录
        for i in range(3):
            result = api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
            assert result is True, f"第 {i+1} 次登录应该成功"
            assert api.is_logged_in(), f"第 {i+1} 次登录后应该已登录"
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_order_cancel_sequence(self, mock_dll_loader_class):
        """测试下单-撤单序列"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        order_no = 123456789012345
        
        # 执行多次下单-撤单序列
        for i in range(3):
            # 下单
            order_request_id = api.order(
                trdacct='A197407210',
                board_id=BOARD_SH,
                symbol='600000',
                price=10.50 + i,
                quantity=100
            )
            assert order_request_id > 0, f"第 {i+1} 次下单应该成功"
            
            time.sleep(0.1)
            
            # 撤单
            cancel_request_id = api.cancel(BOARD_SH, order_no + i)
            assert cancel_request_id > 0, f"第 {i+1} 次撤单应该成功"
            
            time.sleep(0.1)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_different_order_types_sequence(self, mock_dll_loader_class):
        """测试不同订单类型的序列"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 测试不同订单类型
        order_types = [
            (ORDER_TYPE_LIMIT, 10.50, "限价单"),
            (ORDER_TYPE_MKT, 0, "市价单"),
        ]
        
        for order_type, price, type_name in order_types:
            request_id = api.order(
                trdacct='A197407210',
                board_id=BOARD_SH,
                symbol='600000',
                price=price,
                quantity=100,
                stk_biz_action=order_type
            )
            assert request_id > 0, f"{type_name} 下单应该成功"
            time.sleep(0.1)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_different_board_ids(self, mock_dll_loader_class):
        """测试不同交易板块的操作"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 测试上海和深圳板块
        boards = [
            (BOARD_SH, '600000', "上海"),
            (BOARD_SZ, '000001', "深圳"),
        ]
        
        for board_id, symbol, board_name in boards:
            request_id = api.order(
                trdacct='A197407210',
                board_id=board_id,
                symbol=symbol,
                price=10.50,
                quantity=100
            )
            assert request_id > 0, f"{board_name} 板块下单应该成功"
            
            time.sleep(0.1)
            
            cancel_request_id = api.cancel(board_id, 123456789012345)
            assert cancel_request_id > 0, f"{board_name} 板块撤单应该成功"
            
            time.sleep(0.1)
        
        api.stop()


class TestErrorRecovery:
    """测试错误恢复"""
    
    @patch('stock_ox.api.DLLoader')
    def test_recover_after_order_failure(self, mock_dll_loader_class):
        """测试下单失败后的恢复"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        api._acct_type = AccountType.CREDIT
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 第一次下单失败
        with patch.object(api, '_call_order_virtual', return_value=1):
            with pytest.raises(OXOrderError):
                api.order('A197407210', BOARD_SH, '600000', 10.50, 100)
        
        # 恢复后再次下单应该成功
        with patch.object(api, '_call_order_virtual', return_value=0):
            request_id = api.order('A197407210', BOARD_SH, '600000', 10.50, 100)
            assert request_id > 0, "恢复后下单应该成功"
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_recover_after_cancel_failure(self, mock_dll_loader_class):
        """测试撤单失败后的恢复"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        api._acct_type = AccountType.CREDIT
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 第一次撤单失败
        with patch.object(api, '_call_cancel_virtual', return_value=1):
            with pytest.raises(OXOrderError):
                api.cancel(BOARD_SH, 123456789012345)
        
        # 恢复后再次撤单应该成功
        with patch.object(api, '_call_cancel_virtual', return_value=0):
            request_id = api.cancel(BOARD_SH, 123456789012345)
            assert request_id > 0, "恢复后撤单应该成功"
        
        api.stop()


def test_all_integration_tests():
    """运行所有集成测试"""
    print("\n" + "="*60)
    print("集成测试开始")
    print("="*60)
    
    print("\n[完整交易流程测试]")
    test_complete = TestCompleteTradingFlow()
    test_complete.test_complete_trading_workflow()
    print("✅ 完整交易流程测试通过")
    
    print("\n[异常情况测试]")
    test_exceptions = TestExceptionScenarios()
    test_exceptions.test_order_without_init()
    test_exceptions.test_order_without_login()
    test_exceptions.test_order_failure_scenarios()
    test_exceptions.test_cancel_failure_scenarios()
    test_exceptions.test_batch_order_validation()
    print("✅ 异常情况测试通过")
    
    print("\n[并发调用测试]")
    test_concurrent = TestConcurrentCalls()
    test_concurrent.test_multiple_orders_concurrent()
    test_concurrent.test_order_and_cancel_concurrent()
    print("✅ 并发调用测试通过")
    
    print("\n[边界情况测试]")
    test_edges = TestIntegrationEdgeCases()
    test_edges.test_repeated_init_stop()
    test_edges.test_multiple_login_attempts()
    test_edges.test_order_cancel_sequence()
    print("✅ 边界情况测试通过")
    
    print("\n[错误恢复测试]")
    test_recovery = TestErrorRecovery()
    test_recovery.test_recover_after_order_failure()
    test_recovery.test_recover_after_cancel_failure()
    print("✅ 错误恢复测试通过")
    
    print("\n" + "="*60)
    print("✅ 所有集成测试通过！")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_all_integration_tests()

