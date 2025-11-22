# API 参考文档

本文档提供了 stock_ox API 的完整参考。

## 目录

1. [核心 API](#核心-api)
2. [回调接口](#回调接口)
3. [数据类型](#数据类型)
4. [常量定义](#常量定义)
5. [异常定义](#异常定义)

## 核心 API

### OXTradeApi

主要的 API 类，提供所有交易功能。

#### 初始化

```python
api = OXTradeApi(config_path=None, dll_path=None)
```

**参数：**
- `config_path` (str, optional): 配置文件路径
- `dll_path` (str, optional): DLL 文件路径，如果为 None 则自动查找

#### 方法

##### `init(err_msg=None) -> int`

初始化 API。

**参数：**
- `err_msg` (list, optional): 错误消息列表，如果提供，初始化失败时会填充错误消息

**返回：**
- `int`: 返回码，0 表示成功，非 0 表示失败

**异常：**
- `OXDllError`: DLL 加载失败
- `OXConnectionError`: 初始化失败

##### `stop() -> None`

停止 API。

##### `register_spi(spi: OXTradeSpi) -> None`

注册回调接口。

**参数：**
- `spi` (OXTradeSpi): 回调接口实例

##### `login(account: str, password: str, account_type: AccountType, timeout: float = 5.0) -> bool`

登录账户。

**参数：**
- `account` (str): 账户号码
- `password` (str): 密码
- `account_type` (AccountType): 账户类型
- `timeout` (float): 超时时间（秒），默认 5.0

**返回：**
- `bool`: True 表示登录成功，False 表示登录失败

**异常：**
- `OXConnectionError`: API 未初始化或连接错误
- `OXLoginError`: 登录失败

##### `order(trdacct: str, board_id: str, symbol: str, price: float, quantity: int, stk_biz: int = 100, stk_biz_action: int = 100, order_ref: str = '', trd_code_cls: str = '', trd_ex_info: str = '') -> int`

下单。

**参数：**
- `trdacct` (str): 股东账号
- `board_id` (str): 交易板块（如 "10" 表示上海，"00" 表示深圳）
- `symbol` (str): 证券代码
- `price` (float): 委托价格（市价单为 0）
- `quantity` (int): 委托数量
- `stk_biz` (int): 证券业务（100 表示买入，101 表示卖出）
- `stk_biz_action` (int): 证券业务指令（100 表示限价单，121 表示市价单）
- `order_ref` (str, optional): 客户委托信息
- `trd_code_cls` (str, optional): 交易代码类别
- `trd_ex_info` (str, optional): 交易扩展信息

**返回：**
- `int`: 请求编号

**异常：**
- `OXConnectionError`: API 未初始化或未登录
- `OXOrderError`: 下单请求失败

##### `cancel(board_id: str, order_no: int, order_date: Optional[int] = None) -> int`

撤单。

**参数：**
- `board_id` (str): 交易板块
- `order_no` (int): 委托编号
- `order_date` (int, optional): 委托日期（格式：YYYYMMDD），如果不提供则使用当前日期

**返回：**
- `int`: 请求编号

**异常：**
- `OXConnectionError`: API 未初始化或未登录
- `OXOrderError`: 撤单请求失败

##### `batch_order(order_list: List[Dict[str, Any]], stk_biz: int, stk_biz_action: int) -> int`

批量下单。

**参数：**
- `order_list` (List[Dict]): 订单列表，每个元素包含订单信息
- `stk_biz` (int): 证券业务
- `stk_biz_action` (int): 证券业务指令

**返回：**
- `int`: 请求编号

**异常：**
- `OXConnectionError`: API 未初始化或未登录
- `OXOrderError`: 批量下单请求失败或订单列表为空/超出限制

##### `is_initialized() -> bool`

检查 API 是否已初始化。

**返回：**
- `bool`: True 表示已初始化，False 表示未初始化

##### `is_logged_in() -> bool`

检查是否已登录。

**返回：**
- `bool`: True 表示已登录，False 表示未登录

#### 上下文管理器

`OXTradeApi` 支持上下文管理器：

```python
with OXTradeApi() as api:
    # 使用 API
    pass
# API 自动停止
```

## 回调接口

### OXTradeSpi

回调接口基类，用户应该继承此类并重写需要处理的回调方法。

#### 方法

##### `on_connected() -> int`

连接建立回调。

**返回：**
- `int`: 0 表示成功

##### `on_disconnected() -> int`

连接断开回调。

**返回：**
- `int`: 0 表示成功

##### `on_rsp_logon(request: int, error: Optional[Dict], is_last: bool, field: Optional[Dict]) -> None`

登录响应回调。

**参数：**
- `request` (int): 请求编号
- `error` (Dict, optional): 错误信息字典（如果发生错误），None 表示无错误
- `is_last` (bool): 是否最后一条
- `field` (Dict, optional): 响应字段字典（成功时），None 表示无数据

##### `on_rtn_order(field: Optional[Dict]) -> None`

委托回报回调。

**参数：**
- `field` (Dict, optional): 委托回报字段字典，None 表示无数据

##### `on_rtn_order_filled(field: Optional[Dict]) -> None`

成交回报回调。

**参数：**
- `field` (Dict, optional): 成交回报字段字典，None 表示无数据

##### `on_rsp_cancel_ticket(request: int, error: Optional[Dict], field: Optional[Dict]) -> None`

撤单响应回调。

**参数：**
- `request` (int): 请求编号
- `error` (Dict, optional): 错误信息字典（如果发生错误），None 表示无错误
- `field` (Dict, optional): 响应字段字典（成功时），None 表示无数据

##### `on_rsp_batch_order(request: int, error: Optional[Dict], field: Optional[Dict]) -> None`

批量下单响应回调。

**参数：**
- `request` (int): 请求编号
- `error` (Dict, optional): 错误信息字典（如果发生错误），None 表示无错误
- `field` (Dict, optional): 响应字段字典（成功时），None 表示无数据

## 数据类型

### AccountType

账户类型枚举。

**值：**
- `STOCK` - 现货账户（0）
- `OPTION` - 期权账户（1）
- `FUTURES` - 期货账户（2）
- `CREDIT` - 信用账户（3）

**使用示例：**

```python
from stock_ox.types import AccountType

account_type = AccountType.STOCK
```

### OrderState

委托状态枚举。

**值：**
- `NOT_REPORT` - 未报
- `REPORTED` - 已报
- `PARTIALLY_FILLED` - 部分成交
- `FILLED` - 全部成交
- `CANCELLED` - 已撤
- `REJECTED` - 已拒绝

**使用示例：**

```python
from stock_ox.types import OrderState

state = OrderState.FILLED
```

### ExchangeId

交易所 ID 枚举。

**值：**
- `SHANGHAI` - 上海交易所（'1'）
- `SHENZHEN` - 深圳交易所（'2'）

**使用示例：**

```python
from stock_ox.types import ExchangeId

exchange = ExchangeId.SHANGHAI
```

## 常量定义

### 交易板块

```python
from stock_ox.constants import BOARD_SH, BOARD_SZ

BOARD_SH = "10"  # 上海交易所
BOARD_SZ = "00"  # 深圳交易所
```

### 证券业务

```python
from stock_ox.constants import STK_BIZ_BUY, STK_BIZ_SELL

STK_BIZ_BUY = 100   # 买入
STK_BIZ_SELL = 101  # 卖出
```

### 委托类型

```python
from stock_ox.constants import ORDER_TYPE_LIMIT, ORDER_TYPE_MKT

ORDER_TYPE_LIMIT = 100  # 限价单
ORDER_TYPE_MKT = 121    # 市价单
```

### 其他常量

查看 `stock_ox/constants.py` 获取完整的常量定义。

## 异常定义

### OXApiError

所有 API 异常的基类。

### OXDllError

DLL 相关错误。

### OXConnectionError

连接相关错误（API 未初始化、未登录等）。

### OXLoginError

登录相关错误。

### OXOrderError

交易相关错误（下单失败、撤单失败等）。

### OXQueryError

查询相关错误（查询功能实现后使用）。

**使用示例：**

```python
from stock_ox.exceptions import (
    OXConnectionError,
    OXLoginError,
    OXOrderError
)

try:
    api.order(...)
except OXConnectionError as e:
    print(f"连接错误: {e}")
except OXOrderError as e:
    print(f"交易错误: {e}")
```

## 数据结构

所有数据结构定义在 `stock_ox/structs.py` 中。这些结构体主要用于与 C++ DLL 交互，通常不需要直接使用。

如需详细了解数据结构，请查看源代码或 C++ API 文档。

## 工具函数

工具函数定义在 `stock_ox/utils.py` 中，主要用于内部使用。如需使用，请参考源代码。

## 更多信息

- 查看 [快速入门指南](QUICKSTART.md)
- 查看 [完整使用示例](USAGE_EXAMPLES.md)
- 查看 [常见问题解答](FAQ.md)
- 查看源代码：`stock_ox/` 目录

