# Python 股票交易 API 封装开发计划

## 1. 项目概述

### 1.1 目标
将国信证券 OX 交易 API（C++ DLL）封装为 Python 包，提供简洁易用的 Python 接口，支持：
- 现货交易
- 期权交易  
- 期货交易
- 信用交易（融资融券）
- ETF 交易
- 各种查询功能

### 1.2 技术方案
**采用 ctypes 封装方案**

**理由：**
- ✅ 无需编译，直接调用 DLL
- ✅ 纯 Python 实现，跨平台维护简单（DLL 本身为 Windows）
- ✅ 开发周期短，无需学习 Cython/pybind11
- ✅ 灵活性强，易于调试和维护
- ⚠️ 缺点：需要手动映射 C++ 类型和结构体

**备选方案：**
- pybind11（需要 C++ 编译环境，开发复杂）
- Cython（需要编译步骤，开发周期长）

### 1.3 项目结构

```
stock_ox/
├── python/                          # Python 封装代码
│   ├── stock_ox/                    # 主包目录
│   │   ├── __init__.py              # 包初始化
│   │   ├── api.py                   # 核心 API 封装类
│   │   ├── spi.py                   # 回调接口封装
│   │   ├── structs.py               # 数据结构定义
│   │   ├── constants.py             # 常量定义
│   │   ├── types.py                 # 类型枚举
│   │   ├── dll_loader.py            # DLL 加载器
│   │   ├── utils.py                 # 工具函数
│   │   └── exceptions.py            # 异常定义
│   ├── tests/                       # 测试代码
│   │   ├── __init__.py
│   │   ├── test_api.py              # API 测试
│   │   ├── test_structs.py          # 结构体测试
│   │   └── test_integration.py      # 集成测试
│   ├── examples/                    # 示例代码
│   │   ├── basic_trade.py           # 基础交易示例
│   │   ├── query_demo.py            # 查询示例
│   │   ├── credit_trade.py          # 信用交易示例
│   │   └── callback_demo.py         # 回调示例
│   ├── setup.py                     # 安装脚本
│   ├── requirements.txt             # 依赖列表
│   └── README.md                    # Python 包文档
├── bin/                             # 现有 DLL 文件（保持不变）
├── include/                         # 现有头文件（保持不变）
└── plan.md                          # 本文档
```

## 2. 功能模块设计

### 2.1 核心模块

#### 2.1.1 DLL 加载模块 (`dll_loader.py`)
**职责：**
- 加载 `GuosenOXAPI.dll`
- 定义 C 函数签名
- 映射 DLL 导出函数
- 处理 DLL 加载错误

**关键函数：**
```python
def load_dll(dll_path: str) -> CDLL
def get_create_api_func(dll: CDLL) -> callable
def get_release_api_func(dll: CDLL) -> callable
```

#### 2.1.2 数据结构模块 (`structs.py`)
**职责：**
- 使用 `ctypes.Structure` 定义所有 C++ 结构体
- 处理内存对齐（`_pack_ = 1`）
- 提供结构体的 Python 友好构造函数
- 实现结构体到字典的转换方法

**主要结构体：**
- `COXReqLogonField` - 登录请求
- `COXReqOrderTicketField` - 下单请求
- `COXReqCancelTicketField` - 撤单请求
- `COXRspOrderField` - 委托响应
- `COXRspBalanceField` - 资金响应
- `COXRspPositionField` - 持仓响应
- ... 等所有响应和请求结构体

#### 2.1.3 常量模块 (`constants.py`)
**职责：**
- 定义所有常量（字符串长度、业务代码等）
- 从 C++ 头文件映射常量值

**主要内容：**
- 长度常量：`OX_ACCOUNT_LENGTH = 24`
- 业务代码：`STK_BIZ_BUY = 100`, `STK_BIZ_SELL = 101`
- 委托类型：`ORDER_TYPE_LIMIT = 100`, `ORDER_TYPE_MKT = 121`
- 板块代码：`BOARD_SH = "10"`, `BOARD_SZ = "00"`

#### 2.1.4 类型枚举模块 (`types.py`)
**职责：**
- 定义 Python 枚举类
- 提供类型转换函数

**主要内容：**
- `AccountType` - 账户类型枚举
- `OrderState` - 委托状态枚举
- `ExchangeId` - 交易所枚举

#### 2.1.5 回调接口模块 (`spi.py`)
**职责：**
- 实现回调接口的 Python 包装
- 处理回调函数的 C++ 到 Python 调用
- 支持用户自定义回调处理函数

