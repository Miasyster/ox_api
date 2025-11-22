"""
批量下单功能测试模块

测试批量下单功能和批量下单响应回调。
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from ctypes import c_void_p

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXLoginError, OXOrderError
from stock_ox.structs import COXOrderItem, COXReqBatchOrderTicketField
from stock_ox.constants import MAX_ORDERS_COUNT, STK_BIZ_BUY


class TestBatchOrderStructures:
    """测试批量下单相关结构体"""
    
    def test_order_item_creation(self):
        """测试订单项结构体创建"""
        item = COXOrderItem.from_dict({
            'Trdacct': 'A197407210',
            'BoardId': '10',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': 100,
            'Symbol': '600000',
            'OrderQty': 100,
            'OrderPrice': 10.50,
            'OrderRef': 'ORDER001',
        })
        
        assert item is not None
        assert item.StkBiz == STK_BIZ_BUY
        assert item.OrderQty == 100
    
    def test_order_item_to_dict(self):
        """测试订单项结构体转字典"""
        item = COXOrderItem.from_dict({
            'Trdacct': 'A197407210',
            'BoardId': '10',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': 100,
            'Symbol': '600000',
            'OrderQty': 100,
            'OrderPrice': 10.50,
        })
        
        item_dict = item.to_dict()
        assert isinstance(item_dict, dict)
        assert item_dict['StkBiz'] == STK_BIZ_BUY
        assert item_dict['OrderQty'] == 100
        assert item_dict['Symbol'] == '600000'
    
    def test_batch_order_request_creation(self):
        """测试批量下单请求结构体创建"""
        orders = [
            {
                'Trdacct': 'A197407210',
                'BoardId': '10',
                'StkBiz': STK_BIZ_BUY,
                'StkBizAction': 100,
                'Symbol': '600000',
                'OrderQty': 100,
                'OrderPrice': 10.50,
            },
            {
                'Trdacct': 'A197407210',
                'BoardId': '10',
                'StkBiz': STK_BIZ_BUY,
                'StkBizAction': 100,
                'Symbol': '600001',
                'OrderQty': 200,
                'OrderPrice': 11.00,
            },
        ]
        
        req = COXReqBatchOrderTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': 100,
            'orderArray': orders,
        })
        
        assert req is not None
        assert req.AcctType == b'0' or req.AcctType == ord('0')
        assert req.TotalCount == 2
        assert req.StkBiz == STK_BIZ_BUY
    
    def test_batch_order_request_to_dict(self):
        """测试批量下单请求结构体转字典"""
        orders = [
            {
                'Trdacct': 'A197407210',
                'BoardId': '10',
                'Symbol': '600000',
                'OrderQty': 100,
                'OrderPrice': 10.50,
            },
        ]
        
        req = COXReqBatchOrderTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': 100,
            'orderArray': orders,
        })
        
        req_dict = req.to_dict()
        assert isinstance(req_dict, dict)
        assert req_dict['TotalCount'] == 1
        assert len(req_dict['orderArray']) == 1
        assert req_dict['orderArray'][0]['Symbol'] == '600000'


class TestBatchOrderAPI:
    """测试批量下单 API"""
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_success(self, mock_dll_loader_class):
        """测试批量下单成功"""
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
        assert api.is_logged_in()
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 批量下单
        orders = [
            {
                'trdacct': 'A197407210',
                'board_id': '10',
                'symbol': '600000',
                'price': 10.50,
                'quantity': 100,
            },
            {
                'trdacct': 'A197407210',
                'board_id': '10',
                'symbol': '600001',
                'price': 11.00,
                'quantity': 200,
            },
        ]
        
        request_id = api.batch_order(orders)
        
        assert request_id > 0
        
        # 等待回调
        time.sleep(0.2)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_with_order_ref(self, mock_dll_loader_class):
        """测试带委托信息的批量下单"""
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
        
        # 批量下单（带委托信息）
        orders = [
            {
                'trdacct': 'A197407210',
                'board_id': '10',
                'symbol': '600000',
                'price': 10.50,
                'quantity': 100,
                'order_ref': 'BATCH_001',
            },
        ]
        
        request_id = api.batch_order(orders)
        assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_empty_list(self, mock_dll_loader_class):
        """测试空订单列表批量下单"""
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
        
        # 空订单列表
        with pytest.raises(OXOrderError) as exc_info:
            api.batch_order([])
        
        assert "Orders list cannot be empty" in str(exc_info.value)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_exceeds_limit(self, mock_dll_loader_class):
        """测试订单数量超过限制"""
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
        
        # 创建超过限制的订单列表
        orders = []
        for i in range(MAX_ORDERS_COUNT + 1):
            orders.append({
                'trdacct': 'A197407210',
                'board_id': '10',
                'symbol': '600000',
                'price': 10.50,
                'quantity': 100,
            })
        
        with pytest.raises(OXOrderError) as exc_info:
            api.batch_order(orders)
        
        assert "exceeds maximum limit" in str(exc_info.value)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_without_init(self, mock_dll_loader_class):
        """测试未初始化时批量下单"""
        api = OXTradeApi()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.batch_order([{'trdacct': 'A197407210', 'board_id': '10', 'symbol': '600000', 'price': 10.50, 'quantity': 100}])
        
        assert "API not initialized" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_without_login(self, mock_dll_loader_class):
        """测试未登录时批量下单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.batch_order([{'trdacct': 'A197407210', 'board_id': '10', 'symbol': '600000', 'price': 10.50, 'quantity': 100}])
        
        assert "Not logged in" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_without_spi(self, mock_dll_loader_class):
        """测试未注册 SPI 时批量下单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True  # 模拟已登录
        
        with pytest.raises(OXOrderError) as exc_info:
            api.batch_order([{'trdacct': 'A197407210', 'board_id': '10', 'symbol': '600000', 'price': 10.50, 'quantity': 100}])
        
        assert "SPI not registered" in str(exc_info.value)


class TestBatchOrderCallback:
    """测试批量下单回调"""
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_callback_received(self, mock_dll_loader_class):
        """测试批量下单响应回调接收"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_batch_order(self, request, error, field):
                callback_received.append({
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
        
        # 批量下单
        orders = [
            {
                'trdacct': 'A197407210',
                'board_id': '10',
                'symbol': '600000',
                'price': 10.50,
                'quantity': 100,
            },
        ]
        
        request_id = api.batch_order(orders)
        
        # 等待回调
        time.sleep(0.2)
        
        assert len(callback_received) > 0
        assert callback_received[0]['request'] == request_id
        assert callback_received[0]['error'] is None
        assert callback_received[0]['field'] is not None
        assert callback_received[0]['field']['TotalCount'] == 1
        assert len(callback_received[0]['field']['orderArray']) == 1
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_callback_with_error(self, mock_dll_loader_class):
        """测试批量下单响应回调（有错误）"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_batch_order(self, request, error, field):
                callback_received.append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发批量下单响应回调（有错误）
        error_dict = {'ErrorId': 1001, 'ErrorInfo': '批量下单失败'}
        field_dict = None
        
        api.spi.on_rsp_batch_order(1, error_dict, field_dict)
        
        assert len(callback_received) > 0
        assert callback_received[0]['error'] is not None
        assert callback_received[0]['error']['ErrorId'] == 1001
        assert callback_received[0]['field'] is None
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_callback_with_spi_wrapper(self, mock_dll_loader_class):
        """测试 SPI 包装类的批量下单回调转发"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_batch_order(self, request, error, field):
                callback_received.append(('batch_order', request, error, field))
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 测试批量下单回调
        error_dict = None
        field_dict = {'TotalCount': 2, 'orderArray': []}
        api.spi.on_rsp_batch_order(1, error_dict, field_dict)
        
        assert len(callback_received) == 1
        assert callback_received[0][0] == 'batch_order'
        assert callback_received[0][1] == 1
        
        api.stop()


class TestBatchOrderErrorHandling:
    """测试批量下单错误处理"""
    
    @patch('stock_ox.api.DLLoader')
    def test_batch_order_failure_return_code(self, mock_dll_loader_class):
        """测试批量下单请求返回非零代码"""
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
        
        orders = [
            {
                'trdacct': 'A197407210',
                'board_id': '10',
                'symbol': '600000',
                'price': 10.50,
                'quantity': 100,
            },
        ]
        
        # 模拟批量下单请求返回非零代码
        with patch.object(api, '_call_batch_order_virtual', return_value=1):
            with pytest.raises(OXOrderError) as exc_info:
                api.batch_order(orders)
            
            assert "Batch order request failed with return code: 1" in str(exc_info.value)
        
        api.stop()

