# C++ 股票下单使用指南

## 快速开始

### 1. 修改配置

在 `order_stock.cpp` 的 `main()` 函数中修改以下配置信息：

```cpp
std::string account = "110060035050";              // 资金账号
std::string password = "111111";                   // 密码
std::string shTrdAccount = "A197407210";           // 上海股东账号
std::string szTrdAccount = "0000035074";           // 深圳股东账号
OXAccountType acctType = OX_ACCOUNT_STOCK;         // 账户类型：现货
```

### 2. 编译程序

#### Windows (Visual Studio)

1. 创建新的控制台项目
2. 将 `order_stock.cpp` 添加到项目
3. 配置项目属性：
   - **包含目录**: `../include`
   - **库目录**: `../lib`
   - **附加依赖项**: `GuosenOXAPI.lib`
4. 编译项目

#### 或者使用命令行编译（示例）

```bash
# 编译
cl /EHsc order_stock.cpp /I../include /link /LIBPATH:../lib GuosenOXAPI.lib /OUT:order_stock.exe

# 运行前需要将 DLL 文件放在同一目录
```

### 3. 运行程序

确保以下文件在同一目录：

- `order_stock.exe` (编译后的可执行文件)
- `GuosenOXAPI.dll`
- `uaAPI.dll`
- `uaAuth.dll`
- `uaCrypto.dll`
- `uaPacker.dll`
- `gxtrade.ini` (系统配置文件)

## 函数说明

### PlaceOrder - 下单函数

```cpp
bool PlaceOrder(
    const std::string &account,      // 资金账号
    const std::string &trdAccount,   // 股东账号（上海或深圳）
    const std::string &boardId,      // 交易板块 ("10" 上海, "00" 深圳)
    const std::string &symbol,       // 证券代码（如 "600000"）
    uint32_t orderQty,               // 委托数量（股，必须是100的整数倍）
    const std::string &orderPrice,   // 委托价格（限价单）或 "MKT"（市价单）
    bool isBuy,                      // true-买入, false-卖出
    OXAccountType acctType,          // 账户类型（默认 OX_ACCOUNT_STOCK）
    const std::string &orderRef      // 委托引用（可选）
)
```

#### 使用示例

```cpp
// 限价买入上海股票 600000，100股，价格 9.90
PlaceOrder(
    account,           // 资金账号
    shTrdAccount,      // 上海股东账号
    "10",              // 上海交易板块
    "600000",          // 证券代码
    100,               // 委托数量
    "9.90",            // 限价价格
    true,              // 买入
    acctType           // 账户类型
);

// 市价卖出深圳股票 000001，100股
PlaceOrder(
    account,
    szTrdAccount,
    "00",              // 深圳交易板块
    "000001",
    100,
    "MKT",             // 市价单
    false,             // 卖出
    acctType
);
```

### CancelOrder - 撤单函数

```cpp
bool CancelOrder(
    const std::string &account,      // 资金账号
    const std::string &boardId,      // 交易板块 ("10" 上海, "00" 深圳)
    int64_t orderNo,                 // 委托编号（从委托回报中获取）
    OXAccountType acctType           // 账户类型（默认 OX_ACCOUNT_STOCK）
)
```

#### 使用示例

```cpp
// 撤单，委托编号从委托回报中获取
CancelOrder(account, "10", 1234567890, acctType);
```

## 交易板块代码

- **"10"** - 上海证券交易所
- **"00"** - 深圳证券交易所

## 委托类型

- **限价单**: 指定具体价格（如 "9.90"）
- **市价单**: 使用 "MKT" 或 "mkt"

## 业务类型代码

- **100** - 买入
- **101** - 卖出
- **181** - ETF 申购
- **182** - ETF 赎回
- **700** - 担保品买入（信用交易）
- **701** - 担保品卖出（信用交易）
- **702** - 融资买入
- **703** - 融券卖出

## 注意事项

1. **账户类型**: 默认使用 `OX_ACCOUNT_STOCK`（现货账户），如需使用其他账户类型：
   - `OX_ACCOUNT_OPTION` - 期权账户
   - `OX_ACCOUNT_FUTURE` - 期货账户
   - `OX_ACCOUNT_CREDIT` - 信用交易账户

2. **委托数量**: 必须是100股的整数倍（1手=100股）

3. **证券代码**: 
   - 上海股票：6位数字（如 "600000"）
   - 深圳股票：6位数字（如 "000001"）

4. **股东账号**: 需要根据交易所选择对应的股东账号
   - 上海股票使用上海股东账号
   - 深圳股票使用深圳股东账号

5. **委托回报**: 下单后会通过回调函数 `OnRtnOrder()` 返回委托状态

6. **成交回报**: 如果委托成交，会通过回调函数 `OnRtnOrderFilled()` 返回成交信息

7. **委托编号**: 从委托回报中获取的 `OrderNo` 字段用于撤单

8. **交易时间**: 仅在交易时间内可以下单

9. **错误处理**: 请检查所有函数的返回值，失败时返回 `false`

## 程序流程

1. **初始化 API** - 创建 API 实例并注册回调
2. **用户登录** - 使用账号密码登录
3. **下单** - 调用 `PlaceOrder()` 函数下单
4. **接收回报** - 通过回调函数接收委托回报和成交回报
5. **撤单**（可选）- 如果需要，调用 `CancelOrder()` 撤单
6. **清理资源** - 程序退出前调用 `Cleanup()` 释放资源

## 回调函数说明

程序会自动处理以下回调：

- `OnRtnOrder()` - 委托回报，包含委托状态、委托编号等信息
- `OnRtnOrderFilled()` - 成交回报，包含成交价格、成交数量等信息
- `OnRspCancelTicket()` - 撤单响应

所有回调信息会自动输出到控制台。

