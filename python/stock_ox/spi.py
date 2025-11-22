"""
回调接口模块

实现回调接口的 Python 包装。
"""

from typing import Callable, Optional
from .structs import CRspErrorField


class OXTradeSpi:
    """OX 交易回调接口基类"""
    
    def on_connected(self) -> int:
        """连接建立回调
        
        Returns:
            0 表示成功
        """
        return 0
    
    def on_disconnected(self) -> int:
        """连接断开回调
        
        Returns:
            0 表示成功
        """
        return 0
    
    def on_rsp_logon(self, request: int, error: CRspErrorField, 
                     is_last: bool, field: Optional[object]) -> None:
        """登录响应回调
        
        Args:
            request: 请求编号
            error: 错误信息
            is_last: 是否最后一条
            field: 响应字段
        """
        pass
    
    # 更多回调方法将在后续开发中添加

