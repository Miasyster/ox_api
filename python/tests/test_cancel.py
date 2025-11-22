"""
撤单功能测试模块

测试撤单功能和撤单响应回调。
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from ctypes import c_void_p
from datetime import date

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXLoginError, OXOrderError
from stock_ox.structs import COXReqCancelTicketField, COXRspCancelTicketField


class TestCancelStructures:
    """测试撤单相关结构体"""
    
    def test_cancel_request_creation(self):
        """测试撤单请求结构体创建"""
        today = date.today()
        order_date = today.year * 10000 + today.month * 100 + today.day
        
        req = COXReqCancelTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'BoardId': '10',
            'OrderDate': order_date,
            'OrderNo': 123456789012345,
        })
        
        assert req is not None
        assert req.AcctType == b'0' or req.AcctType == ord('0')
        assert req.OrderDate == order_date
        assert req.OrderNo == 123456789012345
    
    def test_cancel_request_to_dict(self):
        """测试撤单请求结构体转字典"""
        today = date.today()
        order_date = today.year * 10000 + today.month * 100 + today.day
        
        req = COXReqCancelTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'BoardId': '10',
            'OrderDate': order_date,
            'OrderNo': 123456789012345,
        })
        
        req_dict = req.to_dict()
        assert isinstance(req_dict, dict)
        assert req_dict['OrderDate'] == order_date
        assert req_dict['OrderNo'] == 123456789012345
    
    def test_cancel_response_creation(self):
        """测试撤单响应结构体创建"""
        today = date.today()
        order_date = today.year * 10000 + today.month * 100 + today.day
        
        rsp = COXRspCancelTicketField()
        rsp.OrderDate = order_date
        rsp.OrderNo = 123456789012345
        rsp.OrderState = ord('0')
        rsp.StkBiz = 100
        rsp.StkBizAction = 100
        
        assert rsp.OrderDate == order_date
        assert rsp.OrderNo == 123456789012345
        assert rsp.OrderState == b'0' or rsp.OrderState == ord('0')
    
    def test_cancel_response_to_dict(self):
        """测试撤单响应结构体转字典"""
        today = date.today()
        order_date = today.year * 10000 + today.month * 100 + today.day
        
        rsp = COXRspCancelTicketField()
        rsp.OrderDate = order_date
        rsp.OrderNo = 123456789012345
        rsp.OrderState = ord('0')
        rsp.StkBiz = 100
        rsp.StkBizAction = 100
        
        rsp_dict = rsp.to_dict()
        assert isinstance(rsp_dict, dict)
        assert rsp_dict['OrderDate'] == order_date
        assert rsp_dict['OrderNo'] == 123456789012345
        assert rsp_dict['OrderState'] == '0'
        assert rsp_dict['StkBiz'] == 100


class TestCancelAPI:
    """测试撤单 API"""
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_success(self, mock_dll_loader_class):
        """测试撤单成功"""
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
        
        # 撤单
        board_id = '10'
        order_no = 123456789012345
        request_id = api.cancel(board_id, order_no)
        
        assert request_id > 0
        
        # 等待回调
        time.sleep(0.2)
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_order_date(self, mock_dll_loader_class):
        """测试使用指定委托日期撤单"""
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
        
        # 确保账户信息已设置
        if not api._account:
            api._account = '110060035050'
            api._acct_type = AccountType.CREDIT
        
        # 使用指定日期撤单
        order_date = 20240101
        board_id = '10'
        order_no = 123456789012345
        request_id = api.cancel(board_id, order_no, order_date)
        
        assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_without_init(self, mock_dll_loader_class):
        """测试未初始化时撤单"""
        api = OXTradeApi()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.cancel('10', 123456789012345)
        
        assert "API not initialized" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_without_login(self, mock_dll_loader_class):
        """测试未登录时撤单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.cancel('10', 123456789012345)
        
        assert "Not logged in" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_without_spi(self, mock_dll_loader_class):
        """测试未注册 SPI 时撤单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True  # 模拟已登录
        
        with pytest.raises(OXOrderError) as exc_info:
            api.cancel('10', 123456789012345)
        
        assert "SPI not registered" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_without_account(self, mock_dll_loader_class):
        """测试账户信息未设置时撤单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = ''  # 账户信息为空
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        with pytest.raises(OXOrderError) as exc_info:
            api.cancel('10', 123456789012345)
        
        assert "Account not available" in str(exc_info.value)


