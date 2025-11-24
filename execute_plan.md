# 国信证券OX API量化交易系统执行计划

## 项目概述

基于国信证券OX C++ SDK，构建C++中间服务 + Python客户端的量化交易系统架构，实现策略逻辑与交易执行分离。

---

## 系统架构

```
+----------------+       HTTP/gRPC        +------------------+       SDK调用      +----------------+
| Python客户端   | --------------------> | C++中间服务      | ----------------> | 国信OX SDK     |
| (策略 &风控)  | <-------------------- | (REST/gRPC API)  | <---------------- | (下单 &查询)   |
+----------------+                        +------------------+                  +----------------+
```

### 核心优势
- ✅ 解决Python直接调用C++成员函数的技术难题
- ✅ 策略逻辑与交易执行解耦，便于维护和扩展
- ✅ 支持多策略、多账户管理
- ✅ 统一的API接口，便于测试和监控

---

## 阶段一：基础环境搭建与登录验证（第1-2周）

### 1.1 环境准备 ✅
- [x] 确认Windows开发环境
- [x] 确认国信OX SDK文件完整性
- [x] 验证配置文件格式
- [x] 修复Tradelog.prop路径问题

### 1.2 登录功能验证
**目标**：确保能够成功登录国信证券账户

**任务清单**：
- [x] 修复C++ demo编译问题（如需要）
- [x] 验证登录流程：`gxCreateTradeApi()` -> `RegisterSpi()` -> `Init()` -> `OnReqLogon()`
- [x] 实现登录回调处理 `OnRspLogon`（已改进，添加错误检查和详细日志）
- [x] 测试登录成功，获取账户信息（登录成功后自动查询交易账户）
- [x] 记录登录过程中的所有错误和解决方案（见 `登录测试说明.md` 和 `登录错误记录.md`）

**验收标准**：
- ✅ 能够成功登录账户
- ✅ 能够接收登录回调
- ✅ 能够查询交易账户信息

**预计时间**：3-5天

**完成情况**：
- ✅ 已改进登录回调处理，添加错误检查和详细日志
- ✅ 已验证登录流程完整性
- ✅ 已实现登录成功后自动查询交易账户信息
- ✅ 已添加超时机制和错误处理
- ✅ 已创建测试文档和错误记录文档

**测试文档**：
- `登录测试说明.md` - 详细的测试步骤和预期结果
- `登录错误记录.md` - 错误记录和解决方案

---

## 阶段二：C++中间服务核心开发（第3-5周）

### 2.1 技术选型

**HTTP框架选择**：
- **推荐**：`cpp-httplib`（轻量级，易用）
- 备选：`Crow`（功能丰富）、`Pistache`（高性能）

**JSON库**：
- **推荐**：`nlohmann/json`（现代C++，易用）

**项目结构**：
```
cpp_service/
├── src/
│   ├── main.cpp              # 服务入口
│   ├── api_handler.cpp       # HTTP请求处理
│   ├── ox_wrapper.cpp        # 国信OX SDK包装
│   ├── ox_spi.cpp            # 回调处理类
│   └── config.cpp            # 配置管理
├── include/
│   ├── api_handler.h
│   ├── ox_wrapper.h
│   └── config.h
├── CMakeLists.txt
└── config/
    └── service_config.json
```

### 2.2 核心功能实现

#### 2.2.1 账户初始化接口
```cpp
POST /api/v1/init
Request:
{
  "account": "620000259568",
  "password": "111111",
  "acct_type": 0,
  "sh_trade_account": "A354038998",
  "sz_trade_account": "0148211801"
}

Response:
{
  "status": "success",
  "message": "Account initialized successfully",
  "session_id": "xxx"
}
```

#### 2.2.2 下单接口
```cpp
POST /api/v1/order
Request:
{
  "symbol": "600519",
  "board_id": "10",          // 10-上海, 00-深圳
  "side": "buy",             // buy/sell
  "quantity": 100,
  "price": 2500.0,          // 限价单价格，市价单传0
  "order_type": "limit",    // limit/market
  "order_ref": "unique_ref_123"
}

Response:
{
  "status": "success",
  "order_id": "123456",
  "order_ref": "unique_ref_123",
  "message": "Order placed successfully"
}
```

#### 2.2.3 撤单接口
```cpp
POST /api/v1/cancel
Request:
{
  "order_no": 123456,
  "board_id": "10",
  "symbol": "600519"
}

Response:
{
  "status": "success",
  "message": "Order cancelled successfully"
}
```

