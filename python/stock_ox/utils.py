"""
工具函数模块

提供字符串编码转换、结构体序列化、价格格式化等工具函数。
"""

from typing import Union, Optional
import struct


def encode_str(s: str, encoding: str = 'gbk') -> bytes:
    """将字符串编码为指定编码的字节串
    
    Args:
        s: 要编码的字符串
        encoding: 编码格式，默认 'gbk'（C++ DLL 使用 GBK）
    
    Returns:
        编码后的字节串
        
    Example:
        >>> encode_str('测试')
        b'\\xb2\\xe2\\xca\\xd4'
    """
    if not isinstance(s, str):
        s = str(s)
    return s.encode(encoding)


def decode_str(b: Union[bytes, bytearray], encoding: str = 'gbk') -> str:
    """将字节串解码为指定编码的字符串
    
    Args:
        b: 要解码的字节串或字节数组
        encoding: 编码格式，默认 'gbk'（C++ DLL 使用 GBK）
    
    Returns:
        解码后的字符串（去除末尾的空字符和换行符）
        
    Example:
        >>> decode_str(b'\\xb2\\xe2\\xca\\xd4\\x00')
        '测试'
    """
    if not isinstance(b, (bytes, bytearray)):
        b = bytes(b)
    
    # 解码并去除空字符
    try:
        result = b.decode(encoding).rstrip('\x00\n\r')
    except UnicodeDecodeError:
        # 如果解码失败，尝试 UTF-8
        try:
            result = b.decode('utf-8').rstrip('\x00\n\r')
        except UnicodeDecodeError:
            # 最后尝试 latin-1（单字节编码，不会失败）
            result = b.decode('latin-1').rstrip('\x00\n\r')
    
    return result


def format_price(price: Union[float, str], precision: int = 2) -> str:
    """格式化价格为字符串
    
    Args:
        price: 价格，可以是浮点数或字符串
        precision: 小数位数，默认 2
    
    Returns:
        格式化后的价格字符串
        
    Example:
        >>> format_price(10.5)
        '10.50'
        >>> format_price(10.123, 3)
        '10.123'
    """
    if isinstance(price, str):
        try:
            price = float(price)
        except ValueError:
            return price
    
    return f"{price:.{precision}f}"


def parse_price(price_str: str) -> float:
    """解析价格字符串为浮点数
    
    Args:
        price_str: 价格字符串
    
    Returns:
        浮点数价格
        
    Example:
        >>> parse_price('10.50')
        10.5
        >>> parse_price('10')
        10.0
    """
    if not price_str or price_str.strip() == '':
        return 0.0
    
    try:
        return float(price_str.strip())
    except ValueError:
        return 0.0


def format_quantity(quantity: Union[int, str]) -> str:
    """格式化数量为字符串（整数，无小数）
    
    Args:
        quantity: 数量，可以是整数或字符串
    
    Returns:
        格式化后的数量字符串
        
    Example:
        >>> format_quantity(100)
        '100'
        >>> format_quantity('100')
        '100'
    """
    if isinstance(quantity, str):
        try:
            quantity = int(quantity)
        except ValueError:
            return quantity
    
    return str(int(quantity))


def parse_quantity(quantity_str: str) -> int:
    """解析数量字符串为整数
    
    Args:
        quantity_str: 数量字符串
    
    Returns:
        整数数量
        
    Example:
        >>> parse_quantity('100')
        100
        >>> parse_quantity('100.5')
        100
    """
    if not quantity_str or quantity_str.strip() == '':
        return 0
    
    try:
        return int(float(quantity_str.strip()))
    except ValueError:
        return 0


def pad_string(s: str, length: int, padding: str = '\x00', encoding: str = 'gbk') -> bytes:
    """将字符串填充到指定长度
    
    Args:
        s: 要填充的字符串
        length: 目标长度（字节数）
        padding: 填充字符，默认 '\x00'
        encoding: 编码格式，默认 'gbk'
    
    Returns:
        填充后的字节串
        
    Example:
        >>> pad_string('test', 10)
        b'test\\x00\\x00\\x00\\x00\\x00\\x00'
    """
    if not isinstance(s, str):
        s = str(s)
    
    encoded = s.encode(encoding)
    if len(encoded) >= length:
        return encoded[:length]
    
    padding_bytes = padding.encode(encoding) if isinstance(padding, str) else padding
    return encoded + padding_bytes * (length - len(encoded))


def truncate_string(s: str, length: int, encoding: str = 'gbk') -> str:
    """截断字符串到指定字节长度
    
    Args:
        s: 要截断的字符串
        length: 目标字节长度
        encoding: 编码格式，默认 'gbk'
    
    Returns:
        截断后的字符串
        
    Example:
        >>> truncate_string('测试测试', 4, 'gbk')
        '测试'
    """
    if not isinstance(s, str):
        s = str(s)
    
    encoded = s.encode(encoding)
    if len(encoded) <= length:
        return s
    
    # 截断到指定长度（可能需要调整以保持字符完整性）
    truncated = encoded[:length]
    try:
        return truncated.decode(encoding).rstrip('\x00')
    except UnicodeDecodeError:
        # 如果截断导致字符不完整，尝试减少一个字节
        if length > 0:
            truncated = encoded[:length - 1]
            try:
                return truncated.decode(encoding).rstrip('\x00')
            except UnicodeDecodeError:
                return ''
        return ''


def struct_to_dict(struct_obj, exclude_none: bool = True) -> dict:
    """将 ctypes 结构体转换为字典
    
    Args:
        struct_obj: ctypes.Structure 实例
        exclude_none: 是否排除 None 值，默认 True
    
    Returns:
        字典表示的结构体数据
    """
    if hasattr(struct_obj, 'to_dict'):
        return struct_obj.to_dict()
    
    result = {}
    for field_name, _ in struct_obj._fields_:
        value = getattr(struct_obj, field_name, None)
        if exclude_none and value is None:
            continue
        
        # 处理字节串
        if isinstance(value, (bytes, bytearray)):
            value = decode_str(value)
        
        result[field_name] = value
    
    return result


def safe_int(value: Optional[Union[str, int, float]]) -> int:
    """安全地将值转换为整数
    
    Args:
        value: 要转换的值
    
    Returns:
        整数，如果转换失败返回 0
    """
    if value is None:
        return 0
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, float):
        return int(value)
    
    if isinstance(value, str):
        try:
            return int(float(value.strip()))
        except (ValueError, AttributeError):
            return 0
    
    return 0


def safe_float(value: Optional[Union[str, int, float]]) -> float:
    """安全地将值转换为浮点数
    
    Args:
        value: 要转换的值
    
    Returns:
        浮点数，如果转换失败返回 0.0
    """
    if value is None:
        return 0.0
    
    if isinstance(value, float):
        return value
    
    if isinstance(value, int):
        return float(value)
    
    if isinstance(value, str):
        try:
            return float(value.strip())
        except (ValueError, AttributeError):
            return 0.0
    
    return 0.0
