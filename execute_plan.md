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
├── src/                      # 源代码目录
│   ├── main.cpp              # 服务入口
│   ├── api_handler.cpp       # HTTP请求处理
│   ├── ox_wrapper.cpp        # 国信OX SDK包装
│   ├── ox_spi.cpp            # 回调处理类
│   └── config.cpp            # 配置管理
├── include/                   # 头文件目录
│   ├── api_handler.h
│   ├── ox_wrapper.h
│   └── config.h
├── third_party/               # 第三方依赖库
│   ├── httplib.h             # cpp-httplib HTTP库
│   ├── json.hpp              # nlohmann/json JSON库
│   └── README.md             # 依赖库说明文档
├── config/                    # 配置文件目录
│   └── service_config.json    # 服务配置文件
├── tests/                     # 测试代码目录
├── logs/                      # 日志文件目录
├── build/                     # 构建输出目录（由CMake生成）
├── CMakeLists.txt            # CMake构建配置文件
└── .gitignore                # Git忽略文件配置
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

### 2.5 详细开发任务规划

#### 2.5.1 环境准备与项目搭建（第1-2天）

**任务清单**：
- [x] **T2.1.1** 安装和配置开发环境
  - 确认C++17编译器（Visual Studio 2019+ 或 GCC 7+）
  - 安装CMake（3.12+）
  - 配置Git版本控制
  
- [x] **T2.1.2** 集成第三方依赖库
  - 下载并集成 `cpp-httplib`（单头文件，直接包含）
  - 下载并集成 `nlohmann/json`（单头文件，直接包含）
  - 或使用vcpkg/Conan管理依赖
  - 验证依赖库编译和链接成功
  
- [x] **T2.1.3** 创建项目目录结构
  - 创建 `cpp_service/` 目录
  - 创建 `src/`, `include/`, `config/`, `tests/`, `logs/` 目录
  - 创建 `CMakeLists.txt` 文件
  - 创建 `.gitignore` 文件
  
- [x] **T2.1.4** 配置CMake构建系统
  - 编写基础 `CMakeLists.txt`
  - 配置C++17标准
  - 配置包含目录和库目录
  - 链接国信OX SDK库（GuosenOXAPI.lib）
  - 配置编译选项（Debug/Release）
  - 测试编译空项目成功

**验收标准**：
- ✅ 项目可以成功编译（即使只有main函数）
- ✅ 所有依赖库可以正确包含和使用
- ✅ CMake配置正确，可以生成Visual Studio项目文件

**预计时间**：1-2天

**验收结果**：✅ **已通过**

**验收详情**：
1. ✅ **项目编译测试**：
   - `ox_service` 主程序编译成功（Release模式）
   - 程序运行正常，输出正确
   - 编译输出：`build/bin/Release/ox_service.exe`

2. ✅ **依赖库验证**：
   - `cpp-httplib` 库：包含和使用正常，可以创建Server实例
   - `nlohmann/json` 库：包含和使用正常，JSON序列化功能正常
   - 测试程序 `test_dependencies.exe` 运行成功，所有依赖库功能正常

3. ✅ **CMake配置验证**：
   - CMake配置成功，生成Visual Studio项目文件
   - 生成了4个 `.vcxproj` 项目文件
   - 生成了 `ox_trading_service.slnx` 解决方案文件
   - 可以在Visual Studio中正常打开和编译

**验收日期**：2024-11-24

---

#### 2.5.2 基础框架开发（第3-5天）

**任务清单**：
- [x] **T2.2.1** 实现配置管理模块（`config.cpp/h`）
  - 定义配置结构体（服务器配置、SDK配置、日志配置）
  - 实现JSON配置文件读取
  - 实现配置验证和默认值设置
  - 实现配置热加载（可选）
  - 编写配置模块单元测试
  
- [x] **T2.2.2** 实现日志系统
  - 集成spdlog或实现简单日志类
  - 实现日志级别控制（DEBUG/INFO/WARN/ERROR）
  - 实现文件日志和控制台日志
  - 实现日志文件按日期轮转
  - 实现日志格式化（时间戳、级别、文件、行号）
  
- [x] **T2.2.3** 实现错误处理模块
  - 定义错误码枚举（ErrorCode）
  - 实现错误信息结构体
  - 实现错误码到错误信息的映射
  - 实现统一的错误响应格式
  - 编写错误处理单元测试
  