#### 2.2.4 查询接口

**查询资金**：
```cpp
GET /api/v1/balance

Response:
{
  "status": "success",
  "data": {
    "account_worth": 1000000.0,
    "fund_value": 500000.0,
    "market_value": 500000.0,
    "available": 450000.0
  }
}
```

**查询持仓**：
```cpp
GET /api/v1/positions?symbol=600519

Response:
{
  "status": "success",
  "data": [
    {
      "symbol": "600519",
      "available": 1000,
      "frozen": 0,
      "cost_price": 2500.0
    }
  ]
}
```

**查询委托**：
```cpp
GET /api/v1/orders?status=all

Response:
{
  "status": "success",
  "data": [
    {
      "order_no": 123456,
      "symbol": "600519",
      "side": "buy",
      "quantity": 100,
      "filled_qty": 0,
      "price": 2500.0,
      "order_state": "2",  // 已报
      "order_time": "2024-01-01 10:00:00"
    }
  ]
}
```

**查询成交明细**：
```cpp
GET /api/v1/filled_details?symbol=600519

Response:
{
  "status": "success",
  "data": [
    {
      "order_no": 123456,
      "symbol": "600519",
      "filled_qty": 100,
      "filled_price": 2500.0,
      "filled_time": "2024-01-01 10:01:00"
    }
  ]
}
```

### 2.3 回调处理机制

**实现要点**：
- 使用单例模式管理API实例
- 实现完整的`GuosenOXTradeSpi`回调类
- 使用线程安全的队列存储回调数据
- 提供查询接口获取回调结果

**回调映射**：
- `OnRspLogon` -> 登录状态
- `OnRtnOrder` -> 委托回报
- `OnRtnOrderFilled` -> 成交回报
- `OnRspQueryBalance` -> 资金查询结果
- `OnRspQueryPositions` -> 持仓查询结果
- `OnRspQueryOrders` -> 委托查询结果

### 2.4 错误处理与日志

**错误码定义**：
```cpp
enum class ErrorCode {
    SUCCESS = 0,
    NOT_INITIALIZED = 1001,
    LOGIN_FAILED = 1002,
    INVALID_PARAM = 1003,
    ORDER_FAILED = 1004,
    NETWORK_ERROR = 1005
};
```

**日志系统**：
- 使用spdlog或类似库
- 记录所有API调用和回调
- 支持日志级别控制
- 日志文件按日期轮转

### 2.5 开发任务清单

- [ ] 创建C++项目结构
- [ ] 集成HTTP服务器框架
- [ ] 实现OX SDK包装类
- [ ] 实现回调处理类
- [ ] 实现账户初始化接口
- [ ] 实现下单接口
- [ ] 实现撤单接口
- [ ] 实现查询接口（资金/持仓/委托/成交）
- [ ] 实现错误处理和日志
- [ ] 编写单元测试

**预计时间**：2-3周

---

## 阶段三：Python客户端开发（第6-7周）

### 3.1 项目结构

```
python_client/
├── src/
│   ├── client.py           # HTTP客户端封装
│   ├── strategy.py         # 策略基类
│   ├── risk_control.py     # 风控模块
│   ├── logger.py           # 日志模块
│   └── monitor.py          # 监控模块
├── strategies/
│   ├── simple_strategy.py  # 示例策略
│   └── ...
├── config/
│   └── config.yaml         # 配置文件
├── logs/                    # 日志目录
└── requirements.txt
```

### 3.2 核心模块

#### 3.2.1 HTTP客户端封装
```python
class OXAPIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def init_account(self, account: str, password: str, 
                     acct_type: int = 0) -> dict:
        """初始化账户"""
        pass
    
    def place_order(self, symbol: str, side: str, quantity: int,
                   price: float = 0, order_type: str = "limit") -> dict:
        """下单"""
        pass
    
    def cancel_order(self, order_no: int, board_id: str, 
                    symbol: str) -> dict:
        """撤单"""
        pass
    
    def get_balance(self) -> dict:
        """查询资金"""
        pass
    
    def get_positions(self, symbol: str = None) -> dict:
        """查询持仓"""
        pass
    
    def get_orders(self, status: str = "all") -> dict:
        """查询委托"""
        pass
    
    def get_filled_details(self, symbol: str = None) -> dict:
        """查询成交明细"""
        pass
```