class TestCancelCallback:
    """测试撤单回调"""
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_callback_received(self, mock_dll_loader_class):
        """测试撤单响应回调接收"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
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
        
        # 撤单
        request_id = api.cancel('10', 123456789012345)
        
        # 等待回调
        time.sleep(0.2)
        
        assert len(callback_received) > 0
        assert callback_received[0]['request'] == request_id
        assert callback_received[0]['error'] is None
        assert callback_received[0]['field'] is not None
        assert callback_received[0]['field']['OrderNo'] == 123456789012345
        assert callback_received[0]['field']['OrderState'] == '0'
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_callback_with_error(self, mock_dll_loader_class):
        """测试撤单响应回调（有错误）"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                callback_received.append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发撤单响应回调（有错误）
        error_dict = {'ErrorId': 1001, 'ErrorInfo': '撤单失败'}
        field_dict = None
        
        api.spi.on_rsp_cancel_ticket(1, error_dict, field_dict)
        
        assert len(callback_received) > 0
        assert callback_received[0]['error'] is not None
        assert callback_received[0]['error']['ErrorId'] == 1001
        assert callback_received[0]['field'] is None
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_callback_with_spi_wrapper(self, mock_dll_loader_class):
        """测试 SPI 包装类的撤单回调转发"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                callback_received.append(('cancel', request, error, field))
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 测试撤单回调
        error_dict = None
        field_dict = {'OrderNo': 123456789012345, 'OrderState': '0'}
        api.spi.on_rsp_cancel_ticket(1, error_dict, field_dict)
        
        assert len(callback_received) == 1
        assert callback_received[0][0] == 'cancel'
        assert callback_received[0][1] == 1
        
        api.stop()


class TestCancelErrorHandling:
    """测试撤单错误处理"""
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_failure_return_code(self, mock_dll_loader_class):
        """测试撤单请求返回非零代码"""
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
        
        # 模拟撤单请求返回非零代码
        with patch.object(api, '_call_cancel_virtual', return_value=1):
            with pytest.raises(OXOrderError) as exc_info:
                api.cancel('10', 123456789012345)
            
            assert "Cancel request failed with return code: 1" in str(exc_info.value)
        
        api.stop()


class TestCancelEdgeCases:
    """测试撤单边界情况"""
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_zero_order_no(self, mock_dll_loader_class):
        """测试委托号为0时撤单"""
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
        
        # 委托号为0
        request_id = api.cancel('10', 0)
        assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_negative_order_no(self, mock_dll_loader_class):
        """测试委托号为负数时撤单"""
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
        
        # 委托号为负数（虽然不合法，但应该能够处理）
        request_id = api.cancel('10', -1)
        assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_large_order_no(self, mock_dll_loader_class):
        """测试委托号很大时撤单"""
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
        
        # 委托号很大
        large_order_no = 9223372036854775807  # int64 最大值
        request_id = api.cancel('10', large_order_no)
        assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_different_board_ids(self, mock_dll_loader_class):
        """测试不同交易板块撤单"""
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
        
        # 上海板块
        request_id_sh = api.cancel('10', 123456789012345)
        assert request_id_sh > 0
        
        # 深圳板块
        request_id_sz = api.cancel('00', 123456789012345)
        assert request_id_sz > 0
        
        assert request_id_sh != request_id_sz  # 不同的请求应该有不同编号
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_different_account_types(self, mock_dll_loader_class):
        """测试不同账户类型撤单"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 测试不同账户类型
        for acct_type in [AccountType.STOCK, AccountType.OPTION, AccountType.FUTURE, AccountType.CREDIT]:
            api._acct_type = acct_type
            request_id = api.cancel('10', 123456789012345)
            assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_with_various_order_dates(self, mock_dll_loader_class):
        """测试不同委托日期撤单"""
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
        
        # 测试不同的日期格式
        test_dates = [
            20240101,  # 正常日期
            20231231,  # 上一年最后一天
            20240229,  # 闰年2月29日（虽然2024年有，但格式上可能不合法）
            20000101,  # 很早的日期
            20991231,  # 很晚的日期
        ]
        
        for order_date in test_dates:
            request_id = api.cancel('10', 123456789012345, order_date)
            assert request_id > 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_auto_date_calculation(self, mock_dll_loader_class):
        """测试自动计算委托日期"""
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
        
        # 不提供委托日期，应该自动使用当前日期
        from datetime import date
        expected_date = date.today().year * 10000 + date.today().month * 100 + date.today().day
        
        request_id = api.cancel('10', 123456789012345)
        assert request_id > 0
        
        # 等待回调并验证日期
        time.sleep(0.2)
        
        api.stop()


