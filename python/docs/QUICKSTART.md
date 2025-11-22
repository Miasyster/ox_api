# 快速入门指南

本指南将帮助您快速开始使用 stock_ox API。

## 安装

### 从源码安装

```bash
cd python
pip install -e .
```

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

## 基础使用

### 1. 创建 API 实例

```python
from stock_ox import OXTradeApi

api = OXTradeApi()
```

### 2. 初始化 API

```python
api.init()
```

### 3. 创建并注册回调接口

```python
from stock_ox.spi import OXTradeSpi

class MySpi(OXTradeSpi):
    def on_rsp_logon(self, request, error, is_last, field):
        if error:
            print(f"登录失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"登录成功: Account={field.get('Account', '')}")

spi = MySpi()
api.register_spi(spi)
```

### 4. 登录账户

```python
from stock_ox.types import AccountType

api.login(
    account="110060035050",
    password="111111",
    account_type=AccountType.STOCK,
    timeout=5.0
)
```

### 5. 下单

```python
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, BOARD_SH

request_id = api.order(
    trdacct='A197407210',      # 股东账号
    board_id=BOARD_SH,          # 交易板块（上海）
    symbol='600000',            # 证券代码
    price=10.50,                # 委托价格
    quantity=100,               # 委托数量
    stk_biz=STK_BIZ_BUY,       # 买入
    stk_biz_action=ORDER_TYPE_LIMIT  # 限价单
)
```

### 6. 接收委托回报

在您的 SPI 类中实现 `on_rtn_order` 方法：

```python
def on_rtn_order(self, field):
    if field:
        print(f"委托编号: {field.get('OrderNo', '')}")
        print(f"证券代码: {field.get('Symbol', '')}")
        print(f"委托数量: {field.get('OrderQty', 0)}")
        print(f"委托价格: {field.get('OrderPrice', '0')}")
        print(f"委托状态: {field.get('OrderState', '')}")
```

### 7. 撤单

```python
order_no = 123456789012345  # 委托编号
request_id = api.cancel(
    board_id=BOARD_SH,
    order_no=order_no
)
```

### 8. 停止 API

```python
api.stop()
```

## 使用上下文管理器（推荐）

推荐使用上下文管理器来管理 API 生命周期：

```python
with OXTradeApi() as api:
    spi = MySpi()
    api.register_spi(spi)
    api.login(account, password, account_type)
    # ... 进行交易操作 ...
# API 自动停止
```

## 完整示例

```python
from stock_ox import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, BOARD_SH

class MySpi(OXTradeSpi):
    def on_rsp_logon(self, request, error, is_last, field):
        if error:
            print(f"登录失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"登录成功: Account={field.get('Account', '')}")
    
    def on_rtn_order(self, field):
        if field:
            print(f"委托回报: {field.get('Symbol', '')} x {field.get('OrderQty', 0)}")
    
    def on_rtn_order_filled(self, field):
        if field:
            print(f"成交回报: {field.get('Symbol', '')} x {field.get('FilledQty', 0)}")
    
    def on_rsp_cancel_ticket(self, request, error, field):
        if error:
            print(f"撤单失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"撤单成功")

def main():
    api = OXTradeApi()
    spi = MySpi()
    
    try:
        api.init()
        api.register_spi(spi)
        api.login("110060035050", "111111", AccountType.STOCK, timeout=5.0)
        
        # 下单
        request_id = api.order(
            trdacct='A197407210',
            board_id=BOARD_SH,
            symbol='600000',
            price=10.50,
            quantity=100,
            stk_biz=STK_BIZ_BUY
        )
        print(f"下单成功，请求编号: {request_id}")
        
        # 等待回报
        import time
        time.sleep(1.0)
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        api.stop()

if __name__ == "__main__":
    main()
```

## 更多示例

查看 `examples/` 目录获取更多示例代码：

- `trading_example.py` - 完整的交易流程示例
- `order_example.py` - 下单功能示例
- `query_example.py` - 查询功能示例（待实现）

## 下一步

- 阅读 [完整使用示例](USAGE_EXAMPLES.md)
- 查看 [API 参考文档](API_REFERENCE.md)
- 查看 [常见问题解答](FAQ.md)

