# 示例代码说明

本目录包含 stock_ox API 的使用示例。

## 示例文件列表

### 1. `trading_example.py` - 基础交易示例

演示完整的交易流程，包括：
- API 初始化和停止
- 账户登录
- 下单（限价单、市价单）
- 接收委托回报和成交回报
- 撤单
- 批量下单
- 使用上下文管理器
- 不同交易板块操作

**使用方法：**
```bash
cd python
python examples/trading_example.py
```

### 2. `order_example.py` - 下单功能示例

演示基本的下单操作（已存在的示例）。

**使用方法：**
```bash
cd python
python examples/order_example.py
```

### 3. `query_example.py` - 查询功能示例

演示查询功能的使用方式（占位示例，待阶段四实现后完善）。

**注意：** 查询功能将在阶段四实现，本示例展示了查询功能的预期使用方式。

**使用方法：**
```bash
cd python
python examples/query_example.py
```

### 4. `real_trading.py` - 真实股票交易脚本 ⚠️

**⚠️ 重要警告：这是一个真实的交易系统！所有操作都会产生真实的交易。请确保您完全了解交易风险，谨慎操作。**

用于进行真实的股票下单操作，支持：
- 从配置文件读取账户信息或手动输入
- 交互式下单和撤单
- 实时查看委托回报和成交回报
- 订单管理

**使用方法：**
```bash
cd python
python examples/real_trading.py
```

**详细使用指南：**
请参阅 [REAL_TRADING_GUIDE.md](REAL_TRADING_GUIDE.md) 获取详细的使用说明和注意事项。

**配置说明：**
1. 编辑 `bin/config/config.ini` 文件，配置账户信息
2. 或者运行脚本时手动输入账户信息

**主要功能：**
- 登录账户
- 下单（限价单、市价单）
- 撤单
- 查看订单状态
- 接收实时回报

## 运行环境要求

### Windows 环境

示例代码需要在 Windows 环境下运行，因为：
1. DLL 文件（`GuosenOXAPI.dll`）是 Windows 专用的
2. 需要实际的交易服务器连接

### 非 Windows 环境（macOS/Linux）

在非 Windows 环境下，示例代码会提示 DLL 加载失败。这是正常现象，因为：
1. DLL 文件无法在非 Windows 系统上加载
2. 示例代码主要用于展示 API 的使用方式

如果需要测试 API 功能，可以使用单元测试和集成测试（使用 Mock）。

## 配置说明

在运行示例代码之前，请确保：

1. **DLL 文件存在**
   - 路径：`../bin/GuosenOXAPI.dll`
   - 确保 DLL 文件在正确的位置

2. **配置文件**
   - 路径：`../bin/config/config.ini`
   - 包含账户信息和密码

3. **账户信息**
   - 示例代码中使用的账户信息为测试数据
   - 实际使用时请修改为您的账户信息

## 示例代码结构

### TradingSpi 类

自定义的回调接口类，用于处理各种回调：
- `on_rsp_logon()` - 登录响应回调
- `on_rtn_order()` - 委托回报回调
- `on_rtn_order_filled()` - 成交回报回调
- `on_rsp_cancel_ticket()` - 撤单响应回调
- `on_rsp_batch_order()` - 批量下单响应回调

### 使用上下文管理器

推荐使用上下文管理器（`with` 语句）来管理 API 生命周期：

```python
with OXTradeApi() as api:
    api.register_spi(spi)
    api.login(account, password, account_type)
    # ... 进行交易操作 ...
# API 自动停止
```

### 错误处理

示例代码包含完整的错误处理：

```python
try:
    # API 操作
except OXConnectionError as e:
    print(f"连接错误: {e}")
except OXLoginError as e:
    print(f"登录错误: {e}")
except OXOrderError as e:
    print(f"交易错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
finally:
    api.stop()  # 确保 API 被停止
```

## 注意事项

1. **账户信息**
   - 示例代码中的账户信息为测试数据
   - 实际使用时请修改为您的账户信息
   - 不要在公开代码中硬编码密码

2. **回调处理**
   - 回调函数是异步的
   - 需要在回调中正确处理数据
   - 避免在回调中进行耗时操作

3. **线程安全**
   - API 操作是线程安全的
   - 但回调处理需要注意线程安全

4. **错误处理**
   - 始终使用 try-except 处理错误
   - 确保在 finally 中停止 API

## 更多示例

更多示例代码将在后续版本中添加：
- 信用交易示例（阶段五）
- 期权交易示例（阶段五）
- ETF 交易示例（阶段五）
- 回调使用示例（任务 6.3）
- 错误处理示例（任务 6.3）

## 相关文档

- API 参考文档：待添加（任务 6.4）
- 快速入门指南：待添加（任务 6.4）
- 常见问题解答：待添加（任务 6.4）

