# 更新日志

本文档记录了 stock_ox 的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2024-11-23

### 新增功能

#### 核心 API
- ✅ 实现 `OXTradeApi` 核心类
  - 支持 API 初始化和停止
  - 支持账户登录
  - 支持下单（限价单、市价单）
  - 支持撤单
  - 支持批量下单
  - 支持上下文管理器（`with` 语句）

#### 回调接口
- ✅ 实现 `OXTradeSpi` 回调接口基类
  - 支持登录响应回调
  - 支持委托回报回调
  - 支持成交回报回调
  - 支持撤单响应回调
  - 支持批量下单响应回调

#### 数据结构
- ✅ 实现核心数据结构（使用 ctypes）
  - `COXReqLogonField` - 登录请求结构体
  - `COXRspLogonField` - 登录响应结构体
  - `COXReqOrderTicketField` - 下单请求结构体
  - `COXOrderTicket` - 委托回报结构体
  - `COXOrderFilledField` - 成交回报结构体
  - `COXReqCancelTicketField` - 撤单请求结构体
  - `COXRspCancelTicketField` - 撤单响应结构体
  - `COXOrderItem` - 订单项结构体
  - `COXReqBatchOrderTicketField` - 批量下单请求结构体

#### 工具函数
- ✅ 实现字符串编码/解码工具
  - 支持 GBK、UTF-8 编码转换
  - 支持编码失败回退机制
- ✅ 实现价格和数量格式化工具
- ✅ 实现安全的类型转换工具
- ✅ 实现结构体转字典工具

#### 类型和常量
- ✅ 实现账户类型枚举（`AccountType`）
- ✅ 实现委托状态枚举（`OrderState`）
- ✅ 实现交易所 ID 枚举（`ExchangeId`）
- ✅ 实现业务常量定义
  - 交易板块常量（上海、深圳）
  - 证券业务常量（买入、卖出）
  - 委托类型常量（限价单、市价单）

#### 异常处理
- ✅ 实现自定义异常类
  - `OXApiError` - 所有异常基类
  - `OXDllError` - DLL 相关错误
  - `OXConnectionError` - 连接相关错误
  - `OXLoginError` - 登录相关错误
  - `OXOrderError` - 交易相关错误
  - `OXQueryError` - 查询相关错误

#### DLL 加载器
- ✅ 实现 DLL 加载和函数获取
- ✅ 支持自动查找 DLL 路径
- ✅ 支持 API 实例创建和释放

### 测试

#### 单元测试
- ✅ 为所有核心模块编写单元测试
  - `test_api.py` - API 测试（100% 覆盖率）
  - `test_spi.py` - SPI 测试（79% 覆盖率）
  - `test_structs.py` - 数据结构测试（90% 覆盖率）
  - `test_order.py` - 下单功能测试（14 个测试）
  - `test_cancel.py` - 撤单功能测试（31 个测试）
  - `test_batch_order.py` - 批量下单测试（15 个测试）
  - `test_dll_loader.py` - DLL 加载器测试
  - `test_task_2_1.py` - 常量、类型、工具函数测试

#### 集成测试
- ✅ 实现完整交易流程测试
- ✅ 实现异常情况测试
- ✅ 实现并发调用测试
- ✅ 实现边界情况测试
- ✅ 实现错误恢复测试
  - 总测试数：24 个（20 个通过，4 个跳过）
  - 代码覆盖率：87%

#### 验收测试
- ✅ 阶段一验收测试（DLL 加载、API 创建、基础结构体）
- ✅ 阶段二验收测试（API 初始化、登录、回调接收）
- ✅ 阶段三验收测试（下单、撤单、回报接收）

### 文档

#### 用户文档
- ✅ 快速入门指南（`docs/QUICKSTART.md`）
- ✅ 完整使用示例（`docs/USAGE_EXAMPLES.md`）
- ✅ API 参考文档（`docs/API_REFERENCE.md`）
- ✅ 常见问题解答（`docs/FAQ.md`）
- ✅ 项目 README（`README.md`）

#### 示例代码
- ✅ 基础交易示例（`examples/trading_example.py`）
- ✅ 下单功能示例（`examples/order_example.py`）
- ✅ 查询功能示例（`examples/query_example.py`，占位）
- ✅ 示例说明文档（`examples/README.md`）

#### 开发文档
- ✅ 项目开发计划（`../plan.md`）
- ✅ 代码覆盖率报告（`docs/`）
- ✅ 验收测试报告（`docs/`）

### 配置和构建

#### 项目配置
- ✅ 配置 `setup.py` 用于 PyPI 发布
- ✅ 配置 `pyproject.toml` 用于代码质量工具
- ✅ 配置 `requirements.txt` 和 `requirements-dev.txt`
- ✅ 配置 `MANIFEST.in` 用于包含额外文件
- ✅ 配置 `.gitignore` 排除不需要的文件

#### 代码质量工具
- ✅ 配置 `black` 代码格式化
- ✅ 配置 `flake8` 代码检查
- ✅ 配置 `mypy` 类型检查
- ✅ 配置 `pylint` 代码分析
- ✅ 配置 `pytest` 测试框架

### 已知问题

- ⚠️ DLL 文件只能在 Windows 环境下加载
- ⚠️ 查询功能尚未实现（待阶段四）
- ⚠️ 信用交易、期权、ETF 功能尚未实现（待阶段五）

### 待实现功能

#### 阶段四（查询功能）
- ⏳ 查询资金
- ⏳ 查询持仓
- ⏳ 查询委托
- ⏳ 查询成交明细
- ⏳ 查询股东账号

#### 阶段五（高级功能）
- ⏳ 信用交易（融资融券）
- ⏳ 期权交易
- ⏳ ETF 交易

### 贡献者

感谢所有贡献者！

---

## 版本说明

### 版本号规则

- **主版本号（MAJOR）**：不兼容的 API 修改
- **次版本号（MINOR）**：向后兼容的功能性新增
- **修订号（PATCH）**：向后兼容的问题修正

### 发布计划

- **v0.1.0** (当前版本) - 初始发布
  - 核心交易功能（下单、撤单、批量下单）
  - 基础回调机制
  - 完整的测试和文档

- **v0.2.0** (计划中) - 查询功能
  - 所有查询功能实现
  - 查询回调接口

- **v0.3.0** (计划中) - 高级功能
  - 信用交易
  - 期权交易
  - ETF 交易

