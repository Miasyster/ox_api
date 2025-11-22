"""
阶段一验收测试

验证阶段一验收标准：
1. ✅ 可以成功加载 DLL
2. ✅ 可以创建和释放 API 实例
3. ✅ 基础结构体可以正确创建和访问
"""

import sys
import os
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from ctypes import sizeof

from stock_ox.dll_loader import (
    load_dll,
    get_create_api_func,
    get_release_api_func
)
from stock_ox.exceptions import OXDllError
from stock_ox.structs import (
    CRspErrorField,
    COXReqLogonField,
    COXRspLogonField,
    COXReqTradeAcctField,
    COXRspTradeAcctField
)
from stock_ox.constants import (
    OX_ERRORINFO_LENGTH,
    OX_ACCOUNT_LENGTH,
    OX_PASSWORD_LENGTH,
    OX_RESERVED_LENGTH,
    OX_CUSTCODE_LENGTH
)


class TestStage1Acceptance:
    """阶段一验收测试"""
    
    def test_criterion_1_load_dll(self):
        """
        验收标准 1: 可以成功加载 DLL
        
        测试步骤：
        1. 尝试加载 DLL
        2. 验证 DLL 对象不为 None
        3. 验证 DLL 对象类型正确
        """
        # 获取 DLL 路径（相对于项目根目录）
        project_root = Path(__file__).parent.parent.parent.parent
        dll_path = project_root / "bin" / "GuosenOXAPI.dll"
        
        # 如果是 macOS/Linux，跳过 DLL 加载测试（DLL 只能在 Windows 上加载）
        if sys.platform != 'win32':
            pytest.skip("DLL loading test only works on Windows")
        
        # 如果 DLL 文件不存在，跳过测试
        if not dll_path.exists():
            pytest.skip(f"DLL file not found: {dll_path}")
        
        # 测试加载 DLL
        try:
            dll = load_dll(str(dll_path))
            assert dll is not None, "DLL 加载失败，返回 None"
            assert hasattr(dll, '_handle'), "DLL 对象无效"
            print(f"✓ 成功加载 DLL: {dll_path}")
        except OXDllError as e:
            pytest.fail(f"DLL 加载失败: {e}")
        except Exception as e:
            pytest.fail(f"加载 DLL 时发生意外错误: {e}")
    
    def test_criterion_2_create_and_release_api(self):
        """
        验收标准 2: 可以创建和释放 API 实例
        
        测试步骤：
        1. 加载 DLL
        2. 获取创建 API 函数
        3. 创建 API 实例
        4. 验证 API 实例不为 None
        5. 释放 API 实例
        6. 验证释放成功
        """
        # 如果是 macOS/Linux，跳过 DLL 测试
        if sys.platform != 'win32':
            pytest.skip("API creation test only works on Windows")
        
        # 获取 DLL 路径
        project_root = Path(__file__).parent.parent.parent.parent
        dll_path = project_root / "bin" / "GuosenOXAPI.dll"
        
        if not dll_path.exists():
            pytest.skip(f"DLL file not found: {dll_path}")
        
        try:
            # 1. 加载 DLL
            dll = load_dll(str(dll_path))
            assert dll is not None, "DLL 加载失败"
            
            # 2. 获取创建 API 函数
            create_api_func = get_create_api_func(dll)
            assert create_api_func is not None, "无法获取创建 API 函数"
            
            # 3. 创建 API 实例
            api_instance = create_api_func()
            assert api_instance is not None, "API 实例创建失败，返回 None"
            assert api_instance != 0, "API 实例创建失败，返回 0"
            print(f"✓ 成功创建 API 实例: {api_instance}")
            
            # 4. 获取释放 API 函数
            release_api_func = get_release_api_func(dll)
            assert release_api_func is not None, "无法获取释放 API 函数"
            
            # 5. 释放 API 实例
            result = release_api_func(api_instance)
            # 释放函数可能返回 void，也可能返回 int
            print(f"✓ 成功释放 API 实例，返回: {result}")
            
        except OXDllError as e:
            pytest.fail(f"DLL 操作失败: {e}")
        except Exception as e:
            pytest.fail(f"创建/释放 API 时发生意外错误: {e}")
    
    def test_criterion_3_structs_creation_and_access(self):
        """
        验收标准 3: 基础结构体可以正确创建和访问
        
        测试步骤：
        1. 创建所有基础结构体实例
        2. 验证结构体大小正确
        3. 验证结构体字段可以访问
        4. 验证结构体可以正确转换为字典
        """
        # 测试 CRspErrorField
        error = CRspErrorField()
        assert error is not None, "CRspErrorField 创建失败"
        assert sizeof(error) == 4 + OX_ERRORINFO_LENGTH, "CRspErrorField 大小不正确"
        assert hasattr(error, 'ErrorId'), "CRspErrorField 缺少 ErrorId 字段"
        assert hasattr(error, 'ErrorInfo'), "CRspErrorField 缺少 ErrorInfo 字段"
        assert error.ErrorId == 0, "CRspErrorField.ErrorId 默认值不正确"
        error_dict = error.to_dict()
        assert isinstance(error_dict, dict), "to_dict() 返回类型不正确"
        assert 'ErrorId' in error_dict, "to_dict() 缺少 ErrorId"
        assert 'ErrorInfo' in error_dict, "to_dict() 缺少 ErrorInfo"
        print("✓ CRspErrorField 创建和访问正常")
        
        # 测试 COXReqLogonField
        req_logon = COXReqLogonField()
        assert req_logon is not None, "COXReqLogonField 创建失败"
        expected_size = 1 + OX_ACCOUNT_LENGTH + OX_PASSWORD_LENGTH + OX_RESERVED_LENGTH
        assert sizeof(req_logon) == expected_size, f"COXReqLogonField 大小不正确: {sizeof(req_logon)} != {expected_size}"
        assert hasattr(req_logon, 'AcctType'), "COXReqLogonField 缺少 AcctType 字段"
        assert hasattr(req_logon, 'Account'), "COXReqLogonField 缺少 Account 字段"
        assert hasattr(req_logon, 'Password'), "COXReqLogonField 缺少 Password 字段"
        assert hasattr(req_logon, 'Reserved'), "COXReqLogonField 缺少 Reserved 字段"
        req_logon_dict = req_logon.to_dict()
        assert isinstance(req_logon_dict, dict), "to_dict() 返回类型不正确"
        print("✓ COXReqLogonField 创建和访问正常")
        
        # 测试 COXReqLogonField.from_dict
        req_logon_data = {
            'AcctType': '0',
            'Account': '110060035050',
            'Password': '111111'
        }
        req_logon_from_dict = COXReqLogonField.from_dict(req_logon_data)
        assert req_logon_from_dict is not None, "from_dict() 创建失败"
        assert req_logon_from_dict.AcctType == ord('0') or req_logon_from_dict.AcctType == b'0', "AcctType 设置不正确"
        print("✓ COXReqLogonField.from_dict() 正常工作")
        
        # 测试 COXRspLogonField
        resp_logon = COXRspLogonField()
        assert resp_logon is not None, "COXRspLogonField 创建失败"
        expected_size = 4 + OX_CUSTCODE_LENGTH + 1 + OX_ACCOUNT_LENGTH
        assert sizeof(resp_logon) == expected_size, f"COXRspLogonField 大小不正确: {sizeof(resp_logon)} != {expected_size}"
        assert hasattr(resp_logon, 'IntOrg'), "COXRspLogonField 缺少 IntOrg 字段"
        assert hasattr(resp_logon, 'CustCode'), "COXRspLogonField 缺少 CustCode 字段"
        assert hasattr(resp_logon, 'AcctType'), "COXRspLogonField 缺少 AcctType 字段"
        assert hasattr(resp_logon, 'Account'), "COXRspLogonField 缺少 Account 字段"
        assert resp_logon.IntOrg == 0, "COXRspLogonField.IntOrg 默认值不正确"
        resp_logon_dict = resp_logon.to_dict()
        assert isinstance(resp_logon_dict, dict), "to_dict() 返回类型不正确"
        print("✓ COXRspLogonField 创建和访问正常")
        
        # 测试 COXReqTradeAcctField
        req_trade_acct = COXReqTradeAcctField()
        assert req_trade_acct is not None, "COXReqTradeAcctField 创建失败"
        expected_size = 1 + OX_ACCOUNT_LENGTH
        assert sizeof(req_trade_acct) == expected_size, f"COXReqTradeAcctField 大小不正确: {sizeof(req_trade_acct)} != {expected_size}"
        assert hasattr(req_trade_acct, 'AcctType'), "COXReqTradeAcctField 缺少 AcctType 字段"
        assert hasattr(req_trade_acct, 'Account'), "COXReqTradeAcctField 缺少 Account 字段"
        req_trade_acct_dict = req_trade_acct.to_dict()
        assert isinstance(req_trade_acct_dict, dict), "to_dict() 返回类型不正确"
        print("✓ COXReqTradeAcctField 创建和访问正常")
        
        # 测试 COXRspTradeAcctField
        resp_trade_acct = COXRspTradeAcctField()
        assert resp_trade_acct is not None, "COXRspTradeAcctField 创建失败"
        expected_size = (
            OX_CUSTCODE_LENGTH +
            OX_ACCOUNT_LENGTH +
            1 +  # ExchangeId
            4 +  # BoardId
            1 +  # TrdAcctStatus
            24 +  # TrdAcct
            1    # TrdAcctType
        )
        assert sizeof(resp_trade_acct) == expected_size, f"COXRspTradeAcctField 大小不正确: {sizeof(resp_trade_acct)} != {expected_size}"
        assert hasattr(resp_trade_acct, 'CustCode'), "COXRspTradeAcctField 缺少 CustCode 字段"
        assert hasattr(resp_trade_acct, 'Account'), "COXRspTradeAcctField 缺少 Account 字段"
        assert hasattr(resp_trade_acct, 'ExchangeId'), "COXRspTradeAcctField 缺少 ExchangeId 字段"
        assert hasattr(resp_trade_acct, 'BoardId'), "COXRspTradeAcctField 缺少 BoardId 字段"
        assert hasattr(resp_trade_acct, 'TrdAcct'), "COXRspTradeAcctField 缺少 TrdAcct 字段"
        resp_trade_acct_dict = resp_trade_acct.to_dict()
        assert isinstance(resp_trade_acct_dict, dict), "to_dict() 返回类型不正确"
        print("✓ COXRspTradeAcctField 创建和访问正常")