**设计要点：**
- 使用 `CFUNCTYPE` 定义 C 回调函数类型
- 维护回调函数引用避免被垃圾回收
- 将 C++ 指针参数转换为 Python 对象
- 提供默认空回调实现

#### 2.1.6 核心 API 模块 (`api.py`)
**职责：**
- 封装 `GuosenOXTradeApi` 类
- 提供 Pythonic 的 API 接口
- 管理 API 生命周期
- 错误处理和异常转换

**主要类：**
```python
class OXTradeApi:
    def __init__(self, config_path: str = None)
    def init(self) -> bool
    def stop(self)
    def login(self, account: str, password: str, account_type: AccountType) -> bool
    def order(self, symbol: str, quantity: int, price: float, ...) -> dict
    def cancel(self, order_no: int, board_id: str) -> bool
    def query_balance(self) -> dict
    def query_positions(self, symbol: str = None) -> List[dict]
    # ... 其他方法
```

#### 2.1.7 工具模块 (`utils.py`)
**职责：**
- 字符串编码转换（UTF-8 ↔ GBK）
- 结构体序列化/反序列化
- 价格格式化
- 日志工具
- 配置解析

#### 2.1.8 异常模块 (`exceptions.py`)
**职责：**
- 定义自定义异常类
- API 错误码到异常的映射

**异常类：**
- `OXApiError` - 基础异常
- `OXConnectionError` - 连接错误
- `OXLoginError` - 登录错误
- `OXOrderError` - 下单错误
- `OXQueryError` - 查询错误

### 2.2 高级功能模块（后续扩展）

#### 2.2.1 异步支持模块
- 使用 `asyncio` 封装异步接口
- 支持并发查询
- 事件驱动的回调处理

#### 2.2.2 数据持久化模块
- 订单记录存储
- 交易历史记录
- 使用 SQLite 或 JSON 文件

#### 2.2.3 策略框架模块
- 策略基类
- 回测框架
- 信号生成器

## 3. 开发阶段规划

### 阶段一：基础框架搭建（预计 3-5 天）

#### 任务 1.1：环境准备
- [x] 创建 Python 项目结构
- [x] 配置开发环境（虚拟环境、IDE）
- [x] 编写 `setup.py` 和 `requirements.txt`
- [x] 配置代码风格检查工具（flake8, black）

#### 任务 1.2：DLL 加载器实现
- [x] 实现 `dll_loader.py`
- [x] 测试 DLL 加载功能
- [x] 实现 DLL 函数签名定义
- [x] 测试 `gxCreateTradeApi` 和 `gxReleaseTradeApi` 调用

#### 任务 1.3：基础数据结构定义
- [x] 定义基础类型（错误响应结构体）
- [x] 定义登录请求/响应结构体
- [x] 测试结构体内存布局与 C++ 一致
- [x] 编写结构体单元测试

**验收标准：**
- ✅ 可以成功加载 DLL
- ✅ 可以创建和释放 API 实例
- ✅ 基础结构体可以正确创建和访问

**验收状态：** ✅ **已完成**（2024年）
- 验收测试文件：`python/tests/test_stage1_acceptance.py`
- 验收报告：`python/docs/STAGE1_ACCEPTANCE_REPORT.md`
- 所有验收标准均已通过

### 阶段二：核心功能实现（预计 5-7 天）

#### 任务 2.1：常量、类型和工具函数
- [x] 实现 `constants.py`（所有常量）
- [x] 实现 `types.py`（枚举类型）
- [x] 实现 `utils.py`（基础工具函数）
- [x] 实现 `exceptions.py`（异常定义）

#### 任务 2.2：回调接口实现
- [x] 实现 `spi.py` 回调接口封装
- [x] 实现回调函数类型定义
- [x] 测试回调函数调用
- [x] 实现回调数据转换（C 结构体 → Python dict）

#### 任务 2.3：API 初始化、登录功能
- [x] 实现 `api.py` 基础框架
- [x] 实现 `init()` 方法
- [x] 实现 `stop()` 方法
- [x] 实现 `login()` 方法
- [x] 实现登录回调处理
- [x] 测试登录流程

**验收标准：**
- ✅ 可以成功初始化 API
- ✅ 可以成功登录账户
- ✅ 可以接收登录响应回调

**验收状态：** ✅ **已完成**（2024年）
- 验收测试文件：`python/tests/test_stage2_acceptance.py`
- 验收报告：`python/docs/STAGE2_ACCEPTANCE_REPORT.md`
- 所有验收标准均已通过

