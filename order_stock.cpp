/**
 * 股票下单示例程序
 * 使用国信证券 OX 交易 API 进行股票下单
 */

#include "OXTradeApi.h"
#include "OXTradeApiConst.h"
#include "OXTradeApiStruct.h"
#include "OXTradeApiType.h"

#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <cstring>

// 全局变量
GuosenOXTradeApi *g_TradeApi = nullptr;
bool g_loggedOn = false;

// 回调接口类
class OrderSpi : public GuosenOXTradeSpi
{
public:
    // 连接事件
    virtual int OnConnected() override
    {
        std::cout << "[回调] 连接成功" << std::endl;
        return 0;
    }

    virtual int OnDisconnected() override
    {
        std::cout << "[回调] 连接断开" << std::endl;
        return 0;
    }

    // 登录响应
    virtual void OnRspLogon(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspLogonField *pField) override
    {
        if (pError && pError->ErrorId != 0)
        {
            std::cout << "[登录失败] ErrorId: " << pError->ErrorId 
                      << ", ErrorInfo: " << pError->ErrorInfo << std::endl;
        }
        else
        {
            std::cout << "[登录成功]" << std::endl;
            g_loggedOn = true;
        }
    }

    // 委托回报
    virtual void OnRtnOrder(const COXOrderTicket *pRtnOrderTicket) override
    {
        std::cout << "\n========== 委托回报 ==========" << std::endl;
        std::cout << "证券代码: " << pRtnOrderTicket->Symbol << std::endl;
        std::cout << "委托价格: " << pRtnOrderTicket->OrderPrice << std::endl;
        std::cout << "委托数量: " << pRtnOrderTicket->OrderQty << std::endl;
        std::cout << "成交数量: " << pRtnOrderTicket->FilledQty << std::endl;
        std::cout << "撤单数量: " << pRtnOrderTicket->CanceledQty << std::endl;
        std::cout << "委托状态: " << (char)pRtnOrderTicket->OrderState << std::endl;
        std::cout << "委托编号: " << pRtnOrderTicket->OrderNo << std::endl;
        std::cout << "委托引用: " << pRtnOrderTicket->OrderRef << std::endl;
        if (strlen(pRtnOrderTicket->ExeInfo) > 0)
        {
            std::cout << "执行信息: " << pRtnOrderTicket->ExeInfo << std::endl;
        }
        std::cout << "============================\n" << std::endl;
    }

    // 成交回报
    virtual void OnRtnOrderFilled(const COXOrderFilledField *pFilledInfo) override
    {
        std::cout << "\n========== 成交回报 ==========" << std::endl;
        std::cout << "证券代码: " << pFilledInfo->Symbol << std::endl;
        std::cout << "成交价格: " << pFilledInfo->FilledPrice << std::endl;
        std::cout << "成交数量: " << pFilledInfo->FilledQty << std::endl;
        std::cout << "成交金额: " << pFilledInfo->FilledAmt << std::endl;
        std::cout << "委托编号: " << pFilledInfo->OrderNo << std::endl;
        std::cout << "成交日期: " << pFilledInfo->FilledDate << std::endl;
        std::cout << "成交时间: " << pFilledInfo->FilledTime << std::endl;
        std::cout << "============================\n" << std::endl;
    }

    // 撤单响应
    virtual void OnRspCancelTicket(int nRequest, const CRspErrorField *pError, const COXRspCancelTicketField *pField) override
    {
        if (pError && pError->ErrorId != 0)
        {
            std::cout << "[撤单失败] ErrorId: " << pError->ErrorId 
                      << ", ErrorInfo: " << pError->ErrorInfo << std::endl;
        }
        else if (pField)
        {
            std::cout << "[撤单成功] 证券代码: " << pField->Symbol 
                      << ", 委托编号: " << pField->OrderNo << std::endl;
        }
    }
};

/**
 * 初始化 API
 */
bool InitAPI()
{
    // 创建 API 实例
    g_TradeApi = gxCreateTradeApi();
    if (g_TradeApi == nullptr)
    {
        std::cerr << "创建 API 实例失败" << std::endl;
        return false;
    }
    std::cout << "API 实例创建成功" << std::endl;

    // 注册回调接口
    static OrderSpi spi;
    g_TradeApi->RegisterSpi(&spi);
    std::cout << "回调接口注册成功" << std::endl;

    // 初始化 API
    const char *errMsg = nullptr;
    int ret = g_TradeApi->Init(&errMsg);
    if (ret != 0)
    {
        std::cerr << "API 初始化失败: " << (errMsg ? errMsg : "未知错误") << std::endl;
        return false;
    }
    std::cout << "API 初始化成功" << std::endl;

    return true;
}