- [x] **T2.2.4** 实现HTTP服务器基础框架
  - 初始化cpp-httplib服务器
  - 实现基础路由注册机制
  - 实现请求/响应JSON解析和序列化
  - 实现CORS支持（如需要）
  - 实现请求日志记录中间件
  - 测试HTTP服务器可以启动和响应

**验收标准**：
- ✅ 配置文件可以正确读取和解析
- ✅ 日志系统可以正常记录日志
- ✅ HTTP服务器可以启动并响应基础请求（如 `/health`）
- ✅ 错误处理机制可以正常工作

**预计时间**：2-3天

**验收结果**：✅ **已通过**

**验收详情**：
1. ✅ **配置文件可以正确读取和解析**：
   - 测试配置文件创建和读取成功
   - 配置验证功能正常
   - 配置项（服务器、SDK、日志）均能正确解析
   - 默认值设置正常工作

2. ✅ **日志系统可以正常记录日志**：
   - 日志系统初始化成功
   - 支持DEBUG、INFO、WARN、ERROR四个级别
   - 控制台和文件日志输出正常
   - 日志格式化包含时间戳、级别、文件位置信息
   - 日志文件按日期轮转功能正常

3. ✅ **HTTP服务器可以启动并响应基础请求**：
   - HTTP服务器初始化成功
   - 服务器可以正常启动和停止
   - 健康检查端点 `/health` 响应正常，返回状态码200
   - 自定义路由可以正常注册和响应
   - 支持GET、POST、PUT、DELETE方法
   - CORS支持正常工作

4. ✅ **错误处理机制可以正常工作**：
   - 错误码枚举定义完整
   - 错误信息映射正确
   - 错误响应JSON格式正确
   - 成功响应JSON格式正确
   - 错误处理和成功响应可以正确序列化为JSON字符串

5. ✅ **综合集成测试**：
   - 所有模块协同工作正常
   - 配置、日志、HTTP服务器、错误处理模块集成成功
   - 实际HTTP请求测试通过
   - 错误响应和成功响应在HTTP接口中正常工作

**验收测试输出**：
```
Acceptance Test 1: Config file reading and parsing...
  [PASS] Config file can be read and parsed correctly

Acceptance Test 2: Logging system...
  [PASS] Logging system can record logs normally

Acceptance Test 3: HTTP server startup and response...
  Health check response: {"service": "ox_trading_service", "status": "ok"}
  [PASS] HTTP server can start and respond to basic requests

Acceptance Test 4: Error handling mechanism...
  [PASS] Error handling mechanism works correctly

Acceptance Test 5: Integration test...
  [PASS] Integration test passed

[PASS] All acceptance criteria are met!
```

**验收日期**：2024-11-24

---

#### 2.5.3 OX SDK包装层开发（第6-8天）

**任务清单**：
- [ ] **T2.3.1** 实现OXWrapper单例类（`ox_wrapper.h/cpp`）
  - 实现单例模式
  - 封装API实例创建和销毁
  - 封装API初始化流程
  - 实现线程安全保护
  - 实现API状态管理（未初始化/已初始化/已登录/已断开）
  
- [ ] **T2.3.2** 实现OXSpi回调处理类（`ox_spi.h/cpp`）
  - 继承 `GuosenOXTradeSpi`
  - 实现所有必需的回调函数
  - 实现回调数据存储机制（使用线程安全队列）
  - 实现回调数据查询接口
  - 实现回调超时处理
  
- [ ] **T2.3.3** 实现回调数据管理
  - 定义回调数据结构（登录回调、订单回调、查询回调等）
  - 实现线程安全的回调队列
  - 实现回调数据按请求ID匹配
  - 实现回调数据过期清理机制
  - 实现回调数据查询接口（按请求ID、按类型等）
  
- [ ] **T2.3.4** 实现登录功能封装
  - 封装登录请求（`Login`方法）
  - 实现登录状态查询
  - 实现登录超时处理
  - 实现自动重连机制（可选）
  - 编写登录功能单元测试

**验收标准**：
- ✅ 可以成功创建和初始化API实例
- ✅ 可以成功注册回调接口
- ✅ 可以成功发送登录请求
- ✅ 可以正确接收和处理登录回调
- ✅ 回调数据可以正确存储和查询

