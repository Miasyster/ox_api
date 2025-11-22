"""
工具函数模块

提供字符串编码转换、结构体序列化等工具函数。
"""


def encode_str(s: str, encoding: str = 'gbk') -> bytes:
    """将字符串编码为指定编码的字节串
    
    Args:
        s: 要编码的字符串
        encoding: 编码格式，默认 'gbk'
    
    Returns:
        编码后的字节串
    """
    return s.encode(encoding)


def decode_str(b: bytes, encoding: str = 'gbk') -> str:
    """将字节串解码为指定编码的字符串
    
    Args:
        b: 要解码的字节串
        encoding: 编码格式，默认 'gbk'
    
    Returns:
        解码后的字符串（去除末尾的空字符）
    """
    if not isinstance(b, bytes):
        b = bytes(b)
    return b.decode(encoding).rstrip('\x00')


def format_price(price: float, precision: int = 2) -> str:
    """格式化价格为字符串
    
    Args:
        price: 价格
        precision: 小数位数，默认 2
    
    Returns:
        格式化后的价格字符串
    """
    return f"{price:.{precision}f}"

