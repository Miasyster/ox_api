# 国信证券 OX 交易 API 项目解析

## 项目概述

本项目是**国信证券（Guosen Securities）OX 交易 API** 的 C++ SDK，提供了完整的证券交易接口封装。支持多种账户类型和交易业务，包括现货交易、期权交易、期货交易、信用交易（融资融券）等。

## 项目结构

```
stock_ox/
├── bin/                        # 运行时文件和配置
│   ├── config/                 # 配置文件目录
│   │   └── config.ini          # 用户账户配置
│   ├── LOG/                    # 日志目录
│   ├── UA/                     # UA 相关配置
│   ├── GuosenOXAPI.dll         # 核心动态库
│   ├── uaAPI.dll               # UA API 动态库
│   ├── uaAuth.dll              # UA 认证动态库
│   ├── uaCrypto.dll            # UA 加密动态库
│   ├── uaPacker.dll            # UA 打包动态库
│   ├── gxtrade.ini             # 交易系统配置
│   └── ...
├── demo/                       # 示例代码
│   ├── config/                 # 示例配置文件
│   ├── main.cpp                # 主程序示例
│   ├── demo.sln                # Visual Studio 解决方案
│   ├── demo.vcxproj            # Visual Studio 项目文件
│   └── ...
├── doc/                        # 文档目录
│   └── API使用说明.docx        # API 使用文档
├── include/                    # 头文件目录
│   ├── OXTradeApi.h            # 主 API 头文件
│   ├── OXTradeApiConst.h       # 常量定义
│   ├── OXTradeApiStruct.h      # 数据结构定义
│   └── OXTradeApiType.h        # 类型定义
└── lib/                        # 静态库文件
    └── GuosenOXAPI.lib         # 核心静态库
```

## 核心组件

### 1. API 接口类

#### `GuosenOXTradeApi` - 主交易 API 类

提供以下核心功能：

**初始化和连接管理：**
- `Init()` - 初始化 API
- `Stop()` - 停止 API
- `RegisterSpi()` - 注册回调接口

**登录和账户管理：**
- `OnReqLogon()` - 用户登录
- `OnReqTradeAccounts()` - 查询股东账号

**委托和撤单：**
- `OnReqOrderTicket()` - 下单
- `OnReqCancelTicket()` - 撤单
- `OnReqBatchOrderTicket()` - 批量下单

**查询功能：**
- `OnReqQueryOrders()` - 查询委托
- `OnReqQueryBalance()` - 查询资金
- `OnReqQueryPositions()` - 查询持仓
- `OnReqQueryPositionsEx()` - 查询持仓（扩展）
- `OnReqQueryFilledDetails()` - 查询成交明细

**信用交易相关：**
- `OnReqCreditRepay()` - 信用交易直接还款
- `OnReqCreditTargetStocks()` - 查询标的证券
- `OnReqCreditCollateralsStocks()` - 查询担保证券
- `OnReqCreditBalanceDebt()` - 查询资产负债
- `OnReqCreditContracts()` - 查询合约
- `OnReqCreditSecuLendQuota()` - 查询融券头寸
- `OnReqCreditReimbursibleBalance()` - 查询可偿还金额
- `OnReqCreditSLContractSummary()` - 查询融券合约汇总

**期权相关：**
- `OnReqStockOptionBalance()` - 查询期权资金
- `OnReqStockOptionPositions()` - 查询期权合约
- `OnReqQueryOptionMarginRisk()` - 查询期权保证金风险度

**ETF 相关：**
- `OnReqQueryETFInfo()` - 查询 ETF 信息
- `OnReqQueryETFComponentInfo()` - 查询 ETF 成分股信息

**期货相关：**
- `OnReqQueryFutureBalance()` - 查询期货资金
- `OnReqQueryFuturePosition()` - 查询期货持仓

#### `GuosenOXTradeSpi` - 回调接口类

所有交易响应和推送通过回调函数返回：

**连接事件：**
- `OnConnected()` - 连接建立
- `OnDisconnected()` - 连接断开

**登录和账户：**
- `OnRspLogon()` - 登录响应
- `OnRspTradeAccounts()` - 股东账号响应

**委托和成交：**
- `OnRtnOrder()` - 委托回报
- `OnRtnOrderFilled()` - 成交回报
- `OnRspCancelTicket()` - 撤单响应
- `OnRspBatchOrder()` - 批量下单响应
- `OnRtnCancelRejected()` - 撤单拒绝

**查询响应：**
- `OnRspQueryOrders()` - 委托查询响应
- `OnRspQueryBalance()` - 资金查询响应
- `OnRspQueryPositions()` - 持仓查询响应
- `OnRspQueryPositionsEx()` - 持仓查询响应（扩展）
- `OnRspQueryFilledDetails()` - 成交明细查询响应