**预计时间**：2-3天

---

#### 2.5.4 HTTP API接口实现（第9-15天）

**任务清单**：

**账户初始化接口**：
- [ ] **T2.4.1** 实现 `/api/v1/init` 接口
  - 实现请求参数解析（account, password, acct_type等）
  - 实现参数验证（非空、格式检查）
  - 调用OXWrapper登录方法
  - 等待登录回调（带超时）
  - 返回登录结果（成功/失败）
  - 生成并返回session_id（如需要）
  - 实现错误处理和错误响应
  - 编写接口单元测试

**下单接口**：
- [ ] **T2.4.2** 实现 `/api/v1/order` 接口
  - 实现请求参数解析（symbol, board_id, side, quantity, price等）
  - 实现参数验证（价格范围、数量限制等）
  - 实现订单类型转换（buy/sell -> StkBiz, limit/market -> StkBizAction）
  - 生成唯一订单引用号（OrderRef）
  - 调用OXWrapper下单方法
  - 等待订单回调（带超时）
  - 返回订单结果（订单号、状态等）
  - 实现错误处理和错误响应
  - 编写接口单元测试

**撤单接口**：
- [ ] **T2.4.3** 实现 `/api/v1/cancel` 接口
  - 实现请求参数解析（order_no, board_id, symbol）
  - 实现参数验证
  - 调用OXWrapper撤单方法
  - 等待撤单回调（带超时）
  - 返回撤单结果
  - 实现错误处理和错误响应
  - 编写接口单元测试

**查询资金接口**：
- [ ] **T2.4.4** 实现 `/api/v1/balance` 接口
  - 实现请求参数解析（如需要）
  - 调用OXWrapper查询资金方法
  - 等待查询回调（带超时）
  - 转换回调数据为JSON格式
  - 返回资金信息
  - 实现错误处理和错误响应
  - 编写接口单元测试

**查询持仓接口**：
- [ ] **T2.4.5** 实现 `/api/v1/positions` 接口
  - 实现请求参数解析（symbol可选）
  - 调用OXWrapper查询持仓方法
  - 等待查询回调（支持多条数据）
  - 转换回调数据为JSON数组格式
  - 实现数据过滤（按symbol）
  - 返回持仓信息
  - 实现错误处理和错误响应
  - 编写接口单元测试

**查询委托接口**：
- [ ] **T2.4.6** 实现 `/api/v1/orders` 接口
  - 实现请求参数解析（status可选）
  - 调用OXWrapper查询委托方法
  - 等待查询回调（支持多条数据）
  - 转换回调数据为JSON数组格式
  - 实现数据过滤（按状态）
  - 返回委托信息
  - 实现错误处理和错误响应
  - 编写接口单元测试

**查询成交明细接口**：
- [ ] **T2.4.7** 实现 `/api/v1/filled_details` 接口
  - 实现请求参数解析（symbol可选）
  - 调用OXWrapper查询成交明细方法
  - 等待查询回调（支持多条数据）
  - 转换回调数据为JSON数组格式
  - 实现数据过滤（按symbol）
  - 返回成交明细信息
  - 实现错误处理和错误响应
  - 编写接口单元测试

**健康检查接口**：
- [ ] **T2.4.8** 实现 `/api/v1/health` 接口
  - 检查API实例状态
  - 检查登录状态
  - 返回服务健康状态
  - 实现错误处理和错误响应

**验收标准**：
- ✅ 所有接口可以正确解析请求参数
- ✅ 所有接口可以正确调用SDK方法
- ✅ 所有接口可以正确返回响应
- ✅ 所有接口的错误处理正常工作
- ✅ 所有接口可以通过Postman/curl测试

**预计时间**：5-7天

---

#### 2.5.5 回调处理机制完善（第16-17天）

**任务清单**：
- [ ] **T2.5.1** 完善所有回调函数实现
  - 实现 `OnRspLogon` - 登录回调
  - 实现 `OnRtnOrder` - 委托回报
  - 实现 `OnRtnOrderFilled` - 成交回报
  - 实现 `OnRspQueryBalance` - 资金查询回调
  - 实现 `OnRspQueryPositions` - 持仓查询回调
  - 实现 `OnRspQueryOrders` - 委托查询回调
  - 实现 `OnRspQueryFilledDetails` - 成交明细查询回调
  - 实现 `OnRspCancelTicket` - 撤单回调
  - 实现 `OnConnected` / `OnDisconnected` - 连接状态回调
  
