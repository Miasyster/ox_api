"""
阶段二验收测试

验收标准：
1. 可以成功初始化 API
2. 可以成功登录账户
3. 可以接收登录响应回调
"""

import pytest
import sys
import time
from unittest.mock import patch, MagicMock
from ctypes import c_void_p

from stock_ox.api import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.exceptions import OXConnectionError, OXLoginError


class TestStage2Acceptance:
    """阶段二验收测试"""
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_1_init_api(self, mock_dll_loader_class):
        """
        验收标准 1: 可以成功初始化 API
        
        测试步骤：
        1. 创建 API 实例
        2. 调用 init() 方法
        3. 验证初始化成功
        4. 验证 API 实例状态
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        assert api is not None, "API 实例创建失败"
        assert not api.is_initialized(), "初始状态应该未初始化"
        
        # 初始化 API
        result = api.init()
        assert result == 0, f"初始化失败，返回码: {result}"
        assert api.is_initialized(), "初始化后应该标记为已初始化"
        assert api.api_ptr is not None, "API 指针应该不为空"
        
        print("✓ API 初始化成功")
        
        # 清理
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_2_login_account(self, mock_dll_loader_class):
        """
        验收标准 2: 可以成功登录账户
        
        测试步骤：
        1. 初始化 API
        2. 注册 SPI
        3. 调用 login() 方法
        4. 验证登录成功
        5. 验证登录状态
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        
        # 初始化 API
        api.init()
        assert api.is_initialized(), "API 应该已初始化"
        
        # 注册 SPI
        spi = OXTradeSpi()
        api.register_spi(spi)
        assert api.spi is not None, "SPI 应该已注册"
        
        # 登录账户
        account = '110060035050'
        password = '111111'
        account_type = AccountType.CREDIT
        
        result = api.login(account, password, account_type, timeout=1.0)
        assert result is True, f"登录失败，返回值: {result}"
        assert api.is_logged_in(), "登录后应该标记为已登录"
        
        print(f"✓ 账户 {account} 登录成功")
        
        # 清理
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_criterion_3_receive_login_callback(self, mock_dll_loader_class):
        """
        验收标准 3: 可以接收登录响应回调
        
        测试步骤：
        1. 初始化 API
        2. 创建自定义 SPI 来捕获回调
        3. 注册 SPI
        4. 触发登录（模拟回调）
        5. 验证回调被正确接收
        6. 验证回调数据正确
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        api = OXTradeApi()
        api.init()
        
        # 创建自定义 SPI 来捕获回调
        callback_received = []
        callback_data = {}
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_logon(self, request, error, is_last, field):
                callback_received.append(True)
                callback_data['request'] = request
                callback_data['error'] = error
                callback_data['is_last'] = is_last
                callback_data['field'] = field
        
        spi = CustomSpi()
        api.register_spi(spi)
        
        # 手动触发登录回调（模拟登录成功）
        request_id = 1
        error_dict = None  # 无错误
        field_dict = {
            'IntOrg': 12345,
            'CustCode': 'CUST001',
            'AcctType': '0',
            'Account': '110060035050'
        }
        
        # 通过 SPI 包装类触发回调
        api.spi.on_rsp_logon(request_id, error_dict, True, field_dict)
        
        # 验证回调被接收
        assert len(callback_received) > 0, "登录回调应该被接收"
        assert callback_data['request'] == request_id, "回调请求 ID 应该正确"
        assert callback_data['is_last'] is True, "回调 is_last 标志应该正确"
        assert callback_data['field'] is not None, "回调字段应该不为空"
        assert api.is_logged_in(), "登录成功后应该标记为已登录"
        
        print("✓ 登录响应回调接收成功")
        print(f"  - 请求 ID: {callback_data['request']}")
        print(f"  - 是否最后一条: {callback_data['is_last']}")
        print(f"  - 登录状态: {'成功' if api.is_logged_in() else '失败'}")
        
        # 清理
        api.stop()
    
    @patch('stock_ox.api.DLLoader')
    def test_complete_workflow(self, mock_dll_loader_class):
        """
        完整工作流程测试
        
        测试完整的初始化 -> 登录 -> 接收回调流程
        """
        mock_loader = MagicMock()
        mock_loader.load.return_value = mock_loader
        mock_loader.create_api.return_value = c_void_p(12345)
        mock_dll_loader_class.return_value = mock_loader
        
        callback_called = []
        
        class CustomSpi(OXTradeSpi):
            def on_rsp_logon(self, request, error, is_last, field):
                callback_called.append({
                    'request': request,
                    'error': error,
                    'is_last': is_last,
                    'field': field
                })
        
        # 使用上下文管理器
        with OXTradeApi() as api:
            assert api.is_initialized(), "API 应该已初始化"
            
            spi = CustomSpi()
            api.register_spi(spi)
            
            # 登录
            result = api.login('110060035050', '111111', AccountType.CREDIT, timeout=1.0)
            assert result is True, "登录应该成功"
            assert api.is_logged_in(), "登录状态应该正确"
            assert len(callback_called) > 0, "登录回调应该被调用"
            
            print("✓ 完整工作流程测试通过")
            print(f"  - API 初始化: {'成功' if api.is_initialized() else '失败'}")
            print(f"  - 账户登录: {'成功' if api.is_logged_in() else '失败'}")
            print(f"  - 回调接收: {'成功' if len(callback_called) > 0 else '失败'}")
        
        # 上下文管理器退出后，API 应该已停止
        assert not api.is_initialized(), "API 应该已停止"


def test_all_criteria():
    """运行所有验收标准测试"""
    test_instance = TestStage2Acceptance()
    
    print("\n" + "="*60)
    print("阶段二验收测试开始")
    print("="*60)
    
    # 验收标准 1: 可以成功初始化 API
    print("\n[验收标准 1] 测试 API 初始化...")
    try:
        with patch('stock_ox.api.DLLoader'):
            test_instance.test_criterion_1_init_api()
        print("✅ 验收标准 1 通过: 可以成功初始化 API")
    except Exception as e:
        print(f"❌ 验收标准 1 失败: {e}")
        raise
    
    # 验收标准 2: 可以成功登录账户
    print("\n[验收标准 2] 测试账户登录...")
    try:
        with patch('stock_ox.api.DLLoader'):
            test_instance.test_criterion_2_login_account()
        print("✅ 验收标准 2 通过: 可以成功登录账户")
    except Exception as e:
        print(f"❌ 验收标准 2 失败: {e}")
        raise
    
    # 验收标准 3: 可以接收登录响应回调
    print("\n[验收标准 3] 测试登录回调接收...")
    try:
        with patch('stock_ox.api.DLLoader'):
            test_instance.test_criterion_3_receive_login_callback()
        print("✅ 验收标准 3 通过: 可以接收登录响应回调")
    except Exception as e:
        print(f"❌ 验收标准 3 失败: {e}")
        raise
    
    # 完整工作流程测试
    print("\n[额外测试] 测试完整工作流程...")
    try:
        with patch('stock_ox.api.DLLoader'):
            test_instance.test_complete_workflow()
        print("✅ 完整工作流程测试通过")
    except Exception as e:
        print(f"❌ 完整工作流程测试失败: {e}")
        raise
    
    print("\n" + "="*60)
    print("✅ 阶段二验收测试全部通过！")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_all_criteria()

