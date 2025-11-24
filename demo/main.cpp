
#include "OXTradeApi.h"
#include "OXTradeApiConst.h"
#include "OXTradeApiStruct.h"
#include "OXTradeApiType.h"

#include "inireader.h"
#include "getopt.hpp"

#include <iostream>
#include <string>
#include <regex>
#include <chrono>
#include <thread>
#include <fstream>

GuosenOXTradeApi * g_TradeApi;
OXAccountType g_acctType;
std::string g_acct;
std::string g_passwd;
std::string g_shTrdAcct;
std::string g_szTrdAcct;

static bool g_logedOn = false;




class StkSpi :public GuosenOXTradeSpi
{
public:
	virtual void OnRspLogon(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspLogonField *pField) override
	{
		std::cout << __FUNCTION__ << " called : " << pError->ErrorInfo << std::endl;
		g_logedOn = true;
		return;
	}

	virtual void OnRspTradeAccounts(int nRequest,const CRspErrorField *pError, bool bLast, const COXRspTradeAcctField *pField) override
	{
		std::cout << __FUNCTION__ << " called" << std::endl;
		std::cout << pField->BoardId << " " << pField->TrdAcct << std::endl;
	}

	//委托信息推送
	virtual void OnRtnOrder(const COXOrderTicket *pRtnOrderTicket) override
	{
		std::cout << __FUNCTION__ << " Symbol : " << pRtnOrderTicket->Symbol << " orderPrice : "
			<< pRtnOrderTicket->OrderPrice << " \norderQty: " << pRtnOrderTicket->OrderQty
			<< " FilledQty : " << pRtnOrderTicket->FilledQty << " \ncanceledQty : " << pRtnOrderTicket->CanceledQty
			<< " orderState : " << pRtnOrderTicket->OrderState << " OrderID : " << pRtnOrderTicket->OrderNo 
            <<" OrderRef : "<<pRtnOrderTicket->OrderRef
            <<" ExeInfo : " << pRtnOrderTicket->ExeInfo
            << std::endl;
	}
	//成交信息推送
	virtual void OnRtnOrderFilled(const COXOrderFilledField *pFilledInfo) override
	{
		std::cout << __FUNCTION__ << " symbol: " << pFilledInfo->Symbol << " FilledPrice : " << pFilledInfo->FilledPrice
			<< "\n FilledQty : " << pFilledInfo->FilledQty << " orderID : " << pFilledInfo->OrderNo 
            << "\n FilledAmt : " << pFilledInfo->FilledAmt 
            <<" OrderRef : "<<pFilledInfo->OrderRef
            << std::endl;
	}
	// ...

	virtual void OnRspCancelTicket(int nRequest, const CRspErrorField *pError, const COXRspCancelTicketField * pField) override
	{
		if (pError && pError->ErrorId)
		{
			std::cout << "errorID : " << pError->ErrorId << "errorInfo : " << pError->ErrorInfo << std::endl;
			return;
		}

		if (nullptr != pField)
		{
			std::cout << " symbol : " << pField->Symbol << " exeInfo : " << pField->ExeInfo
				<< " orderID: " << pField->OrderNo << " orderState : " << pField->OrderState
				<< std::endl;
		}
	}

	virtual void OnRspQueryOrders(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspOrderField *pField) override
	{
		if (pError && pError->ErrorId)
		{
			std::cout << pError->ErrorInfo << std::endl;
		}

		if (pField)
		{
			std::cout << " orderID: " << pField->OrderNo << " symbol " << pField->Symbol << " price: " << pField->OrderPrice
				<< " filledQty: " << pField->FilledQty << " canceledQty: " << pField->CanceledQty << std::endl;
		}
	}

