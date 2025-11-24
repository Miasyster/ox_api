
#ifndef _OX_TRADE_API_H_
#define _OX_TRADE_API_H_

#include "OXTradeApiStruct.h"


#if defined(_WIN32) || defined(WIN64) || defined(OS_IS_WINDOWS)
	#ifdef GXOX_TRADEAPI_EXPORTS
		#define GXOX_TRADEAPI __declspec(dllexport)
	#else
		#define GXOX_TRADEAPI __declspec(dllimport)
	#endif
	#define GXOX_API_STDCALL __stdcall
#else
	#define GXOX_TRADEAPI
	#define GXOX_API_STDCALL
#endif

class GuosenOXTradeSpi
{
public:
	virtual ~GuosenOXTradeSpi() {};
    
    //连接事件
    virtual int OnConnected() { return 0; }
    //连接断开事件
    virtual int OnDisconnected() { return 0; }

    //登录
    virtual void OnRspLogon(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspLogonField *pField) {};
    //查股东账号
    virtual void OnRspTradeAccounts(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspTradeAcctField *pField) {};
    //查询当日委托
    virtual void OnRspQueryOrders(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspOrderField *pField) {};
	//查询资金
    virtual void OnRspQueryBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspBalanceField *pField) {};
    //查询持仓
    virtual void OnRspQueryPositions(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspPositionField *pField) {};
    //查询持仓-快速
    virtual void OnRspQueryPositionsEx(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspPositionExField *pField) {};
    

    //查询当日成交
    virtual void OnRspQueryFilledDetails(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspFilledDetailField *pField) {};

	
    //撤单应答
	virtual void OnRspCancelTicket(int nRequest, const CRspErrorField *pError, const COXRspCancelTicketField * pField) {};

    //批量委托应答
    virtual void OnRspBatchOrder(int nRequest, const CRspErrorField *pError, const COXReqBatchOrderTicketField * pField) {};


	//委托信息推送
	virtual void OnRtnOrder(const COXOrderTicket *pRtnOrderTicket) {};
	//成交信息推送
	virtual void OnRtnOrderFilled(const COXOrderFilledField *pFilledInfo) {};

	// 信用交易
	// 直接还款
	virtual void OnRspCreditRepay(int nRequest, const CRspErrorField *pError, const COXRspCreditRepay *pField) {};

	//信用查询相关应答
    //标的券查询应答
	virtual void OnRspQueryCreditTargetStocks(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditTargetStocksField *pField) {};
    //担保券查询应答
    virtual void OnRspQueryCreditCollateralsStocks(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditCollatalStocksField *pField) {};
    //资产负债查询应答
    virtual void OnRspQueryCreditBalanceDebt(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditBalanceDebtField *pField) {};
    //融资融券合约查询应答
    virtual void OnRspQueryCreditContracts(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditContractField *pField) {};
    //融券头寸查询应答
    virtual void OnRspQueryCreditSecuLendQuota(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditSecuLendQuotaField *pField) {};
    //可偿还金额查询应答
    virtual void OnRspQueryCreditReimbursibleBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditReimbursibleBalField *pField) {};
    //融券合约汇总信息应答
    virtual void OnRspQueryCreditSLContractSummary(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditSLContractSummaryField *pField) {};

	//期权
    //期权可用资金应答
	virtual void OnRspQueryStockOptionBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspStockOptionBalanceField *pField) {};
    //期权合约信息应答
    virtual void OnRspQueryStockOptionPositions(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspStockOptionPositionField *pField) {};
    //期权保证金风险查询应答
    virtual void OnRspQueryStockOptionMarginRisk(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspOptionMarginRiskField *pField) {};


    //撤单拒绝推送
    virtual void OnRtnCancelRejected(CRspErrorField *pError, COXOrderTicket *pOrderTicket) {};

    //ETF信息查询应答
    virtual void OnRspQueryETFInfo(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspETFInfoField *pField) {};
    //ETF成分股信息查询应答
    virtual void OnRspQueryETFComponentInfo(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspETFComponentInfoField *pField) {};

    //期货资金应答
    virtual void OnRspQueryFutureBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspFutureBalanceField *pField) {};
    //期货持仓应答
    virtual void OnRspQueryFuturePositions(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspFuturePositionField *pField) {};

};