#### 3.2.2 风控模块
```python
class RiskControl:
    def __init__(self, config: dict):
        self.max_daily_loss = config.get('max_daily_loss', 10000)
        self.max_position = config.get('max_position', 1000000)
        self.max_single_order = config.get('max_single_order', 100000)
        self.daily_loss = 0
        self.daily_orders = []
    
    def check_order(self, order: dict) -> tuple[bool, str]:
        """检查订单是否符合风控规则"""
        # 1. 检查单笔订单金额
        # 2. 检查总持仓
        # 3. 检查当日亏损
        # 4. 检查订单频率
        pass
    
    def update_daily_loss(self, amount: float):
        """更新当日亏损"""
        pass
    
    def reset_daily(self):
        """每日重置"""
        pass
```

#### 3.2.3 策略基类
```python
class BaseStrategy:
    def __init__(self, client: OXAPIClient, risk_control: RiskControl):
        self.client = client
        self.risk_control = risk_control
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_signal(self) -> dict:
        """获取交易信号"""
        # 子类实现
        raise NotImplementedError
    
    def execute(self):
        """执行策略"""
        signal = self.get_signal()
        if signal:
            # 风控检查
            if self.risk_control.check_order(signal)[0]:
                # 下单
                result = self.client.place_order(**signal)
                self.logger.info(f"Order placed: {result}")
            else:
                self.logger.warning("Order rejected by risk control")
```

#### 3.2.4 示例策略
```python
class SimpleStrategy(BaseStrategy):
    def get_signal(self):
        # 获取行情（需要接入行情接口）
        # 计算信号
        # 返回订单信息
        return {
            "symbol": "600519",
            "board_id": "10",
            "side": "buy",
            "quantity": 100,
            "price": 2500.0,
            "order_type": "limit"
        }
```

### 3.3 开发任务清单

- [ ] 创建Python项目结构
- [ ] 实现HTTP客户端封装
- [ ] 实现风控模块
- [ ] 实现策略基类
- [ ] 实现示例策略
- [ ] 实现日志模块
- [ ] 实现监控模块（可选）
- [ ] 编写配置文件
- [ ] 编写单元测试

**预计时间**：1-2周

---

## 阶段四：测试与优化（第8周）

### 4.1 测试计划

#### 4.1.1 C++服务测试
- [ ] 使用Postman测试所有API接口
- [ ] 测试登录和账户初始化
- [ ] 测试下单流程（模拟）
- [ ] 测试查询功能
- [ ] 测试错误处理
- [ ] 压力测试（并发请求）

#### 4.1.2 Python客户端测试
- [ ] 单元测试各个模块
- [ ] 集成测试（与C++服务）
- [ ] 策略回测（使用历史数据）
- [ ] 风控规则测试

#### 4.1.3 全流程测试
- [ ] Python策略 -> C++服务 -> SDK下单
- [ ] 回调处理测试
- [ ] 异常情况处理
- [ ] 长时间运行稳定性测试

### 4.2 性能优化

- [ ] 连接池优化
- [ ] 回调处理优化（异步）
- [ ] 日志性能优化
- [ ] 内存泄漏检查

**预计时间**：1周

---

## 阶段五：部署与监控（第9周）

### 5.1 部署方案

#### Windows部署
```bash
# 1. 编译C++服务
mkdir build && cd build
cmake ..
cmake --build . --config Release

# 2. 创建服务目录
mkdir C:\ox_trading_service
copy Release\ox_service.exe C:\ox_trading_service\
copy -r bin\* C:\ox_trading_service\
copy config\service_config.json C:\ox_trading_service\

# 3. 配置Windows服务（可选）
# 使用NSSM或类似工具将exe注册为Windows服务
```