### 2. 账户类型

```cpp
enum OXAccountType
{
    OX_ACCOUNT_STOCK   = '0',    // 现货
    OX_ACCOUNT_OPTION  = '1',    // 期权
    OX_ACCOUNT_FUTURE  = '2',    // 期货
    OX_ACCOUNT_CREDIT  = '3'     // 信用交易
};
```

### 3. 委托状态

```cpp
enum OXOrderState
{
    ORDER_STATE_NOT_REPORT          = '0',    // 未报
    ORDER_STATE_REPORTING           = '1',    // 正报
    ORDER_STATE_REPORTED            = '2',    // 已报
    ORDER_STATE_CANCELING           = '3',    // 已报撤单
    ORDER_STATE_PARTIAL_CANCELING   = '4',    // 部成待撤
    ORDER_STATE_PARTIAL_CANCELED    = '5',    // 部成部分撤
    ORDER_STATE_CANCELED            = '6',    // 已撤
    ORDER_STATE_PARTIAL_FILLED      = '7',    // 部成成交
    ORDER_STATE_FILLED              = '8',    // 已成交
    ORDER_STATE_REJECTED            = '9',    // 废单
    ORDER_STATE_REPORT_WAITING      = 'A',    // 报盘等待
    ORDER_STATE_REPORT_ACK          = 'B',    // 报盘确认
    ORDER_STATE_NEED_SEND           = 'N',    // 需报送
    ORDER_STATE_DIVIDEND_CANCELED   = 'D',    // 红利息止
    ORDER_STATE_EXPIRED             = 'E',    // 过期终止
    ORDER_STATE_TRIGGER_AGAIN       = 'T'     // 再次触发
};
```

## 配置文件说明

### bin/config/config.ini

用户账户配置文件，包含以下字段：

```ini
[user]
acct=110060035050              # 资金账号
acct_type=3                    # 账户类型：0-现货 1-期权 2-期货 3-信用交易
password=111111                # 密码
sh_trade_account=A197407210    # 上海交易账号
sz_trade_account=0000035074    # 深圳交易账号
```

### bin/gxtrade.ini

系统配置文件：

```ini
[system]
trade_node=2                   # 交易节点
debug=false                    # 调试模式

[future]
appid=guosen_ts_1.0.0         # 应用标识
```

## 主要数据结构

### 登录请求

```cpp
struct COXReqLogonField
{
    OXAccountType  AcctType;                    // 账户类型
    char Account[OX_ACCOUNT_LENGTH];            // 资金账号
    char Password[OX_PASSWORD_LENGTH];          // 密码
    char Reserved[OX_RESERVED_LENGTH];          // 保留字段
};
```

### 下单请求

```cpp
struct COXReqOrderTicketField
{
    OXAccountType  AcctType;                    // 账户类型
    char Account[OX_ACCOUNT_LENGTH];            // 资金账号
    char Trdacct[OX_TRDACCT_LENGTH];           // 股东账号
    char BoardId[OX_BOARDID_LENGTH];           // 交易板块
    int  StkBiz;                                // 证券业务
    int  StkBizAction;                          // 证券业务指令
    char Symbol[OX_SYMBOL_LENGTH];             // 证券代码
    uint32_t OrderQty;                          // 委托数量
    char OrderPrice[OX_ORDERPRICE_LENGTH];     // 委托价格
    char OrderRef[OX_ORDER_REF_LENGTH];        // 委托引用
    char TrdCodeCls;                            // 交易代码类别
    char TrdExInfo[OX_TRD_EXT_INFO_LENGTH];    // 交易扩展信息
};
```

### 委托回报

```cpp
struct COXOrderTicket
{
    // 包含委托的完整信息：证券代码、委托价格、委托数量、
    // 成交数量、撤单数量、委托状态、委托编号等
};
```

## 业务类型代码

### 证券业务（StkBiz）

- `100` - 买入
- `101` - 卖出
- `181` - ETF 申购
- `182` - ETF 赎回
- `700` - 担保品买入
- `701` - 担保品卖出
- `702` - 融资买入
- `703` - 融券卖出

### 委托类型（StkBizAction）

- `100` - 限价单
- `121` - 最优成交剩余撤销（市价单的一种）

## 示例代码流程

### 基本使用流程

1. **创建 API 实例**
```cpp
GuosenOXTradeApi *g_TradeApi = gxCreateTradeApi();
```

2. **注册回调接口**
```cpp
StkSpi stkSpi;  // 继承自 GuosenOXTradeSpi
g_TradeApi->RegisterSpi(&stkSpi);
```

3. **初始化 API**
```cpp
const char *pError = nullptr;
int iInitRet = g_TradeApi->Init(&pError);
```

