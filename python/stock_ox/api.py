"""
核心 API 模块

封装 GuosenOXTradeApi 类，提供 Pythonic 的 API 接口。
"""

from typing import Optional
from .dll_loader import load_dll, get_create_api_func, get_release_api_func
from .spi import OXTradeSpi
from .types import AccountType
from .exceptions import OXDllError, OXConnectionError


class OXTradeApi:
    """OX 交易 API 主类"""
    
    def __init__(self, config_path: Optional[str] = None, dll_path: Optional[str] = None):
        """初始化 API 实例
        
        Args:
            config_path: 配置文件路径（可选）
            dll_path: DLL 文件路径（可选，自动查找）
        """
        self.dll = None
        self.api_ptr = None
        self.dll_path = dll_path
        self.config_path = config_path
        self.spi: Optional[OXTradeSpi] = None
        self._initialized = False
    
    def init(self) -> bool:
        """初始化 API
        
        Returns:
            是否初始化成功
        
        Raises:
            OXDllError: 如果 DLL 加载失败
            OXConnectionError: 如果初始化失败
        """
        try:
            # 加载 DLL
            self.dll = load_dll(self.dll_path)
            
            # 获取函数指针
            create_func = get_create_api_func(self.dll)
            
            # 创建 API 实例
            self.api_ptr = create_func()
            
            if self.api_ptr is None:
                raise OXConnectionError("Failed to create API instance")
            
            self._initialized = True
            return True
            
        except Exception as e:
            raise OXConnectionError(f"API initialization failed: {e}") from e
    
    def stop(self) -> None:
        """停止 API"""
        if self.api_ptr and self.dll:
            release_func = get_release_api_func(self.dll)
            release_func(self.api_ptr)
            self.api_ptr = None
        
        self._initialized = False
    
    def register_spi(self, spi: OXTradeSpi) -> None:
        """注册回调接口
        
        Args:
            spi: 回调接口实例
        """
        self.spi = spi
        # 实际注册逻辑将在后续开发中添加
    
    def login(self, account: str, password: str, 
              account_type: AccountType = AccountType.STOCK) -> bool:
        """用户登录
        
        Args:
            account: 资金账号
            password: 密码
            account_type: 账户类型
        
        Returns:
            是否登录成功
        
        Raises:
            OXConnectionError: 如果 API 未初始化
        """
        if not self._initialized:
            raise OXConnectionError("API not initialized, call init() first")
        
        # 实际登录逻辑将在后续开发中添加
        return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()