#### Python客户端部署
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置定时任务
# Windows: 使用Task Scheduler
# 创建任务，每分钟运行一次策略脚本
```

### 5.2 监控方案

**日志监控**：
- 文件日志：按日期轮转
- 关键操作日志：单独文件
- 错误日志：实时告警

**性能监控**：
- API响应时间
- 订单成功率
- 系统资源使用

**业务监控**：
- 每日盈亏统计
- 订单统计
- 风控触发记录

### 5.3 部署任务清单

- [ ] 准备生产环境配置
- [ ] 编译发布版本
- [ ] 部署C++服务
- [ ] 部署Python客户端
- [ ] 配置定时任务
- [ ] 配置监控和告警
- [ ] 编写运维文档

**预计时间**：1周

---

## 阶段六：实盘测试与优化（第10-12周）

### 6.1 小资金实盘测试

**测试策略**：
- 使用最小交易单位（100股）
- 选择流动性好的股票
- 设置严格的风控规则
- 每日复盘和优化

**测试内容**：
- [ ] 登录稳定性
- [ ] 下单成功率
- [ ] 查询准确性
- [ ] 回调及时性
- [ ] 异常处理

### 6.2 持续优化

- [ ] 根据实盘反馈优化代码
- [ ] 优化策略逻辑
- [ ] 完善风控规则
- [ ] 性能调优

**预计时间**：2-3周

---

## 技术难点与解决方案

### 难点1：C++成员函数调用
**问题**：Python无法直接调用C++类的成员函数（__thiscall调用约定）

**解决方案**：通过C++中间服务封装，提供HTTP/gRPC接口

### 难点2：回调处理
**问题**：SDK使用回调机制返回数据，需要异步处理

**解决方案**：
- 使用线程安全的队列存储回调数据
- HTTP接口轮询或使用WebSocket推送
- 为每个请求分配唯一ID，通过ID匹配回调

### 难点3：会话管理
**问题**：需要管理API实例的生命周期和登录状态

**解决方案**：
- 使用单例模式管理API实例
- 实现自动重连机制
- 提供健康检查接口

### 难点4：错误处理
**问题**：SDK错误信息需要通过回调获取

**解决方案**：
- 统一错误码定义
- 超时机制
- 详细的错误日志

---

## 开发时间表

| 阶段 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| 阶段一 | 基础环境搭建与登录验证 | 1-2周 | 🔄 进行中 |
| 阶段二 | C++中间服务核心开发 | 2-3周 | ⏳ 待开始 |
| 阶段三 | Python客户端开发 | 1-2周 | ⏳ 待开始 |
| 阶段四 | 测试与优化 | 1周 | ⏳ 待开始 |
| 阶段五 | 部署与监控 | 1周 | ⏳ 待开始 |
| 阶段六 | 实盘测试与优化 | 2-3周 | ⏳ 待开始 |

**总计**：8-12周

---

## 风险与应对

### 风险1：SDK文档不完整
**应对**：参考demo代码，逐步测试和验证

### 风险2：网络不稳定
**应对**：实现重连机制，增加超时和重试

### 风险3：实盘交易风险
**应对**：
- 严格的风控规则
- 小资金测试
- 人工监控

### 风险4：性能瓶颈
**应对**：
- 异步处理
- 连接池
- 缓存机制

---

## 下一步行动

### 立即开始（本周）
1. ✅ 完成项目结构梳理
2. ✅ 修复登录功能（解决Tradelog.prop问题）
3. ⏳ 验证登录流程完整性
4. ⏳ 开始设计C++服务API接口

### 本周目标
- [ ] 成功登录账户
- [ ] 能够查询账户信息
- [ ] 完成C++服务技术选型和项目结构设计

---

## 附录

### A. 参考资源
- 国信OX API文档：`doc/API使用说明.docx`
- C++示例代码：`demo/main.cpp`
- Python测试脚本：`test_login.py`

### B. 关键API映射

| 功能 | SDK方法 | HTTP接口 |
|------|---------|----------|
| 登录 | `OnReqLogon` | `POST /api/v1/init` |
| 下单 | `OnReqOrderTicket` | `POST /api/v1/order` |
| 撤单 | `OnReqCancelTicket` | `POST /api/v1/cancel` |
| 查询资金 | `OnReqQueryBalance` | `GET /api/v1/balance` |
| 查询持仓 | `OnReqQueryPositions` | `GET /api/v1/positions` |
| 查询委托 | `OnReqQueryOrders` | `GET /api/v1/orders` |
| 查询成交 | `OnReqQueryFilledDetails` | `GET /api/v1/filled_details` |

### C. 配置文件示例

**C++服务配置** (`service_config.json`):
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080,
    "threads": 4
  },
  "ox_sdk": {
    "dll_path": "./bin/GuosenOXAPI.dll",
    "config_path": "./bin/config/config.ini"
  },
  "log": {
    "level": "info",
    "file": "./logs/service.log"
  }
}
```

**Python客户端配置** (`config.yaml`):
```yaml
api:
  base_url: "http://127.0.0.1:8080"
  timeout: 30

risk_control:
  max_daily_loss: 10000
  max_position: 1000000
  max_single_order: 100000

strategy:
  name: "simple_strategy"
  params:
    symbol: "600519"
    quantity: 100
```

---

**最后更新**：2024-01-XX
**版本**：v1.0

