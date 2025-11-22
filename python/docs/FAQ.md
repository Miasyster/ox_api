# 常见问题解答（FAQ）

## 安装和配置

### Q1: 如何安装 stock_ox？

**A:** 从源码安装：

```bash
cd python
pip install -e .
```

### Q2: DLL 文件在哪里？

**A:** DLL 文件应该位于项目根目录的 `bin/` 目录下：
- `bin/GuosenOXAPI.dll` - 主要的 DLL 文件
- `bin/config/config.ini` - 配置文件

### Q3: 在非 Windows 环境下能运行吗？

**A:** 不能。DLL 文件是 Windows 专用的，只能在 Windows 环境下运行。在 macOS/Linux 环境下无法加载 DLL。

如果需要测试 API 功能，可以使用单元测试和集成测试（使用 Mock）。

## API 使用

### Q4: 如何初始化 API？

**A:** 

```python
from stock_ox import OXTradeApi

api = OXTradeApi()
api.init()
```

或使用上下文管理器（推荐）：

```python
with OXTradeApi() as api:
    # 使用 API
    pass
# API 自动停止
```

### Q5: 如何登录账户？

**A:** 

```python
from stock_ox.types import AccountType

api.login(
    account="110060035050",
    password="111111",
    account_type=AccountType.STOCK,  # 或 AccountType.CREDIT, AccountType.OPTION 等
    timeout=5.0
)
```

### Q6: 账户类型有哪些？

**A:** 支持的账户类型（`AccountType`）：
- `STOCK` - 现货账户（0）
- `OPTION` - 期权账户（1）
- `FUTURES` - 期货账户（2）
- `CREDIT` - 信用账户（3）

### Q7: 如何下单？

**A:** 

```python
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, BOARD_SH

request_id = api.order(
    trdacct='A197407210',      # 股东账号
    board_id=BOARD_SH,          # 交易板块
    symbol='600000',            # 证券代码
    price=10.50,                # 委托价格
    quantity=100,               # 委托数量
    stk_biz=STK_BIZ_BUY,       # 买入/卖出
    stk_biz_action=ORDER_TYPE_LIMIT  # 限价单/市价单
)
```

### Q8: 如何撤单？

**A:** 

```python
# 撤单需要委托编号（从委托回报中获取）和交易板块
request_id = api.cancel(
    board_id=BOARD_SH,
    order_no=123456789012345
)
```

### Q9: 如何接收委托回报和成交回报？

**A:** 实现 SPI 回调接口：

```python
from stock_ox.spi import OXTradeSpi

class MySpi(OXTradeSpi):
    def on_rtn_order(self, field):
        """委托回报回调"""
        if field:
            print(f"委托回报: {field.get('Symbol', '')}")
    
    def on_rtn_order_filled(self, field):
        """成交回报回调"""
        if field:
            print(f"成交回报: {field.get('Symbol', '')}")

# 注册 SPI
spi = MySpi()
api.register_spi(spi)
```

## 回调接口

### Q10: 什么时候会收到委托回报？

**A:** 委托回报是异步的，通常在以下情况触发：
- 下单成功后，立即收到委托回报
- 委托状态发生变化时（如部分成交、全部成交、撤单等）

### Q11: 什么时候会收到成交回报？

**A:** 成交回报是异步的，当委托有成交时触发。

### Q12: 回调函数是线程安全的吗？

**A:** 是的，API 内部的回调处理是线程安全的。但您在自己的回调函数中需要注意线程安全。

## 错误处理

### Q13: 如何处理错误？

**A:** 使用 try-except 捕获异常：

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
    print(f"DLL 错误: {e}")
except OXConnectionError as e:
    print(f"连接错误: {e}")

try:
    api.login(account, password, account_type)
except OXLoginError as e:
    print(f"登录错误: {e}")

try:
    api.order(...)
except OXConnectionError as e:
    print(f"连接错误: {e}")
except OXOrderError as e:
    print(f"交易错误: {e}")
```

### Q14: 常见错误有哪些？

**A:** 

1. **OXDllError** - DLL 加载失败
   - 检查 DLL 文件是否存在
   - 检查 DLL 文件路径是否正确

2. **OXConnectionError** - 连接错误
   - API 未初始化
   - 未登录

3. **OXLoginError** - 登录错误
   - 账户或密码错误
   - 登录超时

4. **OXOrderError** - 交易错误
   - 参数错误
   - 交易请求失败

## 配置和参数

### Q15: 如何设置账户信息？

**A:** 账户信息通常从登录响应中获取。在测试环境中，可能需要手动设置：

```python
# 在登录后，确保账户信息已设置
if not api._account:
    api._account = account
    api._acct_type = account_type
```

### Q16: 如何设置交易板块？

**A:** 使用常量：

```python
from stock_ox.constants import BOARD_SH, BOARD_SZ

# 上海市场
board_id = BOARD_SH  # "10"

# 深圳市场
board_id = BOARD_SZ  # "00"
```

### Q17: 如何设置委托类型？

**A:** 使用常量：

```python
from stock_ox.constants import ORDER_TYPE_LIMIT, ORDER_TYPE_MKT

# 限价单
stk_biz_action = ORDER_TYPE_LIMIT  # 100

# 市价单
stk_biz_action = ORDER_TYPE_MKT    # 121
```

## 查询功能

### Q18: 如何查询资金、持仓、委托？

**A:** 查询功能将在阶段四实现。目前可以查看 `examples/query_example.py` 了解预期的使用方式。

## 其他问题

### Q19: 如何查看示例代码？

**A:** 查看 `examples/` 目录：
- `trading_example.py` - 完整的交易流程示例
- `order_example.py` - 下单功能示例
- `query_example.py` - 查询功能示例（待实现）

### Q20: 如何运行测试？

**A:** 

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_order.py

# 运行测试并生成覆盖率报告
pytest --cov=stock_ox --cov-report=html
```

### Q21: 如何贡献代码？

**A:** 
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 创建 Pull Request

### Q22: 如何报告问题？

**A:** 在 GitHub 上创建 Issue，包含：
- 问题描述
- 复现步骤
- 错误信息
- 环境信息（Python 版本、操作系统等）

### Q23: 如何获取帮助？

**A:** 
- 查看文档：`docs/` 目录
- 查看示例：`examples/` 目录
- 创建 Issue：GitHub Issues
- 查看测试代码：`tests/` 目录

## 联系和支持

如有其他问题，请：
1. 查看文档和示例代码
2. 查看测试代码了解使用方法
3. 创建 GitHub Issue 报告问题