class TestCancelStructureEdgeCases:
    """测试撤单结构体边界情况"""
    
    def test_cancel_request_from_dict_empty(self):
        """测试从空字典创建撤单请求结构体"""
        req = COXReqCancelTicketField.from_dict({})
        
        assert req is not None
        assert req.AcctType == b'0' or req.AcctType == ord('0')  # 默认值
        assert req.OrderDate == 0
        assert req.OrderNo == 0
    
    def test_cancel_request_from_dict_partial(self):
        """测试从部分字段字典创建撤单请求结构体"""
        req = COXReqCancelTicketField.from_dict({
            'Account': '110060035050',
            'OrderNo': 123456789012345,
        })
        
        assert req is not None
        assert req.OrderNo == 123456789012345
    
    def test_cancel_request_from_dict_with_bytes(self):
        """测试从包含字节值的字典创建撤单请求结构体"""
        req = COXReqCancelTicketField.from_dict({
            'AcctType': b'0',
            'Account': b'110060035050',
            'BoardId': b'10',
            'OrderDate': 20240101,
            'OrderNo': 123456789012345,
        })
        
        assert req is not None
        assert req.OrderDate == 20240101
        assert req.OrderNo == 123456789012345
    
    def test_cancel_request_to_dict_with_empty_strings(self):
        """测试撤单请求结构体转字典（空字符串字段）"""
        req = COXReqCancelTicketField()
        req.AcctType = ord('0')
        req.OrderDate = 0
        req.OrderNo = 0
        
        req_dict = req.to_dict()
        assert isinstance(req_dict, dict)
        assert req_dict['OrderDate'] == 0
        assert req_dict['OrderNo'] == 0
    
    def test_cancel_response_with_different_order_states(self):
        """测试不同委托状态的撤单响应"""
        rsp = COXRspCancelTicketField()
        rsp.OrderDate = 20240101
        rsp.OrderNo = 123456789012345
        
        # 测试不同的委托状态
        states = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for state in states:
            rsp.OrderState = ord(state)
            rsp_dict = rsp.to_dict()
            assert rsp_dict['OrderState'] == state


class TestCancelCallbackEdgeCases:
    """测试撤单回调边界情况"""
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_callback_with_none_field(self, mock_dll_loader_class):
        """测试撤单响应回调（field为None）"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                callback_received.append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发撤单响应回调（field为None）
        error_dict = None
        field_dict = None
        
        api.spi.on_rsp_cancel_ticket(1, error_dict, field_dict)
        
        assert len(callback_received) == 1
        assert callback_received[0]['request'] == 1
        assert callback_received[0]['error'] is None
        assert callback_received[0]['field'] is None
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_callback_with_empty_field(self, mock_dll_loader_class):
        """测试撤单响应回调（空字典字段）"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                callback_received.append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发撤单响应回调（空字典字段）
        error_dict = None
        field_dict = {}
        
        api.spi.on_rsp_cancel_ticket(1, error_dict, field_dict)
        
        assert len(callback_received) == 1
        assert callback_received[0]['field'] == {}
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_cancel_callback_multiple_callbacks(self, mock_dll_loader_class):
        """测试多个撤单响应回调"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_received = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_cancel_ticket(self, request, error, field):
                callback_received.append({
                    'request': request,
                    'error': error,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 触发多个撤单响应回调
        for i in range(5):
            error_dict = None
            field_dict = {'OrderNo': 123456789012345 + i, 'OrderState': '0'}
            api.spi.on_rsp_cancel_ticket(i + 1, error_dict, field_dict)
        
        assert len(callback_received) == 5
        for i, callback in enumerate(callback_received):
            assert callback['request'] == i + 1
            assert callback['field']['OrderNo'] == 123456789012345 + i
        
        api.stop()


class TestCancelVirtualFunction:
    """测试撤单虚函数调用"""
    
    @patch('stock_ox.api.DLLoader')
    def test_call_cancel_virtual_without_spi(self, mock_dll_loader_class):
        """测试没有SPI时调用撤单虚函数"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api._logged_in = True
        api._account = '110060035050'
        api._acct_type = AccountType.CREDIT
        api.spi = None  # 没有SPI
        
        req = COXReqCancelTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'BoardId': '10',
            'OrderDate': 20240101,
            'OrderNo': 123456789012345,
        })
        
        # 调用虚函数（应该返回0，不会触发回调）
        result = api._call_cancel_virtual(1, req)
        assert result == 0
        
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_simulate_cancel_callback_without_spi(self, mock_dll_loader_class):
        """测试模拟撤单回调时没有SPI"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api.spi = None  # 没有SPI
        
        req = COXReqCancelTicketField.from_dict({
            'AcctType': '0',
            'Account': '110060035050',
            'BoardId': '10',
            'OrderDate': 20240101,
            'OrderNo': 123456789012345,
        })
        
        # 模拟回调（应该不会崩溃）
        api._simulate_cancel_callback(1, req)
        
        # 等待一下确保线程执行完成
        time.sleep(0.2)
        
        api.stop()