### 阶段三：交易功能实现（预计 5-7 天）

#### 任务 3.1：下单功能
- [x] 定义下单相关结构体
- [x] 实现 `order()` 方法
- [x] 实现委托回报回调处理
- [x] 实现成交回报回调处理
- [x] 编写下单示例代码
- [x] 测试下单功能

#### 任务 3.2：撤单功能
- [x] 定义撤单相关结构体
- [x] 实现 `cancel()` 方法
- [x] 实现撤单响应回调处理
- [x] 测试撤单功能

#### 任务 3.3：批量下单功能（可选）
- [x] 定义批量下单结构体
- [x] 实现 `batch_order()` 方法
- [x] 测试批量下单功能

**验收标准：**
- ✅ 可以成功下单（限价单、市价单）
- ✅ 可以接收委托回报和成交回报
- ✅ 可以成功撤单

**验收状态：** ✅ **已完成**（2024年）
- 验收测试文件：`python/tests/test_stage3_acceptance.py`
- 验收报告：`python/docs/STAGE3_ACCEPTANCE_REPORT.md`
- 所有验收标准均已通过

### 阶段四：查询功能实现（预计 5-7 天）

#### 任务 4.1：基础查询功能
- [ ] 定义查询相关结构体
- [ ] 实现 `query_balance()` - 查询资金
- [ ] 实现 `query_positions()` - 查询持仓
- [ ] 实现 `query_orders()` - 查询委托
- [ ] 实现 `query_filled_details()` - 查询成交明细
- [ ] 实现 `query_trade_accounts()` - 查询股东账号
- [ ] 测试所有查询功能

#### 任务 4.2：扩展查询功能
- [ ] 实现 `query_positions_ex()` - 扩展持仓查询
- [ ] 实现 ETF 相关查询
- [ ] 实现期货相关查询

**验收标准：**
- ✅ 所有查询功能正常工作
- ✅ 查询结果正确转换为 Python 字典/列表
- ✅ 支持查询参数过滤

### 阶段五：高级功能实现（预计 7-10 天）

#### 任务 5.1：信用交易功能
- [ ] 定义信用交易相关结构体
- [ ] 实现融资买入、融券卖出
- [ ] 实现担保品买卖
- [ ] 实现信用交易查询功能：
  - `query_credit_target_stocks()` - 标的证券查询
  - `query_credit_collaterals_stocks()` - 担保证券查询
  - `query_credit_balance_debt()` - 资产负债查询
  - `query_credit_contracts()` - 合约查询
  - `query_credit_seculend_quota()` - 融券头寸查询
  - `query_credit_reimbursible_balance()` - 可偿还金额查询
- [ ] 实现 `credit_repay()` - 直接还款
- [ ] 编写信用交易示例代码

#### 任务 5.2：期权功能
- [ ] 定义期权相关结构体
- [ ] 实现期权查询功能：
  - `query_option_balance()` - 期权资金查询
  - `query_option_positions()` - 期权持仓查询
  - `query_option_margin_risk()` - 保证金风险度查询

#### 任务 5.3：ETF 功能
- [ ] 实现 `query_etf_info()` - ETF 信息查询
- [ ] 实现 `query_etf_component_info()` - ETF 成分股查询
- [ ] 支持 ETF 申购赎回下单

**验收标准：**
- ✅ 所有高级功能正常工作
- ✅ 功能覆盖率达到 90% 以上

### 阶段六：测试和文档（预计 5-7 天）

#### 任务 6.1：单元测试
- [ ] 为每个模块编写单元测试
- [ ] 测试覆盖率 > 80%
- [ ] 使用 pytest 框架
- [ ] Mock DLL 调用进行测试

#### 任务 6.2：集成测试
- [x] 编写完整交易流程测试
- [x] 编写查询流程测试（待查询功能实现后完善）
- [x] 编写异常情况测试
- [x] 编写并发调用测试（如果支持）

**完成状态：** ✅ **已完成**（2024年）
- 集成测试文件：`python/tests/test_integration.py`
- 测试报告：`python/docs/INTEGRATION_TEST_REPORT.md`
- 测试结果：20 个测试通过，4 个测试跳过（查询功能尚未实现）
- 代码覆盖率：87%

#### 任务 6.3：示例代码
- [x] 基础交易示例
- [x] 查询功能示例（占位示例，待查询功能实现后完善）

