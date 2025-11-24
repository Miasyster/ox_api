#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国信证券 OX 交易 API 登录测试脚本

注意：此脚本需要在 Windows 系统上运行，因为依赖 Windows DLL 文件。
在 macOS/Linux 系统上无法直接运行。
"""

import os
import sys
import configparser
import ctypes
from ctypes import Structure, c_char, c_int, c_char_p, POINTER, CFUNCTYPE

# 常量定义（来自 OXTradeApiConst.h）
OX_ERRORINFO_LENGTH = 128
OX_ACCOUNT_LENGTH = 24
OX_PASSWORD_LENGTH = 16
OX_RESERVED_LENGTH = 256

# 账户类型（来自 OXTradeApiConst.h）
OX_ACCOUNT_STOCK = ord('0')    # 现货账户
OX_ACCOUNT_OPTION = ord('1')   # 期权账户
OX_ACCOUNT_FUTURE = ord('2')   # 期货账户
OX_ACCOUNT_CREDIT = ord('3')   # 信用账户


class CRspErrorField(Structure):
    """错误响应结构"""
    _fields_ = [
        ("ErrorId", c_int),
        ("ErrorInfo", c_char * OX_ERRORINFO_LENGTH)
    ]


class COXReqLogonField(Structure):
    """登录请求结构"""
    _fields_ = [
        ("AcctType", c_char),                    # 账户类型
        ("Account", c_char * OX_ACCOUNT_LENGTH),  # 资金账号
        ("Password", c_char * OX_PASSWORD_LENGTH), # 密码
        ("Reserved", c_char * OX_RESERVED_LENGTH) # 保留字段
    ]


class COXRspLogonField(Structure):
    """登录响应结构"""
    _fields_ = [
        ("Account", c_char * OX_ACCOUNT_LENGTH),
        ("Reserved", c_char * OX_RESERVED_LENGTH)
    ]


# 回调函数类型定义
OnRspLogonCallback = CFUNCTYPE(None, c_int, POINTER(CRspErrorField), c_int, POINTER(COXRspLogonField))
OnConnectedCallback = CFUNCTYPE(c_int)
OnDisconnectedCallback = CFUNCTYPE(c_int)


class OXTradeApi:
    """国信证券 OX 交易 API Python 包装类"""
    
    def __init__(self, dll_path=None):
        """
        初始化 API
        
        Args:
            dll_path: DLL 文件路径，如果为 None，则尝试从 bin 目录加载
        """
        if dll_path is None:
            # 尝试从项目 bin 目录加载 DLL
            script_dir = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(script_dir, "bin", "GuosenOXAPI.dll")
        
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"无法找到 DLL 文件: {dll_path}")
        
        try:
            self.dll = ctypes.CDLL(dll_path)
        except OSError as e:
            raise RuntimeError(f"无法加载 DLL 文件: {e}\n"
                             f"注意：此 DLL 只能在 Windows 系统上运行。")
        
        # 定义函数签名
        self._setup_functions()
        
        # 回调函数
        self._logon_callback = None
        self._connected_callback = None
        self._disconnected_callback = None
        
    def _setup_functions(self):
        """设置 DLL 函数签名"""
        # gxCreateTradeApi
        self.dll.gxCreateTradeApi.argtypes = []
        self.dll.gxCreateTradeApi.restype = ctypes.c_void_p
        
        # gxReleaseTradeApi
        self.dll.gxReleaseTradeApi.argtypes = [ctypes.c_void_p]
        self.dll.gxReleaseTradeApi.restype = None
        
        # RegisterSpi
        self.dll.RegisterSpi.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.dll.RegisterSpi.restype = None
        
        # Init
        self.dll.Init.argtypes = [ctypes.c_void_p, POINTER(c_char_p)]
        self.dll.Init.restype = c_int
        
        # OnReqLogon
        self.dll.OnReqLogon.argtypes = [ctypes.c_void_p, c_int, POINTER(COXReqLogonField)]
        self.dll.OnReqLogon.restype = c_int
        
        # Stop
        self.dll.Stop.argtypes = [ctypes.c_void_p]
        self.dll.Stop.restype = c_int
    
    def create_api(self):
        """创建 API 实例"""
        api_ptr = self.dll.gxCreateTradeApi()
        if api_ptr is None:
            raise RuntimeError("创建 API 实例失败")
        return api_ptr
    
    def release_api(self, api_ptr):
        """释放 API 实例"""
        if api_ptr:
            self.dll.gxReleaseTradeApi(api_ptr)
    
    def register_spi(self, api_ptr, spi_ptr):
        """注册回调接口"""
        self.dll.RegisterSpi(api_ptr, spi_ptr)
    
    def init(self, api_ptr):
        """初始化 API"""
        error_msg = c_char_p()
        result = self.dll.Init(api_ptr, ctypes.byref(error_msg))
        error_info = error_msg.value.decode('utf-8', errors='ignore') if error_msg.value else ""
        return result, error_info
    
    def login(self, api_ptr, account, password, acct_type=OX_ACCOUNT_STOCK):
        """
        登录
        
        Args:
            api_ptr: API 实例指针
            account: 资金账号
            password: 密码
            acct_type: 账户类型，默认为现货账户
        
        Returns:
            登录请求返回值
        """
        req = COXReqLogonField()
        req.AcctType = acct_type
        req.Account = account.encode('utf-8')[:OX_ACCOUNT_LENGTH-1]
        req.Password = password.encode('utf-8')[:OX_PASSWORD_LENGTH-1]
        
        result = self.dll.OnReqLogon(api_ptr, 0, ctypes.byref(req))
        return result
    
    def stop(self, api_ptr):
        """停止 API"""
        return self.dll.Stop(api_ptr)


def load_config(config_path):
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    
    if 'user' not in config:
        raise ValueError("配置文件中缺少 [user] 节")
    
    user_config = config['user']
    
    account = user_config.get('acct', '')
    password = user_config.get('password', '')
    acct_type_str = user_config.get('acct_type', '0')
    
    # 账户类型转换
    acct_type_map = {
        '0': OX_ACCOUNT_STOCK,
        '1': OX_ACCOUNT_OPTION,
        '2': OX_ACCOUNT_FUTURE,
        '3': OX_ACCOUNT_CREDIT
    }
    acct_type = acct_type_map.get(acct_type_str, OX_ACCOUNT_STOCK)
    
    return {
        'account': account,
        'password': password,
        'acct_type': acct_type,
        'sh_trade_account': user_config.get('sh_trade_account', ''),
        'sz_trade_account': user_config.get('sz_trade_account', '')
    }


def test_login():
    """测试登录功能"""
    print("=" * 60)
    print("国信证券 OX 交易 API 登录测试")
    print("=" * 60)
    
    # 检查操作系统
    if sys.platform != 'win32':
        print(f"\n⚠️  警告：当前运行在 {sys.platform} 系统上")
        print("此 API 需要 Windows 系统和 Windows DLL 文件才能运行。")
        print("请在 Windows 系统上运行此脚本，或使用 C++ 编译的 demo 程序。\n")
        print("C++ demo 程序使用方法：")
        print("1. 使用 Visual Studio 打开 demo/demo.sln")
        print("2. 编译项目生成 demo.exe")
        print("3. 运行: demo.exe --file=config/config.ini")
        return False
    
    # 加载配置
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "bin", "config", "config.ini")
    
    if not os.path.exists(config_path):
        print(f"❌ 错误：找不到配置文件: {config_path}")
        return False
    
    try:
        config = load_config(config_path)
        print(f"\n✓ 成功加载配置文件: {config_path}")
        print(f"  账户: {config['account']}")
        print(f"  账户类型: {chr(config['acct_type'])} ({'现货' if config['acct_type'] == OX_ACCOUNT_STOCK else '其他'})")
        print(f"  上海交易账户: {config['sh_trade_account']}")
        print(f"  深圳交易账户: {config['sz_trade_account']}")
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return False
    
    # 尝试初始化 API
    try:
        api_wrapper = OXTradeApi()
        print(f"\n✓ 成功加载 DLL 文件")
        
        # 创建 API 实例
        api_ptr = api_wrapper.create_api()
        print(f"✓ 成功创建 API 实例")
        
        # 初始化 API
        init_result, error_info = api_wrapper.init(api_ptr)
        if init_result != 0:
            print(f"⚠️  API 初始化返回: {init_result}")
            if error_info:
                print(f"   错误信息: {error_info}")
        else:
            print(f"✓ API 初始化成功")
        
        # 尝试登录
        print(f"\n正在尝试登录...")
        login_result = api_wrapper.login(
            api_ptr,
            config['account'],
            config['password'],
            config['acct_type']
        )
        
        print(f"登录请求返回: {login_result}")
        print(f"\n注意：登录结果需要通过回调函数 OnRspLogon 获取。")
        print(f"请等待几秒钟查看登录回调结果...")
        
        # 等待一段时间以便接收回调
        import time
        time.sleep(3)
        
        # 停止 API
        api_wrapper.stop(api_ptr)
        api_wrapper.release_api(api_ptr)
        print(f"\n✓ API 已停止并释放")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except RuntimeError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)

