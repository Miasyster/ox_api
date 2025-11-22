"""
DLL 加载器模块

负责加载 GuosenOXAPI.dll 并定义 C 函数签名。
"""

import os
import sys
from ctypes import CDLL, POINTER, c_char_p, c_void_p, c_int
from typing import Optional, Callable

from .exceptions import OXDllError

# Windows 调用约定
if sys.platform == 'win32':
    from ctypes import windll, WINFUNCTYPE
else:
    # 非 Windows 平台使用标准调用约定
    from ctypes import CFUNCTYPE
    WINFUNCTYPE = CFUNCTYPE
    # 非 Windows 平台模拟 windll
    windll = None


def find_dll_path() -> Optional[str]:
    """查找 DLL 文件路径
    
    按以下顺序查找 DLL 文件：
    1. 项目根目录的 bin/ 目录
    2. 当前工作目录
    3. 系统路径
    
    Returns:
        DLL 文件路径，如果未找到返回 None
    """
    # 获取项目根目录（向上两级：python/stock_ox/ -> python/ -> stock_ox/）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # 可能的 DLL 路径列表
    dll_paths = [
        os.path.join(project_root, 'bin', 'GuosenOXAPI.dll'),  # 项目根目录/bin/
        os.path.join(current_dir, 'bin', 'GuosenOXAPI.dll'),   # 当前目录/bin/
        'GuosenOXAPI.dll',  # 当前目录或系统路径
        os.path.join(os.getcwd(), 'bin', 'GuosenOXAPI.dll'),   # 工作目录/bin/
    ]
    
    # 遍历所有可能的路径
    for path in dll_paths:
        full_path = os.path.abspath(path) if not os.path.isabs(path) else path
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return full_path
    
    return None


def load_dll(dll_path: Optional[str] = None) -> CDLL:
    """加载 DLL 文件
    
    Args:
        dll_path: DLL 文件路径，如果为 None 则自动查找
    
    Returns:
        加载的 CDLL 对象
    
    Raises:
        OXDllError: 如果 DLL 加载失败或文件不存在
    """
    if dll_path is None:
        dll_path = find_dll_path()
    
    if dll_path is None:
        raise OXDllError("DLL file not found. Please specify the path to GuosenOXAPI.dll")
    
    if not os.path.exists(dll_path):
        raise OXDllError(f"DLL file not found: {dll_path}")
    
    if not os.path.isfile(dll_path):
        raise OXDllError(f"Path is not a file: {dll_path}")
    
    try:
        # 在 Windows 上使用 windll，其他平台使用 CDLL
        if sys.platform == 'win32' and windll is not None:
            dll = windll.LoadLibrary(dll_path)
        else:
            # 非 Windows 平台尝试加载（可能会失败，但用于测试）
            dll = CDLL(dll_path)
        return dll
    except OSError as e:
        error_msg = f"Failed to load DLL '{dll_path}': {e}"
        if sys.platform != 'win32':
            error_msg += " (Note: DLL files are only supported on Windows)"
        raise OXDllError(error_msg) from e


def get_create_api_func(dll: CDLL) -> Callable:
    """获取创建 API 实例的函数
    
    函数签名：GuosenOXTradeApi* gxCreateTradeApi()
    调用约定：__stdcall (Windows)
    
    Args:
        dll: 加载的 CDLL 对象
    
    Returns:
        创建 API 的函数，返回 API 实例指针（c_void_p）
    
    Raises:
        OXDllError: 如果函数未找到
    """
    func = getattr(dll, 'gxCreateTradeApi', None)
    if func is None:
        # 尝试不同的函数名格式
        for name in ['gxCreateTradeApi', '_gxCreateTradeApi', 'gxCreateTradeApi@0']:
            func = getattr(dll, name, None)
            if func is not None:
                break
        
        if func is None:
            raise OXDllError("Function gxCreateTradeApi not found in DLL")
    
    # 设置函数签名
    # 返回类型：GuosenOXTradeApi* (void pointer)
    func.restype = c_void_p
    # 参数类型：无参数
    func.argtypes = []
    
    # 设置调用约定（Windows 上使用 __stdcall）
    if sys.platform == 'win32' and hasattr(func, '_FuncPtr'):
        # __stdcall 调用约定
        func.argtypes = []
        func.restype = c_void_p
    
    return func