**完成状态：** ✅ **部分完成**（2024年）
- 基础交易示例：`python/examples/trading_example.py`
  - 包含完整的交易流程演示
  - 包含限价单、市价单、批量下单等示例
  - 包含上下文管理器使用示例
  - 包含不同交易板块操作示例
- 查询功能示例：`python/examples/query_example.py`
  - 查询功能使用方式占位示例
  - 待阶段四实现查询功能后完善
- 示例说明文档：`python/examples/README.md`
- [ ] 信用交易示例
- [ ] 回调使用示例
- [ ] 错误处理示例

#### 任务 6.4：文档编写
- [x] API 参考文档（使用 Markdown）
- [x] 快速入门指南
- [x] 完整使用示例
- [x] 常见问题解答
- [x] 更新 `README.md`

**完成状态：** ✅ **已完成**（2024年）
- 快速入门指南：`python/docs/QUICKSTART.md`
- 完整使用示例：`python/docs/USAGE_EXAMPLES.md`
- API 参考文档：`python/docs/API_REFERENCE.md`
- 常见问题解答：`python/docs/FAQ.md`
- 更新 README.md：`python/README.md`

**验收标准：**
- ✅ 测试通过率 100%
- ✅ 文档完整清晰
- ✅ 示例代码可运行

### 阶段七：优化和发布（预计 3-5 天）

#### 任务 7.1：性能优化
- [ ] 优化结构体转换性能
- [ ] 优化回调处理性能
- [ ] 添加连接池（如果需要）
- [ ] 内存泄漏检查

#### 任务 7.2：错误处理完善
- [ ] 完善异常处理
- [ ] 添加详细的错误信息
- [ ] 添加重试机制（可选）

#### 任务 7.3：代码质量
- [ ] 代码审查
- [ ] 代码风格统一
- [ ] 添加类型注解
- [ ] 添加文档字符串

#### 任务 7.4：打包发布
- [x] 配置 PyPI 发布
- [x] 编写安装说明
- [x] 创建发布版本
- [x] 编写更新日志

**完成状态：** ✅ **已完成**（2024年）
- PyPI 配置：已更新 `setup.py`，添加 `MANIFEST.in`
- 安装说明：`python/INSTALL.md`
- 发布说明：`python/RELEASE.md`
- 更新日志：`python/CHANGELOG.md`
- 版本信息：`stock_ox/__init__.py` (v0.1.0)

**验收标准：**
- ✅ 代码质量达标
- ✅ 可以打包发布
- ✅ 可以成功安装使用

## 4. 实现优先级

### P0（必须实现 - 核心功能）
1. ✅ DLL 加载和基础框架
2. ✅ API 初始化和登录
3. ✅ 下单和撤单
4. ✅ 查询资金和持仓
5. ✅ 查询委托和成交
6. ✅ 委托回报和成交回报

### P1（重要功能 - 常用功能）
1. 批量下单
2. 扩展持仓查询
3. 信用交易基础功能（融资买入、融券卖出）
4. ETF 申购赎回
5. 股东账号查询

### P2（增强功能 - 高级功能）
1. 信用交易完整功能（所有查询接口）
2. 期权功能
3. 期货功能
4. 异常处理完善
5. 日志功能

### P3（扩展功能 - 可选功能）
1. 异步接口支持
2. 数据持久化
3. 策略框架
4. 性能监控
5. 可视化工具

## 5. 技术难点和解决方案

### 5.1 结构体内存对齐
**问题：** C++ 结构体使用 `#pragma pack(1)`，ctypes 需要匹配

**解决方案：**
```python
class MyStruct(Structure):
    _pack_ = 1  # 1 字节对齐
    _fields_ = [...]
```

### 5.2 回调函数实现
**问题：** C++ 虚函数回调如何映射到 Python

**解决方案：**
- 创建一个 C++ 兼容的回调包装类
- 使用 `CFUNCTYPE` 定义回调函数类型
- 在 Python 中维护回调函数引用
- 使用函数指针将 Python 回调传递给 DLL

**实现思路：**
```python
# 定义回调函数类型
CallbackFunc = CFUNCTYPE(c_int, POINTER(CStruct))

# Python 回调包装
class CallbackWrapper:
    def __init__(self, user_callback):
        self.user_callback = user_callback
        self.c_callback = CallbackFunc(self._callback)
    
    def _callback(self, c_struct):
        # 转换 C 结构体为 Python 对象
        py_obj = convert_to_python(c_struct)
        # 调用用户回调
        return self.user_callback(py_obj)
```

### 5.3 字符串编码问题
**问题：** C++ DLL 可能使用 GBK 编码，Python 使用 UTF-8