/**
 * 用户登录
 */
bool Login(const std::string &account, const std::string &password, OXAccountType acctType)
{
    COXReqLogonField req;
    memset(&req, 0, sizeof(req));
    
    req.AcctType = acctType;
    snprintf(req.Account, sizeof(req.Account), "%s", account.c_str());
    snprintf(req.Password, sizeof(req.Password), "%s", password.c_str());

    std::cout << "正在登录，账号: " << account << std::endl;
    int ret = g_TradeApi->OnReqLogon(0, &req);
    if (ret != 0)
    {
        std::cerr << "登录请求失败，返回值: " << ret << std::endl;
        return false;
    }

    // 等待登录响应
    int waitCount = 0;
    while (!g_loggedOn && waitCount < 50)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        waitCount++;
    }

    if (!g_loggedOn)
    {
        std::cerr << "登录超时" << std::endl;
        return false;
    }

    return true;
}

/**
 * 下单函数
 * @param account 资金账号
 * @param trdAccount 股东账号（上海或深圳）
 * @param boardId 交易板块 ("10" 上海, "00" 深圳)
 * @param symbol 证券代码
 * @param orderQty 委托数量（股，100的整数倍）
 * @param orderPrice 委托价格（限价单）或 "MKT"（市价单）
 * @param isBuy true-买入, false-卖出
 * @param acctType 账户类型
 * @param orderRef 委托引用（可选，用于标识订单）
 * @return true-成功, false-失败
 */
bool PlaceOrder(
    const std::string &account,
    const std::string &trdAccount,
    const std::string &boardId,
    const std::string &symbol,
    uint32_t orderQty,
    const std::string &orderPrice,
    bool isBuy,
    OXAccountType acctType = OX_ACCOUNT_STOCK,
    const std::string &orderRef = "")
{
    COXReqOrderTicketField req;
    memset(&req, 0, sizeof(req));

    // 账户信息
    req.AcctType = acctType;
    snprintf(req.Account, sizeof(req.Account), "%s", account.c_str());
    snprintf(req.Trdacct, sizeof(req.Trdacct), "%s", trdAccount.c_str());
    snprintf(req.BoardId, sizeof(req.BoardId), "%s", boardId.c_str());

    // 业务类型：100-买入，101-卖出
    req.StkBiz = isBuy ? 100 : 101;

    // 委托类型：100-限价单，121-市价单（最优成交剩余撤销）
    if (orderPrice == "MKT" || orderPrice == "mkt")
    {
        req.StkBizAction = 121;  // 市价单
        snprintf(req.OrderPrice, sizeof(req.OrderPrice), "0");
    }
    else
    {
        req.StkBizAction = 100;  // 限价单
        snprintf(req.OrderPrice, sizeof(req.OrderPrice), "%s", orderPrice.c_str());
    }

    // 证券代码和数量
    snprintf(req.Symbol, sizeof(req.Symbol), "%s", symbol.c_str());
    req.OrderQty = orderQty;

    // 委托引用（可选，用于标识订单）
    if (!orderRef.empty())
    {
        snprintf(req.OrderRef, sizeof(req.OrderRef), "%s", orderRef.c_str());
    }
    else
    {
        // 使用时间戳作为默认委托引用
        auto now = std::chrono::system_clock::now();
        auto timestamp = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();
        snprintf(req.OrderRef, sizeof(req.OrderRef), "%ld", timestamp);
    }

    std::cout << "\n========== 下单请求 ==========" << std::endl;
    std::cout << "证券代码: " << symbol << std::endl;
    std::cout << "委托方向: " << (isBuy ? "买入" : "卖出") << std::endl;
    std::cout << "委托数量: " << orderQty << " 股" << std::endl;
    std::cout << "委托价格: " << (orderPrice == "MKT" ? "市价" : orderPrice) << std::endl;
    std::cout << "交易板块: " << boardId << std::endl;
    std::cout << "委托引用: " << req.OrderRef << std::endl;
    std::cout << "============================\n" << std::endl;

    int ret = g_TradeApi->OnReqOrderTicket(0, &req);
    if (ret != 0)
    {
        std::cerr << "下单请求失败，返回值: " << ret << std::endl;
        return false;
    }

    std::cout << "下单请求已发送，等待回报..." << std::endl;
    return true;
}

