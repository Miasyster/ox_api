"""
API 模块测试

测试 API 初始化、登录功能。
"""

import pytest
import time
import sys
from unittest.mock import Mock, patch, MagicMock
from ctypes import c_void_p

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXLoginError, OXDllError
from stock_ox.dll_loader import DLLoader


class TestOXTradeApiInit:
    """测试 API 初始化"""
    
    def test_api_creation(self):
        """测试 API 创建"""
        api = OXTradeApi()
        assert api is not None
        assert not api.is_initialized()
        assert not api.is_logged_in()
    
    def test_api_creation_with_paths(self):
        """测试使用路径创建 API"""
        api = OXTradeApi(config_path='/path/to/config.ini', dll_path='/path/to/dll')
        assert api.config_path == '/path/to/config.ini'
        assert api.dll_path == '/path/to/dll'
    
    @patch('stock_ox.api.DLLoader')
    def test_init_success(self, mock_dll_loader_class):
        """测试初始化成功"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        result = api.init()
        
        assert result == 0
        assert api.is_initialized()
        mock_loader.load.assert_called_once()
        mock_loader.create_api.assert_called_once()
    
    @patch('stock_ox.api.DLLoader')
    def test_init_failure_no_api_instance(self, mock_dll_loader_class):
        """测试初始化失败 - 无法创建 API 实例"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = None
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.init()
        
        assert "Failed to create API instance" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_init_with_spi_registered(self, mock_dll_loader_class):
        """测试初始化时已注册 SPI"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        spi = OXTradeSpi()
        api = OXTradeApi()
        api.register_spi(spi)
        
        result = api.init()
        
        assert result == 0
        assert api.is_initialized()
        assert api.spi is not None


class TestOXTradeApiStop:
    """测试 API 停止"""
    
    @patch('stock_ox.api.DLLoader')
    def test_stop_after_init(self, mock_dll_loader_class):
        """测试初始化后停止"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api.stop()
        
        assert not api.is_initialized()
        assert not api.is_logged_in()
        mock_loader.release_api.assert_called_once()
    
    def test_stop_without_init(self):
        """测试未初始化时停止"""
        api = OXTradeApi()
        # 应该不抛出异常
        api.stop()
        assert not api.is_initialized()
    
    @patch('stock_ox.api.DLLoader')
    def test_stop_twice(self, mock_dll_loader_class):
        """测试停止两次"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        api.stop()
        api.stop()  # 第二次停止应该不抛出异常
        
        assert not api.is_initialized()


class TestOXTradeApiRegisterSpi:
    """测试 API 注册 SPI"""
    
    def test_register_spi_before_init(self):
        """测试初始化前注册 SPI"""
        api = OXTradeApi()
        spi = OXTradeSpi()
        
        api.register_spi(spi)
        
        assert api.spi is not None
        assert api.spi.user_spi == spi  # 检查是否包装
    
    @patch('stock_ox.api.DLLoader')
    def test_register_spi_after_init(self, mock_dll_loader_class):
        """测试初始化后注册 SPI"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        assert api.spi is not None