**解决方案：**
```python
def encode_str(s: str) -> bytes:
    return s.encode('gbk')

def decode_str(b: bytes) -> str:
    return b.decode('gbk').rstrip('\x00')
```

### 5.4 异步回调处理
**问题：** C++ 回调是同步的，如何在 Python 中异步处理

**解决方案：**
- 使用队列存储回调数据
- 在单独线程中处理回调
- 使用 `threading.Event` 或 `queue.Queue` 进行同步
- 可选：使用 `asyncio` 的 `call_soon_threadsafe`

### 5.5 API 实例生命周期管理
**问题：** 确保 API 实例正确释放，避免内存泄漏

**解决方案：**
- 使用上下文管理器（`__enter__` / `__exit__`）
- 在析构函数中确保调用 `Stop()` 和 `Release`
- 使用 `weakref` 跟踪实例（如果需要）

```python
class OXTradeApi:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.release()
```

## 6. 开发规范和最佳实践

### 6.1 代码风格
- 遵循 PEP 8 规范
- 使用类型注解（Python 3.7+）
- 函数和类添加文档字符串
- 使用有意义的变量名

### 6.2 错误处理
- 所有 API 调用都要检查返回值
- 使用自定义异常而不是返回错误码
- 记录详细的错误日志
- 提供清晰的错误消息

### 6.3 测试策略
- 单元测试：测试每个函数/方法
- 集成测试：测试完整流程
- Mock 测试：模拟 DLL 调用
- 实际环境测试：使用真实账户（谨慎）

### 6.4 文档要求
- 每个公共函数都有文档字符串
- 包含参数说明、返回值说明、异常说明
- 提供使用示例
- 维护更新日志

## 7. 风险评估和应对

### 7.1 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| DLL 接口变更 | 高 | 低 | 保持头文件同步，建立版本兼容机制 |
| 回调函数死锁 | 中 | 中 | 使用超时机制，避免在回调中阻塞 |
| 内存泄漏 | 高 | 中 | 仔细管理对象生命周期，使用内存检测工具 |
| 编码问题 | 中 | 中 | 统一使用 UTF-8，在接口层转换 |

### 7.2 开发风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 开发周期延长 | 中 | 中 | 按阶段迭代，优先实现核心功能 |
| 测试不充分 | 高 | 中 | 建立完整的测试体系，自动化测试 |
| 文档不完善 | 低 | 中 | 边开发边写文档，代码审查时检查 |

## 8. 时间估算

### 总开发时间：约 35-50 天

- **阶段一**：基础框架（3-5 天）
- **阶段二**：核心功能（5-7 天）
- **阶段三**：交易功能（5-7 天）
- **阶段四**：查询功能（5-7 天）
- **阶段五**：高级功能（7-10 天）
- **阶段六**：测试文档（5-7 天）
- **阶段七**：优化发布（3-5 天）

### MVP 版本（最小可用版本）：约 15-20 天
包含：登录、下单、撤单、查询资金、查询持仓、委托回报

### 完整版本：约 35-50 天
包含所有功能模块

## 9. 后续优化方向

### 9.1 性能优化
- 缓存查询结果
- 批量查询优化
- 异步接口支持

### 9.2 功能扩展
- 策略回测框架
- 实时行情集成
- 风险控制模块
- 自动化交易系统

### 9.3 易用性提升
- CLI 命令行工具
- Web 管理界面
- 配置文件管理
- 日志分析工具

## 10. 参考资料

### 10.1 技术文档
- ctypes 官方文档：https://docs.python.org/3/library/ctypes.html
- Python C 扩展：https://docs.python.org/3/extending/
- 国信证券 API 文档：`doc/API使用说明.docx`

### 10.2 类似项目参考
- vnpy（期货交易框架）
- easytrader（股票交易框架）
- tushare（股票数据接口）

---

## 附录：快速开始清单

开发开始前需要确认：

- [ ] Python 3.7+ 环境已安装
- [ ] DLL 文件路径确认（Windows 环境）
- [ ] 测试账户准备（用于测试）
- [ ] 开发工具配置（IDE、git 等）
- [ ] 代码仓库创建
- [ ] 项目结构创建

开发流程：

1. 按照阶段顺序开发
2. 每个任务完成后提交代码
3. 编写测试用例
4. 更新文档
5. 代码审查
6. 合并到主分支

---

**最后更新：** 2024-12-XX  
**版本：** 1.0  
**维护者：** 开发团队