	virtual void OnRspQueryBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspBalanceField *pField) override
	{
		if (pError && pError->ErrorId)
		{
			std::cout << pError->ErrorInfo << std::endl;
		}

		if (pField)
		{
			std::cout << " AcctWorth: " << pField->AccountWorth << " FundValue " << pField->FundValue << " MarketValue: " << pField->MarketValue
				<< "Available : " << pField->Avaiable << std::endl;
		}
	}

	virtual void OnRspQueryPositions(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspPositionField *pField) override
	{
		if (pError && pError->ErrorId)
		{
			std::cout << pError->ErrorInfo << std::endl;
		}

		if (pField)
		{
			std::cout << " Symbol: " << pField->Symbol << " Avl: " 
                << pField->StkAvl << " Freeze: " << pField->StkFrz 
                << " StkTrdEtfCreationCount: " << pField->StkTrdEtfCreationCount
                <<" StkTrdEtfRedemptionCount: " <<pField->StkTrdEtfRedemptionCount<< std::endl;
		}
	}
	
	virtual void OnRspQueryFilledDetails(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspFilledDetailField *pField) override
	{
		if (pError && pError->ErrorId)
		{
			std::cout << pError->ErrorInfo << std::endl;
		}

		if (pField)
		{
			std::cout << " Symbol: " << pField->Symbol << " FilledType: " << pField->FilledType << " qty: " << pField->FilledQty << " price: " << pField->FilledPrice << std::endl;
		}
	}
	
	// 融资融券 负债查询
	virtual void OnRspQueryCreditBalanceDebt(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditBalanceDebtField *pField) override
	{
		std::cout << "FiAmt:" << pField->FiAmt << "TotalFiFee:" << pField->TotalFiFee << "FICredit:" << pField->FICredit << std::endl;
	}

	virtual void OnRspCreditRepay(int nRequest, const CRspErrorField *pError, const COXRspCreditRepay *pField) override
	{
		std::cout << __FUNCTION__ << " called " << std::endl;
	}

    virtual void OnRspQueryCreditTargetStocks(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditTargetStocksField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId == 0)
        {
            std::cout << "Symbol: " << pField->Symbol << " StkName: " << pField->StkName
                << " FIMarginRatio: " << pField->FIMarginRatio << " SLMarginRatio: " << pField->SLMarginRatio
                << " CurrEnableFI: " << pField->CurrEnableFI << " CurrEnableSL: " << pField->CurrEnableSL 
                << " CreditFundCtl: " << pField->CreditFundCtl << " CreditStkCtl: " << pField->CreditStkCtl
                << std::endl;
        }
        
    }
    virtual void OnRspQueryCreditCollateralsStocks(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditCollatalStocksField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId == 0)
        {
            std::cout << "Symbol: " << pField->Symbol << " StkName: " << pField->StkName << " BoardId: " << pField->BoardId
                << " CollatRatio: " << pField->CollatRatio << std::endl;

        }
    }

    virtual void OnRspQueryCreditContracts(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditContractField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId == 0)
        {
            std::cout << "Symbol: " << pField->Symbol << " BoardId: " << pField->BoardId
                << " CashNo : " << pField->CashNo
                << " TrdDate : " << pField->TrdDate
                << " ContractType: " << pField->ContractType
                << " Trdacct: " << pField->Trdacct
                << " ExchangeId: " << pField->ExchangeId
                << " BoardId: " << pField->BoardId
                << " OpeningDate: " << pField->OpeningDate
                << " OrderId: " << pField->OrderId
                << " FIDebtsAmt: " << pField->FIDebtsAmt
                << " SLDebtsQty: " << pField->SLDebtsQty
                << " RepaidQty: " << pField->RepaidQty
                << " RepaidAmt: " << pField->RepaidAmt
                << " ContractStatus: " << pField->ContractStatus
                << " ContractExpireDate: " << pField->ContractExpireDate
                << " MarginRatio: " << pField->MarginRatio
                << " MarginAmt: " << pField->MarginAmt
                << " Rights: " << pField->Rights
                << " OverdueFee: " << pField->OverdueFee
                << " LastRepayDate: " << pField->LastRepayDate
                << " CustCode: " << pField->CustCode
                << " Account: " << pField->Account
                << " Currency: " << pField->Currency
                << " IntOrg: " << pField->IntOrg
                << " OrderPrice: " << pField->OrderPrice
                << " OrderQty: " << pField->OrderQty
                << " OrderAmt: " << pField->OrderAmt
                << " WithdrawnQty: " << pField->WithdrawnQty
                << " MatchedQty: " << pField->MatchedQty
                << " MatchedAmt: " << pField->MatchedAmt
                << " RltSettAmt: " << pField->RltSettAmt
                << " SLDebtsMktvalue: " << pField->SLDebtsMktvalue
                << " RltRepaidQty: " << pField->RltRepaidQty
                << " RltRepaidAmt: " << pField->RltRepaidAmt
                << " MatchedAmtRepay: " << pField->MatchedAmtRepay
                << " CalIntDate: " << pField->CalIntDate
                << " ContractInt: " << pField->ContractInt
                << " ContractIntAccrual: " << pField->ContractIntAccrual
                << " OverRights: " << pField->OverRights
                << " RightsRepay: " << pField->RightsRepay
                << " RightsRlt: " << pField->RightsRlt
                << " OverRightsQty      " << pField->OverRightsQty
                << " RightsQtyRepay     " << pField->RightsQtyRepay
                << " RightsQtyRlt       " << pField->RightsQtyRlt
                << " OverRightsQtyRlt   " << pField->OverRightsQtyRlt
                << " ContractFee		   " << pField->ContractFee
                << " FeeRepay		" << pField->FeeRepay
                << " FeeRlt			   " << pField->FeeRlt
                << " OverDuefeeRlt	" << pField->OverDuefeeRlt
                << " PuniDebts		" << pField->PuniDebts
                << " PuniDebtsRepay	   " << pField->PuniDebtsRepay
                << " PuniDebtsRlt	" << pField->PuniDebtsRlt
                << " PuniFee			   " << pField->PuniFee
                << " PuniFeeRepay	" << pField->PuniFeeRepay
                << " PuniFeeRlt		   " << pField->PuniFeeRlt
                << " PuniRights		   " << pField->PuniRights
                << " PuniRightsRepay	   " << pField->PuniRightsRepay
                << " PuniRightsRlt	" << pField->PuniRightsRlt
                << " ClosingDate        " << pField->ClosingDate
                << " ClosingPrice	" << pField->ClosingPrice
                << " OpOrg              " << pField->OpOrg
                << " ContractCls        " << pField->ContractCls
                << " ProIncome		" << pField->ProIncome
                << " PledgeCuacct	" << pField->PledgeCuacct
                << " FIRepayAmt		   " << pField->FIRepayAmt
                << " SLRepayQty         " << pField->SLRepayQty
                << std::endl;

        }

    }
    virtual void OnRspQueryCreditSecuLendQuota(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditSecuLendQuotaField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId == 0)
        {
            std::cout << "Symbol: " << pField->Symbol << " BoardId: " << pField->BoardId
                <<" AssetBln : " << pField->AssetBln 
                << " AssetAvl : " << pField->AssetAvl 
                <<" CashNo: " <<pField->CashNo
                << std::endl;

        }
    }
    
    virtual void OnRspQueryCreditReimbursibleBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditReimbursibleBalField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId == 0)
        {
            std::cout << " Account: " << pField->Account
                << " CanRepayAmt: " << pField->CanRepayAmt
                << " FITotalDebts: " << pField->FITotalDebts
                << " Mayrepay: " << pField->Mayrepay
                << " TotalSLFee: " << pField->TotalSLFee
                << std::endl;
        }

    }
    virtual void OnRspQueryCreditSLContractSummary(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspCreditSLContractSummaryField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId == 0)
        {
            std::cout << "Symbol: " << pField->Symbol 
                << " Account: " << pField->Account
                << " BoardId: " << pField->BoardId                
                << " OpenQty: " << pField->OpenQty
                << " RepayQty: " << pField->RepayQty
                << " SettAmt: " << pField->SettAmt
                << " RepayAmt: " << pField->RepayAmt
                << " OrderQty: " << pField->OrderQty
                << " RightsQty: " << pField->OverRightsQty
                << " CollatRatio         " << pField->CollatRatio
                << " SlMarginRatio         " << pField->SlMarginRatio
                << " RltOpenQty         " << pField->RltOpenQty
                << " RltSettAmt         " << pField->RltSettAmt
                << std::endl;

        }

    }

    //期权
    virtual void OnRspQueryStockOptionBalance(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspStockOptionBalanceField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId)
            return;
        std::cout << "FundExeMargin" << pField->FundExeMargin;
        std::cout << "FundExeFrz	  " << pField->FundExeFrz;
        std::cout << "FundFeeFrz	  " << pField->FundFeeFrz;
        std::cout << "Paylater	  " << pField->Paylater;
        std::cout << "PreadvaPay	  " << pField->PreadvaPay;
        std::cout << "ExpPenInt	  " << pField->ExpPenInt;
        std::cout << "FundDraw	  " << pField->FundDraw;
        std::cout << "FundAvlRlt	  " << pField->FundAvlRlt;
        std::cout << "MarginInclDyn" << pField->MarginInclDyn;
        std::cout << "DailyInAmt	  " << pField->DailyInAmt;
        std::cout << "DailyOutAmt  " << pField->DailyOutAmt;
        std::cout << "FundRealAvl  " << pField->FundRealAvl;
        std::cout<<std::endl;
    }
    virtual void OnRspQueryStockOptionPositions(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspStockOptionPositionField *pField) override
    {
        std::cout << __FUNCTION__ << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
    }

    //ETF信息查询应答
    virtual void OnRspQueryETFInfo(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspETFInfoField *pField) override
    {
        std::cout << __FUNCTION__ <<" request "<<nRequest << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId)
            return;
    }
    //ETF成分股信息查询应答
    virtual void OnRspQueryETFComponentInfo(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspETFComponentInfoField *pField) override
    {
        std::cout << __FUNCTION__ << " request " << nRequest <<" error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId)
            return;

    }


	
	virtual int OnConnected() override
	{
		std::cout << __FUNCTION__ << " called" << std::endl;
		return 0;
	}

	virtual int OnDisconnected() override
	{
		std::cout << __FUNCTION__ << " called" << std::endl;
		return 0;
	}
};