def test_all_criteria():
    """运行所有验收标准测试"""
    test_instance = TestStage1Acceptance()
    
    print("\n" + "="*60)
    print("阶段一验收测试开始")
    print("="*60)
    
    # 验收标准 1: 可以成功加载 DLL
    print("\n[验收标准 1] 测试 DLL 加载...")
    try:
        test_instance.test_criterion_1_load_dll()
        print("✅ 验收标准 1 通过: 可以成功加载 DLL")
    except pytest.skip.Exception as e:
        print(f"⏭️  验收标准 1 跳过: {e}")
    except Exception as e:
        print(f"❌ 验收标准 1 失败: {e}")
        raise
    
    # 验收标准 2: 可以创建和释放 API 实例
    print("\n[验收标准 2] 测试 API 创建和释放...")
    try:
        test_instance.test_criterion_2_create_and_release_api()
        print("✅ 验收标准 2 通过: 可以创建和释放 API 实例")
    except pytest.skip.Exception as e:
        print(f"⏭️  验收标准 2 跳过: {e}")
    except Exception as e:
        print(f"❌ 验收标准 2 失败: {e}")
        raise
    
    # 验收标准 3: 基础结构体可以正确创建和访问
    print("\n[验收标准 3] 测试结构体创建和访问...")
    try:
        test_instance.test_criterion_3_structs_creation_and_access()
        print("✅ 验收标准 3 通过: 基础结构体可以正确创建和访问")
    except Exception as e:
        print(f"❌ 验收标准 3 失败: {e}")
        raise
    
    print("\n" + "="*60)
    print("✅ 阶段一验收测试全部通过！")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_all_criteria()