class GuosenOXTradeApi
{
public:
	
	virtual void RegisterSpi(GuosenOXTradeSpi *pSpi) = 0;
	
    virtual int Init(const char **errMsg = nullptr) = 0;
    virtual int Stop() = 0;

	//登录
    virtual int OnReqLogon(int nRequest, const COXReqLogonField * pField) = 0;
	//查股东账号
	virtual int OnReqTradeAccounts(int nRequest, const COXReqTradeAcctField * pField) = 0;
	//查询当日委托
	virtual int OnReqQueryOrders(int nRequest, const COXReqOrdersField *pField) = 0;
	//查资金
	virtual int OnReqQueryBalance(int nRequest, const COXReqBalanceField *pField) = 0;
	//查持仓
	virtual int OnReqQueryPositions(int nRequest, const COXReqPositionField *pField) = 0;

    //查持仓快速接口（推荐）
    virtual int OnReqQueryPositionsEx(int nRequest, const COXReqPositionExField *pField) = 0;

	//查询当日成交
    virtual int OnReqQueryFilledDetails(int nRequest, const COXReqFilledDetailField *pField) = 0;

	//委托
	virtual int OnReqOrderTicket(int nRequest, const COXReqOrderTicketField *pField) = 0;
	//撤单
	virtual int OnReqCancelTicket(int nRequest, const COXReqCancelTicketField *pField) = 0;

    //批量委托 
    virtual int OnReqBatchOrderTicket(int nRequest, const COXReqBatchOrderTicketField *pField) = 0;
	
	//信用交易直接还款
	virtual int OnReqCreditRepay(int nRequest, const COXReqCreditRepay *pField) = 0;

	//信用交易相关查询接口
    //标的券查询
	virtual int OnReqCreditTargetStocks(int nRequest, const COXReqCreditTargetStocks *pField) = 0;               
    //担保券查询
    virtual int OnReqCreditCollateralsStocks(int nRequest, const COXReqCreditCollateralsStocks *pField) = 0;     
    //资产负债查询 
	virtual int OnReqCreditBalanceDebt(int nRequest, const COXReqCreditBalanceDebt *pField) = 0;                 
    //融资融券合约查询
    virtual int OnReqCreditContracts(int nRequest, const COXReqCreditContracts *pField) = 0;                     
    //融券头寸查询
    virtual int OnReqCreditSecuLendQuota(int nRequest, const COXReqCreditSecuLendQuota *pField) = 0;             
    //可偿还金额查询
	virtual int OnReqCreditReimbursibleBalance(int nRequest, const COXReqCreditReimbursibleBalance *pField) = 0; 
    //融券合约汇总信息
	virtual int OnReqCreditSLContractSummary(int nRequest, const COXReqCreditSLContractSummary *pField) = 0;  

    //期权可用资金
    virtual int OnReqStockOptionBalance(int nRequest, const COXReqStockOptionBalance *pField) = 0;              
    //期权合约信息
    virtual int OnReqStockOptionPositions(int nRequest, const COXReqStockOptionPositions *pField) = 0;    

    //ETF信息查询
    virtual int OnReqQueryETFInfo(int nRequest, const COXReqETFInfo *pField) = 0;
    //ETF成分股信息查询
    virtual int OnReqQueryETFComponentInfo(int nRequest, const COXReqETFComponentInfo *pField)  = 0;


    //查资金-期货
    virtual int OnReqQueryFutureBalance(int nRequest, const COXReqBalanceField *pField) = 0;
    //查持仓-期货
    virtual int OnReqQueryFuturePosition(int nRequest, const COXReqFuturePositionField *pField) = 0;

    //期权查询风险度
    virtual int OnReqQueryOptionMarginRisk(int nRequest, const COXReqOptionMarginRiskDegreeField *pField) = 0;

};

#ifdef __cplusplus
extern "C" {
#endif
	GXOX_TRADEAPI GuosenOXTradeApi * GXOX_API_STDCALL gxCreateTradeApi();
    GXOX_TRADEAPI void GXOX_API_STDCALL gxReleaseTradeApi(GuosenOXTradeApi *pApiObj);
#ifdef __cplusplus
}
#endif

#endif // !_OX_TRADE_API_H_