int Work()
{
	while (true)
	{
		std::cout << "输入你的命令 :\n"
			"\t限价买100手000001： BUY SH.600000 100 9.9\n"
			"\t市价卖100手000001： SELL SZ.000001 100 MKT\n"
			"\t撤掉订单 : CANCEL SH Q123456\n"
			"\t查询股东账号 : QUERY ACCOUNT\n"
			"\t查询持仓 : QUERY POSITION\n"
            "\t查询委托 : QUERY ORDER\n"
			"\t查询成交明细 : QUERY DETAIL\n"
			"\t查询资金 : QUERY BALANCE\n"
			"\t申购ETF : BUYETF SZ.159901 1000000 1\n"
            "\t申购ETF : BUYETF SH.510051 900000 1\n"
			"\t融资融券，融资买入: BUYCREDIT SH.601088 100 18.41\n"
			"\t融资融券，融券卖出: SELLCREDIT SH.601088 100 18.41\n"
			"\t担保品买入: BUYGUARD SH.600000 100 9.9\n"
			"\t担保品卖出: SELLGUARD SH.600000 100 9.9\n"
			"\t融资融券，负债查询: CREDIT QUERY\n"
			"\t融资融券，直接还款: CREDIT REPAY\n"
            "\t融资融券，标的券查询: CREDIT STOCK LIST\n"
            "\t融资融券，担保券查询: CREDIT COLLATERALS STOCKS\n"
            "\t融资融券，融券头寸查询: CREDIT SECULEND QUOTA\n"
            "\t融资融券，资产负债查询: CREDIT BALANCE DEBT\n"
            "\t融资融券，融资融券合约查询: CREDIT CONTRACTS\n"
            "\t融资融券，可偿还金额查询: CREDIT REIMBURSIBLE BALANCE\n"
            "\t融资融券，融券合约汇总信息: CREDIT CONTRACTSUMMARY\n"
            "\t期权    ，期权资金信息查询: OPTION FUND\n"
            "\t期权    ，期权持仓信息查询: OPTION POSITION\n"
            "\tETF     ，ETF信息查询: ETF INFO\n"
            "\tETF     ，ETF成分股信息查询: ETF COMPONENT INFO\n"

			"\t 退出 : q \n" << std::endl;

		std::cout << "please input :";
		std::string input;
		getline(std::cin, input);
		std::cout << "your input is: #" << input << "#" << std::endl;
		if (input == "q")
			return 0;

		std::regex reg3("^QUERY ACCOUNT$"); //查询交易账户
		std::regex reg4("^QUERY POSITION$"); //查询持仓
		std::regex reg5("^QUERY DETAIL$"); //查询成交明细
		std::regex reg6("^QUERY BALANCE$"); //查询资金情况
        std::regex reg7("^QUERY ORDER$");   //查询委托

		std::smatch result;
		//下单
		if (regex_match(input, result,std::regex("^(BUY|SELL|BUYETF|SELLETF|BUYCREDIT|SELLCREDIT|BUYGUARD|SELLGUARD) (SH|SZ)\.([0-9]{1,10}) ([0-9]{1,10}) ([.0-9]{1,10}|MKT)$")))
		{
			auto command = result[1].str();
			auto mkt = result[2].str();
			auto code = result[3].str();
			auto num = result[4].str();
			auto price = result[5].str();
			
			COXReqOrderTicketField req;
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());

			bool isCredit = false;

			if (command == "BUY")
				req.StkBiz = 100;
			else if (command == "SELL")
				req.StkBiz = 101;
			else if (command == "BUYETF")
				req.StkBiz = 181; // ETF申购
			else if (command == "SELLETF")
				req.StkBiz = 182; // ETF赎回
			else if (command == "BUYCREDIT")
			{
				req.StkBiz = 702; // 融资买入
				isCredit = true;
			}
			else if (command == "SELLCREDIT")
			{
				req.StkBiz = 703; // 融券卖出
				isCredit = true;
			}
			else if (command == "BUYGUARD")
			{
				req.StkBiz = 700; //担保品买入
				isCredit = true;
			}
			else if (command == "SELLGUARD")
			{
				req.StkBiz = 701; //担保品卖出
				isCredit = true;
			}


			if ("SH" == mkt )
			{
				snprintf(req.BoardId, sizeof(req.BoardId), "10");
				snprintf(req.Trdacct, sizeof(req.Trdacct), "%s", g_shTrdAcct.c_str());
			}
			else if ("SZ" == mkt )
			{
				snprintf(req.BoardId, sizeof(req.BoardId), "00");
				snprintf(req.Trdacct, sizeof(req.Trdacct), "%s", g_szTrdAcct.c_str());
			}
			
			snprintf(req.Symbol, sizeof(req.Symbol), "%s", code.c_str());

			req.OrderQty = std::atoi(num.c_str());

			if (price == "MKT") // 市价单
			{
				req.StkBizAction = 121; // 最优成交剩撤
				snprintf(req.OrderPrice, sizeof(req.OrderPrice), "0");

			}
			else
			{
				req.StkBizAction = 100; //限价单
				snprintf(req.OrderPrice, sizeof(req.OrderPrice), "%s", price.c_str());
			}

            snprintf(req.OrderRef, sizeof(req.OrderRef), "%s", "1111111111111111");

			g_TradeApi->OnReqOrderTicket(0, &req);
			std::cout << "place order finished" << std::endl;
		}
		else if (regex_match(input, result, std::regex("^CANCEL (SH|SZ) (\\S+)$")))
		{
			//撤单
			auto mkt = result[1].str();
			auto code = result[2].str();

			COXReqCancelTicketField reqCancelOrderTicket;
			memset(&reqCancelOrderTicket, 0, sizeof(reqCancelOrderTicket));
			reqCancelOrderTicket.AcctType = OX_ACCOUNT_STOCK;
			snprintf(reqCancelOrderTicket.Account, sizeof(reqCancelOrderTicket.Account), "%s", g_acct.c_str());

			if (mkt == "SH")
				snprintf(reqCancelOrderTicket.BoardId, sizeof(reqCancelOrderTicket.BoardId), "10");
			else if (mkt == "SZ")
				snprintf(reqCancelOrderTicket.BoardId, sizeof(reqCancelOrderTicket.BoardId), "00");
            reqCancelOrderTicket.OrderNo = std::atoi(code.c_str());
			//snprintf(reqCancelOrderTicket.OrderId, sizeof(reqCancelOrderTicket.OrderId), "%s", code.c_str());
			g_TradeApi->OnReqCancelTicket(0, &reqCancelOrderTicket);
		}
		else if (regex_match(input, reg3))
		{
			//查股东账号
			COXReqTradeAcctField req;
			memset(&req, 0, sizeof(req));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqTradeAccounts(0, &req);

		}
		else if (regex_match(input, reg4))
		{
			//查股票持仓
			COXReqPositionField req;
			memset(&req, 0, sizeof(req));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqQueryPositions(0, &req);
		}
		else if (regex_match(input, reg5))
		{
			// 查成交明细
			COXReqFilledDetailField reqFilledDetailField;
			memset(&reqFilledDetailField, 0, sizeof(reqFilledDetailField));
			reqFilledDetailField.AcctType = OX_ACCOUNT_STOCK;
			snprintf(reqFilledDetailField.Account, sizeof(reqFilledDetailField.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqQueryFilledDetails(0, &reqFilledDetailField);
		}
		else if (regex_match(input, reg6))
		{
			// 查询资金	
			COXReqBalanceField req;
			memset(&req, 0, sizeof(COXReqBalanceField));
			req.AcctType = OX_ACCOUNT_STOCK;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqQueryBalance(0, &req);
		}
        else if (regex_match(input, reg7)) {
            // 查询委托	
            COXReqOrdersField req;
            memset(&req, 0, sizeof(COXReqOrdersField));
            req.AcctType = OX_ACCOUNT_STOCK;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqQueryOrders(0, &req);

        }
		// 融资融券查询负债
		else if (regex_match(input, std::regex("CREDIT QUERY")))
		{
			COXReqCreditBalanceDebt req;
			memset(&req, 0, sizeof(COXReqCreditBalanceDebt));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			req.Currency = '0';
			g_TradeApi->OnReqCreditBalanceDebt(0, &req);
		}
		// 融资融券直接还款
		else if (regex_match(input, result, std::regex("^CREDIT REPAY (\\S+)$")))
		{
			auto money = result[1].str();
			COXReqCreditRepay req;
			memset(&req, 0, sizeof(COXReqCreditRepay));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			snprintf(req.RepayContractAmt, sizeof(req.RepayContractAmt), "%s", money.c_str());
			req.RepayType = '0'; // '0' 偿还融资欠款; '1'偿还融资费用
			g_TradeApi->OnReqCreditRepay(0, &req);
		}
        //标的券查询
        else if (regex_match(input, result, std::regex("CREDIT STOCK LIST")))
        {
            
            COXReqCreditTargetStocks req;
            memset(&req, 0, sizeof(COXReqCreditTargetStocks));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditTargetStocks(0, &req);
        }
        //担保券查询
        else if (regex_match(input, result, std::regex("CREDIT COLLATERALS STOCKS")))
        {

            COXReqCreditCollateralsStocks req;
            memset(&req, 0, sizeof(COXReqCreditCollateralsStocks));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditCollateralsStocks(0, &req);
        }
        //融券头寸查询
        else if (regex_match(input, result, std::regex("CREDIT SECULEND QUOTA")))
        {

            COXReqCreditSecuLendQuota req;
            memset(&req, 0, sizeof(COXReqCreditSecuLendQuota));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            snprintf(req.CashNo, sizeof(req.CashNo), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditSecuLendQuota(0, &req);
        }
        //资产负债查询
        else if (regex_match(input, result, std::regex("CREDIT BALANCE DEBT")))
        {

            COXReqCreditBalanceDebt req;
            memset(&req, 0, sizeof(COXReqCreditBalanceDebt));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditBalanceDebt(0, &req);
        }
        //融资融券合约查询
        else if (regex_match(input, result, std::regex("CREDIT CONTRACTS")))
        {

            COXReqCreditContracts req;
            memset(&req, 0, sizeof(COXReqCreditContracts));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditContracts(0, &req);
        }
        //可偿还金额查询
        else if (regex_match(input, result, std::regex("CREDIT REIMBURSIBLE BALANCE")))
        {

            COXReqCreditReimbursibleBalance req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditReimbursibleBalance(0, &req);
        }
        //融券合约汇总信息
        else if (regex_match(input, result, std::regex("CREDIT CONTRACTSUMMARY")))
        {

            COXReqCreditSLContractSummary req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditSLContractSummary(0, &req);
        }
        else if (regex_match(input, result, std::regex("OPTION FUND")))
        {
            COXReqStockOptionBalance req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqStockOptionBalance(0, &req);
        }
        else if (regex_match(input, result, std::regex("OPTION POSITION")))
        {
            COXReqStockOptionPositions req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqStockOptionPositions(0, &req);
        }
        else if (regex_match(input, result, std::regex("ETF INFO")))
        {
            COXReqETFInfo req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqQueryETFInfo(999888, &req);
        }
        else if (regex_match(input, result, std::regex("ETF COMPONENT INFO")))
        {
            COXReqETFComponentInfo req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            snprintf(req.ETFCode, sizeof(req.ETFCode), "%s", "510051");
            snprintf(req.BoardId, sizeof(req.BoardId), "%s", "10");
            g_TradeApi->OnReqQueryETFComponentInfo(999888, &req);
        }
        else 
		{
			std::cout << "unsupport command" << std::endl;
		}
		
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}

	return 0;
}

int main()
{
	std::string strCfgFile = getarg("", "--file");
	if (strCfgFile.empty())
	{
		std::cerr << "can't find config file" << std::endl;
		return 0;
	}

	std::cout << "use config file : " << strCfgFile << std::endl;
	INIReader reader(strCfgFile);
	if (reader.ParseError() < 0)
	{
		std::cout << "Can't load 'config.ini' " << std::endl;
		getchar();
		return -1;
	}
	
	//读取ini配置的账号
	g_acct = reader.Get("user", "acct", "");
	g_passwd = reader.Get("user", "password", "");
    auto acctType = reader.Get("user", "acct_type", "0");
    g_acctType =(OXAccountType) acctType.data()[0];

	g_shTrdAcct = reader.Get("user", "sh_trade_account", ""); 
	g_szTrdAcct = reader.Get("user", "sz_trade_account", "");
	

	

	printf("user.acct=[%s],user.sh_trade_account=[%s],user.sz_trade_account=[%s]\n", g_acct.c_str(), g_shTrdAcct.c_str(), g_szTrdAcct.c_str());
	// 获取并且初始化交易接口
	g_TradeApi = gxCreateTradeApi();
    std::cout <<"gxCreateTradeApi g_TradeApi " << g_TradeApi<<std::endl;
    StkSpi stkSpi;
    g_TradeApi->RegisterSpi(&stkSpi);
    std::cout << "RegisterSpi g_TradeApi " << g_TradeApi << std::endl;
    const char *pError = nullptr;
	int iInitRet = g_TradeApi->Init(&pError);
    printf("Init return %d, error info %s \n", iInitRet, pError);
    std::cout << "Init g_TradeApi " << g_TradeApi << std::endl;

	// 登录
	COXReqLogonField req;
	snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
	//req.AcctType = OX_ACCOUNT_STOCK;
    req.AcctType = g_acctType;
    
	snprintf(req.Password, sizeof(req.Password), "%s", g_passwd.c_str());
	int iLogon = g_TradeApi->OnReqLogon(0, &req);
    printf("Logon return %d\n", iLogon);
    std::cout << "OnReqLogon g_TradeApi " << g_TradeApi << std::endl;
  
	while(!g_logedOn)
		std::this_thread::yield();

	Work();

	getchar();
	getchar();

	g_TradeApi->Stop();   
    gxReleaseTradeApi(g_TradeApi);

	getchar();
	return 0;
}
