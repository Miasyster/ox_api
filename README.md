# 国信证券 OX 交易 API SDK

国信证券 OX 交易 API 的 C++ SDK，提供完整的证券交易功能接口。

## 项目结构

```
ox/
├── ox1/                          # SDK 主目录
│   ├── bin/                      # 运行时文件
│   │   ├── config/               # 配置文件目录
│   │   │   └── config.ini        # 配置文件示例
│   │   ├── GuosenOXAPI.dll       # API 动态链接库
│   │   ├── gxtrade.ini           # 交易配置
│   │   ├── LOG/                  # 日志目录
│   │   ├── Tradelog.prop         # 交易日志配置
│   │   ├── UA/                   # UA 相关配置
│   │   │   ├── UAConfig.prop
│   │   │   └── UALogConfig.prop
│   │   └── *.dll                 # 其他依赖 DLL 文件
│   ├── demo/                     # 示例代码
│   │   ├── config/               # 示例配置文件
│   │   │   └── config.ini
│   │   ├── main.cpp              # 主程序示例
│   │   ├── demo.sln              # Visual Studio 解决方案文件
│   │   ├── demo.vcxproj          # Visual Studio 项目文件
│   │   ├── start.bat             # 启动脚本
│   │   ├── getopt.hpp            # 命令行参数解析
│   │   └── inireader.h           # INI 文件读取工具
│   ├── doc/                      # 文档目录
│   │   └── API使用说明.docx      # API 使用说明文档
│   ├── include/                  # 头文件目录
│   │   ├── OXTradeApi.h          # API 主头文件
│   │   ├── OXTradeApiConst.h     # 常量定义
│   │   ├── OXTradeApiStruct.h    # 数据结构定义
│   │   └── OXTradeApiType.h      # 类型定义
│   └── lib/                      # 库文件目录
│       └── GuosenOXAPI.lib       # 静态链接库
```

## 功能特性

### 支持的账户类型

- **现货账户** (`OX_ACCOUNT_STOCK = '0'`) - 普通股票交易
- **期权账户** (`OX_ACCOUNT_OPTION = '1'`) - 期权交易
- **期货账户** (`OX_ACCOUNT_FUTURE = '2'`) - 期货交易
- **信用账户** (`OX_ACCOUNT_CREDIT = '3'`) - 融资融券交易

### 核心功能

#### 1. 连接管理
- 连接建立 (`OnConnected`)
- 连接断开 (`OnDisconnected`)
- 登录认证 (`OnReqLogon`)

#### 2. 账户管理
- 查询交易账户 (`OnReqTradeAccounts`)
- 查询资金余额 (`OnReqQueryBalance`)
- 查询持仓 (`OnReqQueryPositions`)
- 查询持仓（扩展接口）(`OnReqQueryPositionsEx`)

#### 3. 交易功能
- 下单 (`OnReqOrderTicket`)
- 批量下单 (`OnReqBatchOrderTicket`)
- 撤单 (`OnReqCancelTicket`)
- 查询委托 (`OnReqQueryOrders`)
- 查询成交明细 (`OnReqQueryFilledDetails`)

#### 4. 信用交易功能
- 融资买入 (`StkBiz = 702`)
- 融券卖出 (`StkBiz = 703`)
- 担保品买入 (`StkBiz = 700`)
- 担保品卖出 (`StkBiz = 701`)
- 直接还款 (`OnReqCreditRepay`)
- 查询融资融券标的 (`OnReqCreditTargetStocks`)
- 查询担保品标的 (`OnReqCreditCollateralsStocks`)
- 查询资产负债 (`OnReqCreditBalanceDebt`)
- 查询融资融券合约 (`OnReqCreditContracts`)
- 查询融券头寸 (`OnReqCreditSecuLendQuota`)
- 查询可偿还余额 (`OnReqCreditReimbursibleBalance`)
- 查询融券合约汇总信息 (`OnReqCreditSLContractSummary`)

#### 5. 期权功能
- 查询期权资金 (`OnReqStockOptionBalance`)
- 查询期权持仓 (`OnReqStockOptionPositions`)
- 查询期权保证金风险 (`OnReqQueryOptionMarginRisk`)

#### 6. ETF 功能
- ETF 申购 (`StkBiz = 181`)
- ETF 赎回 (`StkBiz = 182`)
- 查询 ETF 信息 (`OnReqQueryETFInfo`)
- 查询 ETF 成分股信息 (`OnReqQueryETFComponentInfo`)

#### 7. 期货功能
- 查询期货资金 (`OnReqQueryFutureBalance`)
- 查询期货持仓 (`OnReqQueryFuturePosition`)

## 快速开始

### 环境要求

- Windows 操作系统
- Visual Studio 2015 或更高版本
- C++ 编译器支持 C++11 标准

### 编译步骤

1. 使用 Visual Studio 打开 `ox1/demo/demo.sln`
2. 配置项目属性：
   - 包含目录：添加 `ox1/include`
   - 库目录：添加 `ox1/lib`
   - 附加依赖项：添加 `GuosenOXAPI.lib`
3. 编译项目生成 `demo.exe`

### 配置说明

编辑 `ox1/demo/config/config.ini` 文件：

```ini
[user]
# 资金账号
acct=110060035050

# 账户类型: 0-现货, 1-期权, 2-期货, 3-信用交易
acct_type=3

# 密码
password=111111

# 上海交易账户
sh_trade_account=A197407210

# 深圳交易账户
sz_trade_account=0000035074
```

### 运行示例