- [ ] **T2.5.2** 实现回调数据序列化
  - 实现回调数据到JSON的转换
  - 处理特殊数据类型（时间、金额等）
  - 处理可选字段和空值
  
- [ ] **T2.5.3** 实现回调超时和重试机制
  - 实现回调超时检测
  - 实现超时后的错误返回
  - 实现重试机制（可选）
  
- [ ] **T2.5.4** 实现回调数据持久化（可选）
  - 将重要回调数据保存到文件或数据库
  - 实现数据恢复机制

**验收标准**：
- ✅ 所有回调函数可以正确接收和处理数据
- ✅ 回调数据可以正确存储到队列
- ✅ 回调数据可以正确查询和返回
- ✅ 回调超时机制正常工作

**预计时间**：1-2天

---

#### 2.5.6 错误处理与日志完善（第18天）

**任务清单**：
- [ ] **T2.6.1** 完善错误处理
  - 统一所有接口的错误响应格式
  - 实现详细的错误信息记录
  - 实现错误码映射表
  - 实现错误日志记录
  
- [ ] **T2.6.2** 完善日志系统
  - 记录所有API调用（请求和响应）
  - 记录所有回调接收
  - 记录所有错误信息
  - 实现日志级别动态调整
  - 实现敏感信息脱敏（密码等）
  
- [ ] **T2.6.3** 实现性能监控（可选）
  - 记录接口响应时间
  - 记录回调等待时间
  - 实现性能统计接口

**验收标准**：
- ✅ 所有错误都有明确的错误码和错误信息
- ✅ 所有重要操作都有日志记录
- ✅ 日志文件可以正常轮转
- ✅ 敏感信息不会泄露到日志

**预计时间**：1天

---

#### 2.5.7 测试与文档（第19-21天）

**任务清单**：
- [ ] **T2.7.1** 编写单元测试
  - 为每个模块编写单元测试
  - 测试正常流程
  - 测试异常流程
  - 测试边界条件
  - 实现测试覆盖率统计（目标>80%）
  
- [ ] **T2.7.2** 编写集成测试
  - 测试完整API调用流程
  - 测试多个接口的组合调用
  - 测试并发请求处理
  - 测试错误恢复机制
  
- [ ] **T2.7.3** 编写API文档
  - 使用OpenAPI/Swagger格式编写API文档
  - 或编写Markdown格式的API文档
  - 包含所有接口的请求/响应示例
  - 包含错误码说明
  - 包含使用示例
  
- [ ] **T2.7.4** 编写部署文档
  - 编写编译说明
  - 编写配置说明
  - 编写运行说明
  - 编写故障排查指南
  
- [ ] **T2.7.5** 性能测试和优化
  - 测试接口响应时间
  - 测试并发处理能力
  - 识别性能瓶颈
  - 进行性能优化（如需要）

**验收标准**：
- ✅ 单元测试覆盖率>80%
- ✅ 所有接口可以通过集成测试
- ✅ API文档完整且准确
- ✅ 部署文档清晰易懂
- ✅ 性能满足要求（接口响应时间<100ms）

**预计时间**：2-3天

---

### 2.6 开发任务总览

**任务统计**：
- 总任务数：约35个详细任务
- 预计总时间：15-21天（3-4周）
- 关键路径：环境准备 → 基础框架 → SDK包装 → API接口 → 测试

**里程碑**：
- **M1（第5天）**：基础框架完成，HTTP服务器可以启动
- **M2（第8天）**：SDK包装层完成，可以成功登录
- **M3（第15天）**：所有API接口实现完成
- **M4（第21天）**：测试完成，可以交付

**风险点**：
- SDK回调机制理解不深入，可能导致回调处理错误
- 线程安全问题，需要仔细设计
- 性能问题，需要优化回调处理机制
- 错误处理不完善，需要充分测试

**依赖关系**：
- T2.1（环境准备） → T2.2（基础框架） → T2.3（SDK包装） → T2.4（API接口）
- T2.3（SDK包装） → T2.5（回调处理）
- T2.2（基础框架） → T2.6（错误处理与日志）
- T2.4（API接口） → T2.7（测试与文档）

**预计时间**：3-4周（15-21个工作日）

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