class TestOXTradeApiLogin:
    """测试 API 登录"""
    
    @patch('stock_ox.api.DLLoader')
    def test_login_success(self, mock_dll_loader_class):
        """测试登录成功"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 等待登录完成
        result = api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
        
        assert result is True
        assert api.is_logged_in()
    
    @patch('stock_ox.api.DLLoader')
    def test_login_without_init(self, mock_dll_loader_class):
        """测试未初始化时登录"""
        api = OXTradeApi()
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.login('110060035050', '111111')
        
        assert "API not initialized" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_login_without_spi(self, mock_dll_loader_class):
        """测试未注册 SPI 时登录"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        with pytest.raises(OXLoginError) as exc_info:
            api.login('110060035050', '111111')
        
        assert "SPI not registered" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_login_timeout(self, mock_dll_loader_class):
        """测试登录超时"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 模拟登录失败（不触发回调）
        with patch.object(api, '_call_logon_virtual', return_value=0):
            # 禁用模拟回调
            with patch.object(api, '_simulate_login_callback'):
                with pytest.raises(OXLoginError) as exc_info:
                    api.login('110060035050', '111111', timeout=0.1)
                
                assert "timeout" in str(exc_info.value).lower()
    
    @patch('stock_ox.api.DLLoader')
    def test_login_failure_callback(self, mock_dll_loader_class):
        """测试登录失败回调"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_called = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_logon(self, request, error, is_last, field):
                callback_called.append((request, error, is_last, field))
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 模拟登录失败回调
        def simulate_failure():
            time.sleep(0.1)
            error_dict = {'ErrorId': 1001, 'ErrorInfo': '登录失败'}
            # 直接调用 SPI 回调，触发登录响应处理
            api.spi.on_rsp_logon(1, error_dict, True, None)
        
        with patch.object(api, '_call_logon_virtual', return_value=0):
            threading = __import__('threading')
            threading.Thread(target=simulate_failure, daemon=True).start()
            
            # 登录失败时，_logged_in 为 False，但不会抛出异常
            # 只有在超时时才会抛出异常
            result = api.login('110060035050', '111111', timeout=1.0)
            
            # 登录失败，返回 False
            assert result is False
            assert not api.is_logged_in()
            assert len(callback_called) == 1