1. 将 `ox1/bin` 目录下的所有 DLL 文件复制到 `demo.exe` 所在目录
2. 运行 `start.bat` 或直接执行：
   ```bash
   demo.exe --file=config/config.ini
   ```

## API 使用示例

### 基本使用流程

```cpp
#include "OXTradeApi.h"

// 1. 创建 API 实例
GuosenOXTradeApi *pApi = gxCreateTradeApi();

// 2. 创建回调处理类（继承 GuosenOXTradeSpi）
class MySpi : public GuosenOXTradeSpi {
    // 实现回调函数
    virtual void OnRspLogon(...) override { }
    // ... 其他回调函数
};

// 3. 注册回调
MySpi spi;
pApi->RegisterSpi(&spi);

// 4. 初始化
const char *pError = nullptr;
pApi->Init(&pError);

// 5. 登录
COXReqLogonField req;
snprintf(req.Account, sizeof(req.Account), "your_account");
req.AcctType = OX_ACCOUNT_STOCK;
snprintf(req.Password, sizeof(req.Password), "your_password");
pApi->OnReqLogon(0, &req);

// 6. 使用 API 进行交易操作
// ...

// 7. 停止并释放
pApi->Stop();
gxReleaseTradeApi(pApi);
```

### 下单示例

```cpp
COXReqOrderTicketField req;
req.AcctType = OX_ACCOUNT_STOCK;
snprintf(req.Account, sizeof(req.Account), "your_account");
snprintf(req.BoardId, sizeof(req.BoardId), "10");  // 10-上海, 00-深圳
snprintf(req.Trdacct, sizeof(req.Trdacct), "your_trade_account");
snprintf(req.Symbol, sizeof(req.Symbol), "600000");
req.OrderQty = 100;
req.StkBiz = 100;  // 100-买入, 101-卖出
req.StkBizAction = 100;  // 100-限价, 121-市价
snprintf(req.OrderPrice, sizeof(req.OrderPrice), "9.90");
snprintf(req.OrderRef, sizeof(req.OrderRef), "1111111111111111");

pApi->OnReqOrderTicket(0, &req);
```

### 查询资金示例

```cpp
COXReqBalanceField req;
memset(&req, 0, sizeof(COXReqBalanceField));
req.AcctType = OX_ACCOUNT_STOCK;
snprintf(req.Account, sizeof(req.Account), "your_account");
pApi->OnReqQueryBalance(0, &req);
```

## 委托状态说明

- `'0'` - 未报
- `'1'` - 待报
- `'2'` - 已报
- `'3'` - 已报待撤
- `'4'` - 部分待撤
- `'5'` - 部分已撤
- `'6'` - 已撤
- `'7'` - 部分成交
- `'8'` - 已成交
- `'9'` - 废单
- `'A'` - 待报（写入报盘队列未成功）
- `'B'` - 报盘确认（已成功写入接口库，报盘还未写确认）

## 示例程序命令

运行示例程序后，可以使用以下命令：

### 交易命令
- `BUY SH.600000 100 9.9` - 买入上海股票
- `SELL SZ.000001 100 MKT` - 市价卖出深圳股票
- `CANCEL SH Q123456` - 撤单

### 查询命令
- `QUERY ACCOUNT` - 查询交易账户
- `QUERY POSITION` - 查询持仓
- `QUERY ORDER` - 查询委托
- `QUERY DETAIL` - 查询成交明细
- `QUERY BALANCE` - 查询资金

### ETF 命令
- `BUYETF SZ.159901 1000000 1` - ETF 申购
- `SELLETF SH.510051 900000 1` - ETF 赎回

### 信用交易命令
- `BUYCREDIT SH.601088 100 18.41` - 融资买入
- `SELLCREDIT SH.601088 100 18.41` - 融券卖出
- `BUYGUARD SH.600000 100 9.9` - 担保品买入
- `SELLGUARD SH.600000 100 9.9` - 担保品卖出
- `CREDIT QUERY` - 查询融资融券资产负债
- `CREDIT REPAY` - 直接还款
- `CREDIT STOCK LIST` - 查询融资融券标的
- `CREDIT COLLATERALS STOCKS` - 查询担保品标的
- `CREDIT SECULEND QUOTA` - 查询融券头寸
- `CREDIT BALANCE DEBT` - 查询资产负债
- `CREDIT CONTRACTS` - 查询融资融券合约
- `CREDIT REIMBURSIBLE BALANCE` - 查询可偿还余额
- `CREDIT CONTRACTSUMMARY` - 查询融券合约汇总信息

### 期权命令
- `OPTION FUND` - 查询期权资金信息
- `OPTION POSITION` - 查询期权持仓信息

### ETF 信息查询
- `ETF INFO` - 查询 ETF 信息
- `ETF COMPONENT INFO` - 查询 ETF 成分股信息

## 注意事项

1. **DLL 依赖**：运行程序前确保所有必需的 DLL 文件在可执行文件目录或系统 PATH 中
2. **配置文件**：确保配置文件路径正确，账户信息准确
3. **网络连接**：需要稳定的网络连接到国信证券交易服务器
4. **账户权限**：确保账户具有相应的交易权限（如信用交易、期权交易等）
5. **交易时间**：仅在交易时间内进行交易操作
6. **错误处理**：所有回调函数都应检查 `pError` 参数，处理错误情况

## 文档

详细 API 文档请参考 `ox1/doc/API使用说明.docx`

## 技术支持

如有问题，请参考：
- API 使用说明文档
- 示例代码 `ox1/demo/main.cpp`
- 国信证券官方技术支持

## 许可证

请参考国信证券相关许可协议。

