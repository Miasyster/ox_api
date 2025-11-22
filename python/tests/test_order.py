"""
下单功能测试模块

测试下单功能和委托回报、成交回报回调。
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from ctypes import c_void_p

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXLoginError, OXOrderError
from stock_ox.structs import COXReqOrderTicketField, COXOrderTicket, COXOrderFilledField
from stock_ox.constants import STK_BIZ_BUY, STK_BIZ_SELL


class TestOrderStructures:
    """测试下单相关结构体"""
    
    def test_order_request_creation(self):
        """测试下单请求结构体创建"""
        req = COXReqOrderTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'Trdacct': 'A197407210',
            'BoardId': '10',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': 100,
            'Symbol': '600000',
            'OrderQty': 100,
            'OrderPrice': 10.50,
            'OrderRef': 'ORDER001',
        })
        
        assert req is not None
        assert req.AcctType == b'0' or req.AcctType == ord('0')
        assert req.StkBiz == STK_BIZ_BUY
        assert req.StkBizAction == 100
        assert req.OrderQty == 100
    
    def test_order_request_to_dict(self):
        """测试下单请求结构体转字典"""
        req = COXReqOrderTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'Trdacct': 'A197407210',
            'BoardId': '10',
            'StkBiz': STK_BIZ_BUY,
            'StkBizAction': 100,
            'Symbol': '600000',
            'OrderQty': 100,
            'OrderPrice': 10.50,
        })
        
        req_dict = req.to_dict()
        assert isinstance(req_dict, dict)
        assert req_dict['StkBiz'] == STK_BIZ_BUY
        assert req_dict['OrderQty'] == 100
    
    def test_order_ticket_creation(self):
        """测试委托回报结构体创建"""
        ticket = COXOrderTicket()
        ticket.OrderNo = 123456789012345
        ticket.OrderState = ord('0')
        ticket.OrderQty = 100
        ticket.FilledQty = 50
        ticket.CanceledQty = 0
        
        assert ticket.OrderNo == 123456789012345
        assert ticket.OrderState == b'0' or ticket.OrderState == ord('0')
        assert ticket.OrderQty == 100
    
    def test_order_ticket_to_dict(self):
        """测试委托回报结构体转字典"""
        ticket = COXOrderTicket()
        ticket.OrderNo = 123456789012345
        ticket.OrderState = ord('0')
        ticket.OrderQty = 100
        ticket.FilledQty = 50
        ticket.CanceledQty = 0
        
        ticket_dict = ticket.to_dict()
        assert isinstance(ticket_dict, dict)
        assert ticket_dict['OrderNo'] == 123456789012345
        assert ticket_dict['OrderState'] == '0'
        assert ticket_dict['OrderQty'] == 100
        assert ticket_dict['FilledQty'] == 50
    
    def test_order_filled_creation(self):
        """测试成交回报结构体创建"""
        filled = COXOrderFilledField()
        filled.OrderNo = 123456789012345
        filled.FilledQty = 50
        filled.FilledDate = 20240101
        filled.ErrorId = 0
        
        assert filled.OrderNo == 123456789012345
        assert filled.FilledQty == 50
        assert filled.FilledDate == 20240101
        assert filled.ErrorId == 0
    
    def test_order_filled_to_dict(self):
        """测试成交回报结构体转字典"""
        filled = COXOrderFilledField()
        filled.OrderNo = 123456789012345
        filled.FilledQty = 50
        filled.FilledDate = 20240101
        filled.ErrorId = 0
        
        filled_dict = filled.to_dict()
        assert isinstance(filled_dict, dict)
        assert filled_dict['OrderNo'] == 123456789012345
        assert filled_dict['FilledQty'] == 50
        assert filled_dict['FilledDate'] == 20240101


class TestOrderAPI:
    """测试下单 API"""
    
    @patch('stock_ox.api.DLLoader')
    def test_order_success(self, mock_dll_loader_class):
        """测试下单成功"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 登录（这会设置账户信息）
        api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        assert api.is_logged_in()
        
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
            stk_biz=STK_BIZ_BUY,
            order_ref='ORDER001'
        )
        
        assert request_id > 0
        
        # 等待回调
        time.sleep(0.2)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_order_without_init(self, mock_dll_loader_class):
        """测试未初始化时下单"""
        api = OXTradeApi()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.order('A197407210', '10', '600000', 10.50, 100)
        
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
            api.order('A197407210', '10', '600000', 10.50, 100)
        
        assert "Not logged in" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_order_without_spi(self, mock_dll_loader_class):
        """测试未注册 SPI 时下单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True  # 模拟已登录
        
        with pytest.raises(OXOrderError) as exc_info:
            api.order('A197407210', '10', '600000', 10.50, 100)
        
        assert "SPI not registered" in str(exc_info.value)


class TestOrderCallback:
    """测试下单回调"""
    
    @patch('stock_ox.api.DLLoader')
    def test_order_callback_received(self, mock_dll_loader_class):
        """测试委托回报回调接收"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rtn_order(self, field):
                callback_received.append(field)
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 登录（这会设置账户信息）
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
            quantity=100
        )
        
        # 等待回调
        time.sleep(0.2)
        
        assert len(callback_received) > 0
        assert callback_received[0] is not None
        assert callback_received[0]['OrderNo'] == 123456789012345
        assert callback_received[0]['Symbol'] == '600000'
        assert callback_received[0]['OrderQty'] == 100
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_order_filled_callback_received(self, mock_dll_loader_class):
        """测试成交回报回调接收"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rtn_order_filled(self, field):
                callback_received.append(field)
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发成交回报回调
        filled_dict = {
            'OrderNo': 123456789012345,
            'Symbol': '600000',
            'FilledQty': 50,
            'FilledPrice': '10.50',
            'FilledAmt': '525.00',
            'FilledDate': 20240101,
        }
        
        api.spi.on_rtn_order_filled(filled_dict)
        
        assert len(callback_received) > 0
        assert callback_received[0] is not None
        assert callback_received[0]['OrderNo'] == 123456789012345
        assert callback_received[0]['FilledQty'] == 50
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_order_callback_with_spi_wrapper(self, mock_dll_loader_class):
        """测试 SPI 包装类的回调转发"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rtn_order(self, field):
                callback_received.append(('order', field))
            
            def on_rtn_order_filled(self, field):
                callback_received.append(('filled', field))
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 测试委托回报
        order_dict = {'OrderNo': 123456789012345, 'Symbol': '600000'}
        api.spi.on_rtn_order(order_dict)
        
        # 测试成交回报
        filled_dict = {'OrderNo': 123456789012345, 'FilledQty': 50}
        api.spi.on_rtn_order_filled(filled_dict)
        
        assert len(callback_received) == 2
        assert callback_received[0][0] == 'order'
        assert callback_received[1][0] == 'filled'
        
        api.stop()


class TestOrderErrorHandling:
    """测试下单错误处理"""
    
    @patch('stock_ox.api.DLLoader')
    def test_order_failure_return_code(self, mock_dll_loader_class):
        """测试下单请求返回非零代码"""
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
        
        # 模拟下单请求返回非零代码
        with patch.object(api, '_call_order_virtual', return_value=1):
            with pytest.raises(OXOrderError) as exc_info:
                api.order('A197407210', '10', '600000', 10.50, 100)
            
            assert "Order request failed with return code: 1" in str(exc_info.value)
        
        api.stop()