4. **用户登录**
```cpp
COXReqLogonField req;
req.AcctType = OX_ACCOUNT_STOCK;
snprintf(req.Account, sizeof(req.Account), "%s", account.c_str());
snprintf(req.Password, sizeof(req.Password), "%s", password.c_str());
g_TradeApi->OnReqLogon(0, &req);
```

5. **下单**
```cpp
COXReqOrderTicketField req;
req.AcctType = OX_ACCOUNT_STOCK;
snprintf(req.Account, sizeof(req.Account), "%s", account.c_str());
snprintf(req.BoardId, sizeof(req.BoardId), "10");  // 10-上海，00-深圳
snprintf(req.Trdacct, sizeof(req.Trdacct), "%s", trdAccount.c_str());
snprintf(req.Symbol, sizeof(req.Symbol), "600000");
req.StkBiz = 100;  // 买入
req.StkBizAction = 100;  // 限价单
req.OrderQty = 100;
snprintf(req.OrderPrice, sizeof(req.OrderPrice), "9.90");
g_TradeApi->OnReqOrderTicket(0, &req);
```

6. **停止和释放**
```cpp
g_TradeApi->Stop();
gxReleaseTradeApi(g_TradeApi);
```

## Demo 程序说明

`demo/main.cpp` 提供了一个完整的交互式交易客户端示例，支持以下命令：

### 委托命令
- `BUY SH.600000 100 9.9` - 限价买入
- `SELL SZ.000001 100 MKT` - 市价卖出
- `BUYETF SH.510051 900000 1` - ETF 申购
- `BUYCREDIT SH.601088 100 18.41` - 融资买入
- `SELLCREDIT SH.601088 100 18.41` - 融券卖出
- `BUYGUARD SH.600000 100 9.9` - 担保品买入
- `SELLGUARD SH.600000 100 9.9` - 担保品卖出

### 撤单命令
- `CANCEL SH Q123456` - 撤单

### 查询命令
- `QUERY ACCOUNT` - 查询股东账号
- `QUERY POSITION` - 查询持仓
- `QUERY ORDER` - 查询委托
- `QUERY BALANCE` - 查询资金
- `QUERY DETAIL` - 查询成交明细

### 信用交易查询
- `CREDIT QUERY` - 查询资产负债
- `CREDIT REPAY` - 直接还款
- `CREDIT STOCK LIST` - 查询标的证券
- `CREDIT COLLATERALS STOCKS` - 查询担保证券
- `CREDIT SECULEND QUOTA` - 查询融券头寸
- `CREDIT CONTRACTS` - 查询合约
- `CREDIT REIMBURSIBLE BALANCE` - 查询可偿还金额
- `CREDIT CONTRACTSUMMARY` - 查询融券合约汇总

### 期权查询
- `OPTION FUND` - 查询期权资金
- `OPTION POSITION` - 查询期权持仓

### ETF 查询
- `ETF INFO` - 查询 ETF 信息
- `ETF COMPONENT INFO` - 查询 ETF 成分股信息

## 编译说明

### 环境要求

- **操作系统**: Windows
- **编译器**: Visual Studio 2015 或更高版本
- **平台**: Win32 或 x64

### 编译步骤

1. 使用 Visual Studio 打开 `demo/demo.sln`
2. 配置项目属性：
   - **包含目录**: `../include`
   - **库目录**: `../lib`
   - **附加依赖项**: `GuosenOXAPI.lib`
3. 编译项目（Debug 或 Release 配置）
4. 将编译生成的 `demo.exe` 和必要的 DLL 文件放置到 `bin/` 目录

### 运行要求

运行时需要以下文件在同一目录：

- `demo.exe` (或编译后的可执行文件)
- `GuosenOXAPI.dll`
- `uaAPI.dll`
- `uaAuth.dll`
- `uaCrypto.dll`
- `uaPacker.dll`
- `config.ini` (配置文件)
- `gxtrade.ini` (系统配置)

## 注意事项

1. **账户配置**: 使用前请确保 `config.ini` 中的账户信息正确
2. **权限要求**: 需要具备相应账户的交易权限
3. **交易时间**: 仅在交易时间内可以进行交易操作
4. **错误处理**: 所有 API 调用都应检查返回值和错误信息
5. **线程安全**: API 本身可能不是线程安全的，多线程使用时需要自行加锁
6. **连接管理**: 建议在程序退出前调用 `Stop()` 和 `gxReleaseTradeApi()` 释放资源

## 技术支持

详细的 API 使用说明请参考 `doc/API使用说明.docx` 文档。

## 版本信息

- 项目名称: 国信证券 OX 交易 API
- 主要库文件: GuosenOXAPI.dll / GuosenOXAPI.lib
- 支持账户类型: 现货、期权、期货、信用交易

---

**注意**: 本项目仅用于学习和研究目的，实际交易请遵守相关法律法规和券商规定。