def get_release_api_func(dll: CDLL) -> Callable:
    """获取释放 API 实例的函数
    
    函数签名：void gxReleaseTradeApi(GuosenOXTradeApi *pApiObj)
    调用约定：__stdcall (Windows)
    
    Args:
        dll: 加载的 CDLL 对象
    
    Returns:
        释放 API 的函数，接受 API 实例指针作为参数
    
    Raises:
        OXDllError: 如果函数未找到
    """
    func = getattr(dll, 'gxReleaseTradeApi', None)
    if func is None:
        # 尝试不同的函数名格式
        for name in ['gxReleaseTradeApi', '_gxReleaseTradeApi', 'gxReleaseTradeApi@4']:
            func = getattr(dll, name, None)
            if func is not None:
                break
        
        if func is None:
            raise OXDllError("Function gxReleaseTradeApi not found in DLL")
    
    # 设置函数签名
    # 返回类型：void (None)
    func.restype = None
    # 参数类型：GuosenOXTradeApi* (void pointer)
    func.argtypes = [c_void_p]
    
    # 设置调用约定（Windows 上使用 __stdcall）
    if sys.platform == 'win32' and hasattr(func, '_FuncPtr'):
        func.restype = None
        func.argtypes = [c_void_p]
    
    return func


class DLLoader:
    """DLL 加载器类，封装 DLL 加载和函数获取功能"""
    
    def __init__(self, dll_path: Optional[str] = None):
        """初始化 DLL 加载器
        
        Args:
            dll_path: DLL 文件路径，如果为 None 则自动查找
        """
        self.dll_path = dll_path
        self.dll: Optional[CDLL] = None
        self.create_api_func: Optional[Callable] = None
        self.release_api_func: Optional[Callable] = None
        self._is_loaded = False
    
    def load(self) -> 'DLLoader':
        """加载 DLL 并获取函数指针
        
        Returns:
            self，支持链式调用
        
        Raises:
            OXDllError: 如果 DLL 加载失败
        """
        if self._is_loaded:
            return self
        
        self.dll = load_dll(self.dll_path)
        self.create_api_func = get_create_api_func(self.dll)
        self.release_api_func = get_release_api_func(self.dll)
        self._is_loaded = True
        return self
    
    def create_api(self) -> c_void_p:
        """创建 API 实例
        
        Returns:
            API 实例指针（c_void_p）
        
        Raises:
            OXDllError: 如果 DLL 未加载或函数调用失败
        """
        if not self._is_loaded:
            raise OXDllError("DLL not loaded. Call load() first.")
        
        if self.create_api_func is None:
            raise OXDllError("Create API function not available")
        
        try:
            api_ptr = self.create_api_func()
            return api_ptr
        except Exception as e:
            raise OXDllError(f"Failed to create API instance: {e}") from e
    
    def release_api(self, api_ptr: c_void_p) -> None:
        """释放 API 实例
        
        Args:
            api_ptr: API 实例指针
        
        Raises:
            OXDllError: 如果 DLL 未加载或函数调用失败
        """
        if not self._is_loaded:
            raise OXDllError("DLL not loaded. Call load() first.")
        
        if self.release_api_func is None:
            raise OXDllError("Release API function not available")
        
        if api_ptr is None or api_ptr == 0:
            raise OXDllError("Invalid API pointer")
        
        try:
            self.release_api_func(api_ptr)
        except Exception as e:
            raise OXDllError(f"Failed to release API instance: {e}") from e
    
    def is_loaded(self) -> bool:
        """检查 DLL 是否已加载
        
        Returns:
            如果 DLL 已加载返回 True，否则返回 False
        """
        return self._is_loaded
    
    def __enter__(self):
        """上下文管理器入口"""
        self.load()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # DLL 加载器不需要清理资源
        pass