class TestOXTradeApiContextManager:
    """测试 API 上下文管理器"""
    
    @patch('stock_ox.api.DLLoader')
    def test_context_manager(self, mock_dll_loader_class):
        """测试上下文管理器"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        with OXTradeApi() as api:
            assert api.is_initialized()
        
        assert not api.is_initialized()
        mock_loader.release_api.assert_called_once()


class TestOXTradeApiLoginCallback:
    """测试登录回调处理"""
    
    @patch('stock_ox.api.DLLoader')
    def test_login_callback_success(self, mock_dll_loader_class):
        """测试登录成功回调"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_data = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_logon(self, request, error, is_last, field):
                callback_data.append({
                    'request': request,
                    'error': error,
                    'is_last': is_last,
                    'field': field
                })
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发登录回调（通过 SPI）
        error_dict = None  # 无错误
        field_dict = {'IntOrg': 123, 'Account': '110060035050'}
        api.spi.on_rsp_logon(1, error_dict, True, field_dict)
        
        assert api.is_logged_in()
        assert len(callback_data) == 1
        assert callback_data[0]['request'] == 1
        assert callback_data[0]['is_last'] is True
    
    @patch('stock_ox.api.DLLoader')
    def test_login_callback_failure(self, mock_dll_loader_class):
        """测试登录失败回调"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        error_dict = {'ErrorId': 1001, 'ErrorInfo': '密码错误'}
        api._handle_login_response(1, error_dict, None)
        
        assert not api.is_logged_in()
    
    @patch('stock_ox.api.DLLoader')
    def test_login_callback_with_error_id_zero(self, mock_dll_loader_class):
        """测试登录回调 - ErrorId 为 0 时应该成功"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        # ErrorId 为 0，但 error 不为 None
        error_dict = {'ErrorId': 0, 'ErrorInfo': '成功'}
        field_dict = {'IntOrg': 123, 'Account': '110060035050'}
        api._handle_login_response(1, error_dict, field_dict)
        
        assert api.is_logged_in()
    
    @patch('stock_ox.api.DLLoader')
    def test_spi_wrapper_delegation(self, mock_dll_loader_class):
        """测试 SPI 包装类的方法委托"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        callback_data = []
        
        class CustomSpi(OXTradeSpi):
            def on_connected(self):
                callback_data.append('connected')
                return 1
            
            def on_disconnected(self):
                callback_data.append('disconnected')
                return 1
            
            def on_rsp_trade_accounts(self, request, error, is_last, field):
                callback_data.append(('trade_accounts', request, error, is_last, field))
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 测试连接回调
        result = api.spi.on_connected()
        assert result == 1
        assert 'connected' in callback_data
        
        # 测试断开回调
        result = api.spi.on_disconnected()
        assert result == 1
        assert 'disconnected' in callback_data
        
        # 测试交易账户回调
        api.spi.on_rsp_trade_accounts(123, None, True, {'TrdAcct': 'test'})
        assert ('trade_accounts', 123, None, True, {'TrdAcct': 'test'}) in callback_data


class TestOXTradeApiInternalMethods:
    """测试 API 内部方法"""
    
    @patch('stock_ox.api.DLLoader')
    def test_get_next_request_id(self, mock_dll_loader_class):
        """测试获取下一个请求 ID"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        
        id1 = api._get_next_request_id()
        id2 = api._get_next_request_id()
        
        assert id1 == 1
        assert id2 == 2
        assert id2 > id1
    
    @patch('stock_ox.api.DLLoader')
    def test_call_init_virtual(self, mock_dll_loader_class):
        """测试调用 Init 虚函数"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.dll_loader = mock_loader
        api.api_ptr = c_void_p(12345)
        
        # 测试默认返回值
        result = api._call_init_virtual()
        assert result == 0
    
    @patch('stock_ox.api.DLLoader')
    def test_call_stop_virtual(self, mock_dll_loader_class):
        """测试调用 Stop 虚函数"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.dll_loader = mock_loader
        api.api_ptr = c_void_p(12345)
        
        # 应该不抛出异常
        api._call_stop_virtual()
    
    @patch('stock_ox.api.DLLoader')
    def test_init_with_error_msg(self, mock_dll_loader_class):
        """测试初始化时传递错误消息列表"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        err_msg = []
        result = api.init(err_msg)
        
        assert result == 0
        assert api.is_initialized()
    
    @patch('stock_ox.api.DLLoader')
    def test_init_failure_with_error_msg(self, mock_dll_loader_class):
        """测试初始化失败时填充错误消息"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = None
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        err_msg = []
        
        with pytest.raises(OXConnectionError) as exc_info:
            api.init(err_msg)
        
        assert len(err_msg) > 0
        assert "Failed to create API instance" in err_msg[0]
    
    @patch('stock_ox.api.DLLoader')
    def test_call_logon_virtual_without_spi(self, mock_dll_loader_class):
        """测试调用登录虚函数时没有 SPI"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.dll_loader = mock_loader
        api.api_ptr = c_void_p(12345)
        api.spi = None
        
        from stock_ox.structs import COXReqLogonField
        req = COXReqLogonField.from_dict({
            'AcctType': '0',
            'Account': 'test',
            'Password': 'test',
        })
        
        result = api._call_logon_virtual(1, req)
        assert result == 0
    
    @patch('stock_ox.api.DLLoader')
    def test_init_failure_nonzero_return_code(self, mock_dll_loader_class):
        """测试初始化返回非零代码"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.dll_loader = mock_loader
        api.api_ptr = c_void_p(12345)
        
        # 模拟 Init 返回非零代码
        with patch.object(api, '_call_init_virtual', return_value=1):
            with pytest.raises(OXConnectionError) as exc_info:
                api.init()
            
            assert "Init failed with return code: 1" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_init_failure_with_error_msg_list(self, mock_dll_loader_class):
        """测试初始化失败时传递错误消息列表"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.dll_loader = mock_loader
        api.api_ptr = c_void_p(12345)
        err_msg = ["DLL initialization failed"]
        
        # 模拟 Init 返回非零代码
        with patch.object(api, '_call_init_virtual', return_value=1):
            with pytest.raises(OXConnectionError) as exc_info:
                api.init(err_msg)
            
            assert "DLL initialization failed" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_init_dll_error_propagation(self, mock_dll_loader_class):
        """测试 DLL 错误传播"""
        mock_loader = MagicMock()
        mock_loader.load.side_effect = OXDllError("DLL load failed")
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        
        with pytest.raises(OXDllError) as exc_info:
            api.init()
        
        assert "DLL load failed" in str(exc_info.value)
    
    @patch('stock_ox.api.DLLoader')
    def test_login_failure_return_code(self, mock_dll_loader_class):
        """测试登录请求返回非零代码"""
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        spi = OXTradeSpi()
        api.register_spi(spi)
        
        # 模拟登录请求返回非零代码
        with patch.object(api, '_call_logon_virtual', return_value=1):
            with pytest.raises(OXLoginError) as exc_info:
                api.login('110060035050', '111111', timeout=1.0)
            
            assert "Login request failed with return code: 1" in str(exc_info.value)