/**
 * 撤单函数
 * @param account 资金账号
 * @param boardId 交易板块 ("10" 上海, "00" 深圳)
 * @param orderNo 委托编号
 * @param acctType 账户类型
 * @return true-成功, false-失败
 */
bool CancelOrder(
    const std::string &account,
    const std::string &boardId,
    int64_t orderNo,
    OXAccountType acctType = OX_ACCOUNT_STOCK)
{
    COXReqCancelTicketField req;
    memset(&req, 0, sizeof(req));

    req.AcctType = acctType;
    snprintf(req.Account, sizeof(req.Account), "%s", account.c_str());
    snprintf(req.BoardId, sizeof(req.BoardId), "%s", boardId.c_str());
    req.OrderNo = orderNo;

    std::cout << "\n========== 撤单请求 ==========" << std::endl;
    std::cout << "委托编号: " << orderNo << std::endl;
    std::cout << "交易板块: " << boardId << std::endl;
    std::cout << "============================\n" << std::endl;

    int ret = g_TradeApi->OnReqCancelTicket(0, &req);
    if (ret != 0)
    {
        std::cerr << "撤单请求失败，返回值: " << ret << std::endl;
        return false;
    }

    std::cout << "撤单请求已发送" << std::endl;
    return true;
}

/**
 * 清理资源
 */
void Cleanup()
{
    if (g_TradeApi)
    {
        g_TradeApi->Stop();
        gxReleaseTradeApi(g_TradeApi);
        g_TradeApi = nullptr;
        std::cout << "API 资源已释放" << std::endl;
    }
}

/**
 * 主函数示例
 */
int main()
{
    std::cout << "=== 股票下单示例程序 ===" << std::endl;

    // 配置信息（请根据实际情况修改）
    std::string account = "110060035050";              // 资金账号
    std::string password = "111111";                   // 密码
    std::string shTrdAccount = "A197407210";           // 上海股东账号
    std::string szTrdAccount = "0000035074";           // 深圳股东账号
    OXAccountType acctType = OX_ACCOUNT_STOCK;         // 账户类型：现货

    // 1. 初始化 API
    if (!InitAPI())
    {
        std::cerr << "初始化失败，程序退出" << std::endl;
        return -1;
    }

    // 2. 用户登录
    if (!Login(account, password, acctType))
    {
        std::cerr << "登录失败，程序退出" << std::endl;
        Cleanup();
        return -1;
    }

    // 等待一下确保登录完成
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // 3. 下单示例

    // 示例1：限价买入上海股票
    std::cout << "\n>>> 示例1：限价买入上海股票 600000" << std::endl;
    PlaceOrder(
        account,           // 资金账号
        shTrdAccount,      // 上海股东账号
        "10",              // 上海交易板块
        "600000",          // 证券代码
        100,               // 委托数量（100股）
        "9.90",            // 委托价格（限价）
        true,              // 买入
        acctType           // 账户类型
    );

    // 等待回报
    std::this_thread::sleep_for(std::chrono::seconds(2));

    // 示例2：市价卖出深圳股票
    std::cout << "\n>>> 示例2：市价卖出深圳股票 000001" << std::endl;
    PlaceOrder(
        account,           // 资金账号
        szTrdAccount,      // 深圳股东账号
        "00",              // 深圳交易板块
        "000001",          // 证券代码
        100,               // 委托数量（100股）
        "MKT",             // 市价单
        false,             // 卖出
        acctType           // 账户类型
    );

    // 等待回报
    std::this_thread::sleep_for(std::chrono::seconds(2));

    // 示例3：限价卖出
    std::cout << "\n>>> 示例3：限价卖出" << std::endl;
    // 注意：实际使用时，请根据持仓情况和市场价格调整参数
    // PlaceOrder(
    //     account,
    //     shTrdAccount,
    //     "10",
    //     "600000",
    //     100,
    //     "10.50",
    //     false,
    //     acctType
    // );

    // 等待回报（通常需要等待几秒以接收委托回报和可能的成交回报）
    std::cout << "\n等待回报中..." << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(5));

    // 4. 如果需要撤单，使用以下代码
    // std::cout << "\n>>> 撤单示例" << std::endl;
    // CancelOrder(account, "10", 1234567890, acctType);
    // std::this_thread::sleep_for(std::chrono::seconds(2));

    std::cout << "\n程序运行完成，按回车键退出..." << std::endl;
    std::cin.get();

    // 5. 清理资源
    Cleanup();

    return 0;
}

