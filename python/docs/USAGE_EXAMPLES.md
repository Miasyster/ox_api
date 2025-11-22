# 完整使用示例

本文档提供了 stock_ox API 的完整使用示例。

## 目录

1. [基础交易流程](#基础交易流程)
2. [下单操作](#下单操作)
3. [撤单操作](#撤单操作)
4. [批量下单](#批量下单)
5. [接收回调](#接收回调)
6. [错误处理](#错误处理)
7. [使用上下文管理器](#使用上下文管理器)

## 基础交易流程

### 完整的交易流程示例

```python
from stock_ox import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, BOARD_SH
import time

class TradingSpi(OXTradeSpi):
    def __init__(self):
        super().__init__()
        self.order_callbacks = []
        self.filled_callbacks = []
        self.cancel_callbacks = []
    
    def on_rsp_logon(self, request, error, is_last, field):
        """登录响应回调"""
        if error:
            print(f"❌ 登录失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"✅ 登录成功: Account={field.get('Account', '')}")
    
    def on_rtn_order(self, field):
        """委托回报回调"""
        if field:
            self.order_callbacks.append(field)
            print(f"📋 委托回报: {field.get('Symbol', '')} x {field.get('OrderQty', 0)}")
    
    def on_rtn_order_filled(self, field):
        """成交回报回调"""
        if field:
            self.filled_callbacks.append(field)
            print(f"💰 成交回报: {field.get('Symbol', '')} x {field.get('FilledQty', 0)} @ {field.get('FilledPrice', '0')}")
    
    def on_rsp_cancel_ticket(self, request, error, field):
        """撤单响应回调"""
        self.cancel_callbacks.append({'request': request, 'error': error, 'field': field})
        if error:
            print(f"❌ 撤单失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"✅ 撤单成功")

# 创建 API 实例
api = OXTradeApi()
spi = TradingSpi()

try:
    # 1. 初始化 API
    print("[步骤 1] 初始化 API...")
    api.init()
    print("✓ API 初始化成功")
    
    # 2. 注册回调接口
    print("[步骤 2] 注册回调接口...")
    api.register_spi(spi)
    print("✓ 回调接口注册成功")
    
    # 3. 登录账户
    print("[步骤 3] 登录账户...")
    api.login("110060035050", "111111", AccountType.STOCK, timeout=5.0)
    print("✓ 账户登录成功")
    
    # 4. 下单
    print("[步骤 4] 下单...")
    request_id = api.order(
        trdacct='A197407210',
        board_id=BOARD_SH,
        symbol='600000',
        price=10.50,
        quantity=100,
        stk_biz=STK_BIZ_BUY,
        stk_biz_action=ORDER_TYPE_LIMIT
    )
    print(f"✓ 下单成功，请求编号: {request_id}")
    
    # 5. 等待回报
    print("[步骤 5] 等待回报...")
    time.sleep(1.0)
    
    # 6. 撤单
    print("[步骤 6] 撤单...")
    order_no = 123456789012345  # 从委托回报中获取
    cancel_request_id = api.cancel(BOARD_SH, order_no)
    print(f"✓ 撤单请求已发送，请求编号: {cancel_request_id}")
    
    # 7. 等待撤单响应
    time.sleep(0.5)
    
except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    # 8. 停止 API
    print("[清理] 停止 API...")
    api.stop()
    print("✓ API 已停止")
```

## 下单操作

### 限价单

```python
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, BOARD_SH

request_id = api.order(
    trdacct='A197407210',      # 股东账号
    board_id=BOARD_SH,          # 交易板块（上海）
    symbol='600000',            # 证券代码
    price=10.50,                # 委托价格
    quantity=100,               # 委托数量
    stk_biz=STK_BIZ_BUY,       # 买入
    stk_biz_action=ORDER_TYPE_LIMIT,  # 限价单
    order_ref='ORDER001'        # 客户委托信息（可选）
)
```

### 市价单

```python
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_MKT, BOARD_SH

request_id = api.order(
    trdacct='A197407210',
    board_id=BOARD_SH,
    symbol='600000',
    price=0,                    # 市价单价格为 0
    quantity=100,
    stk_biz=STK_BIZ_BUY,
    stk_biz_action=ORDER_TYPE_MKT  # 市价单
)
```

### 卖出

```python
from stock_ox.constants import STK_BIZ_SELL, ORDER_TYPE_LIMIT, BOARD_SH

request_id = api.order(
    trdacct='A197407210',
    board_id=BOARD_SH,
    symbol='600000',
    price=10.50,
    quantity=100,
    stk_biz=STK_BIZ_SELL,      # 卖出
    stk_biz_action=ORDER_TYPE_LIMIT
)
```

### 不同交易板块

```python
from stock_ox.constants import BOARD_SH, BOARD_SZ

# 上海市场
request_id_sh = api.order(
    trdacct='A197407210',
    board_id=BOARD_SH,          # 上海
    symbol='600000',
    price=10.50,
    quantity=100
)

# 深圳市场
request_id_sz = api.order(
    trdacct='0000035074',
    board_id=BOARD_SZ,          # 深圳
    symbol='000001',
    price=12.00,
    quantity=100
)
```

## 撤单操作

### 基本撤单

```python
# 撤单需要委托编号和交易板块
order_no = 123456789012345  # 从委托回报中获取
board_id = BOARD_SH

request_id = api.cancel(board_id, order_no)
```

### 指定委托日期撤单

```python
from datetime import date

today = date.today()
order_date = today.year * 10000 + today.month * 100 + today.day

request_id = api.cancel(
    board_id=BOARD_SH,
    order_no=123456789012345,
    order_date=order_date  # 可选，默认使用当前日期
)
```

## 批量下单

```python
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT

# 准备订单列表
order_list = [
    {
        'Trdacct': 'A197407210',
        'BoardId': BOARD_SH,
        'Symbol': '600000',
        'OrderPrice': 10.50,
        'OrderQty': 100,
        'OrderRef': 'BATCH001',
    },
    {
        'Trdacct': 'A197407210',
        'BoardId': BOARD_SH,
        'Symbol': '600001',
        'OrderPrice': 11.00,
        'OrderQty': 200,
        'OrderRef': 'BATCH002',
    },
]

# 批量下单
request_id = api.batch_order(
    order_list=order_list,
    stk_biz=STK_BIZ_BUY,
    stk_biz_action=ORDER_TYPE_LIMIT
)

print(f"批量下单成功，请求编号: {request_id}")
```

## 接收回调

### 委托回报回调

```python
class MySpi(OXTradeSpi):
    def on_rtn_order(self, field):
        """委托回报回调"""
        if field:
            order_no = field.get('OrderNo', '')
            symbol = field.get('Symbol', '')
            order_qty = field.get('OrderQty', 0)
            order_price = field.get('OrderPrice', '0')
            order_state = field.get('OrderState', '')
            filled_qty = field.get('FilledQty', 0)
            
            print(f"委托回报:")
            print(f"  委托编号: {order_no}")
            print(f"  证券代码: {symbol}")
            print(f"  委托数量: {order_qty}")
            print(f"  委托价格: {order_price}")
            print(f"  委托状态: {order_state}")
            print(f"  成交数量: {filled_qty}")
            
            # 保存委托编号用于撤单
            self.order_no = order_no
```

### 成交回报回调

```python
def on_rtn_order_filled(self, field):
    """成交回报回调"""
    if field:
        order_no = field.get('OrderNo', '')
        symbol = field.get('Symbol', '')
        filled_qty = field.get('FilledQty', 0)
        filled_price = field.get('FilledPrice', '0')
        filled_amt = field.get('FilledAmt', '0')
        
        print(f"成交回报:")
        print(f"  委托编号: {order_no}")
        print(f"  证券代码: {symbol}")
        print(f"  成交数量: {filled_qty}")
        print(f"  成交价格: {filled_price}")
        print(f"  成交金额: {filled_amt}")
```

### 撤单响应回调

```python
def on_rsp_cancel_ticket(self, request, error, field):
    """撤单响应回调"""
    if error and error.get('ErrorId', 0) != 0:
        print(f"撤单失败: {error.get('ErrorInfo', '')}")
    else:
        print(f"撤单成功")
        if field:
            print(f"  委托编号: {field.get('OrderNo', '')}")
            print(f"  撤单状态: {field.get('OrderState', '')}")
```

## 错误处理

### 完整的错误处理示例

```python
from stock_ox.exceptions import (
    OXConnectionError,
    OXLoginError,
    OXOrderError,
    OXDllError
)

try:
    api.init()
except OXDllError as e:
    print(f"DLL 加载失败: {e}")
except OXConnectionError as e:
    print(f"连接错误: {e}")

try:
    api.login(account, password, account_type)
except OXLoginError as e:
    print(f"登录错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")

try:
    request_id = api.order(...)
except OXConnectionError as e:
    print(f"连接错误: {e}")
except OXOrderError as e:
    print(f"交易错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
finally:
    api.stop()
```

### 检查 API 状态

```python
# 检查是否已初始化
if not api.is_initialized():
    print("API 未初始化")
    api.init()

# 检查是否已登录
if not api.is_logged_in():
    print("未登录")
    api.login(account, password, account_type)
```

## 使用上下文管理器

推荐使用上下文管理器来管理 API 生命周期：

```python
from stock_ox import OXTradeApi

def main():
    spi = MySpi()
    
    # 使用上下文管理器，自动初始化和清理
    with OXTradeApi() as api:
        api.register_spi(spi)
        api.login(account, password, account_type)
        
        # 进行交易操作
        request_id = api.order(...)
        
        # 等待回报
        import time
        time.sleep(1.0)
    
    # API 自动停止，无需手动调用 stop()

if __name__ == "__main__":
    main()
```

## 更多示例

查看 `examples/` 目录获取更多示例代码：

- `trading_example.py` - 完整的交易流程示例
- `order_example.py` - 下单功能示例
- `query_example.py` - 查询功能示例（待实现）

