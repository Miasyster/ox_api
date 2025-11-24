
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
#ifdef _WIN32
#include <windows.h>
#include <direct.h>
#endif

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

	//ί����Ϣ����
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
	//�ɽ���Ϣ����
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
	
	// ������ȯ ��ծ��ѯ
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

    //��Ȩ
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

    //ETF��Ϣ��ѯӦ��
    virtual void OnRspQueryETFInfo(int nRequest, const CRspErrorField *pError, bool bLast, const COXRspETFInfoField *pField) override
    {
        std::cout << __FUNCTION__ <<" request "<<nRequest << " error: " << pError->ErrorId << " error_info: " << pError->ErrorInfo << std::endl;
        if (pError->ErrorId)
            return;
    }
    //ETF�ɷֹ���Ϣ��ѯӦ��
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
		std::cout << "����������� :\n"
			"\t�޼���100��000001�� BUY SH.600000 100 9.9\n"
			"\t�м���100��000001�� SELL SZ.000001 100 MKT\n"
			"\t�������� : CANCEL SH Q123456\n"
			"\t��ѯ�ɶ��˺� : QUERY ACCOUNT\n"
			"\t��ѯ�ֲ� : QUERY POSITION\n"
            "\t��ѯί�� : QUERY ORDER\n"
			"\t��ѯ�ɽ���ϸ : QUERY DETAIL\n"
			"\t��ѯ�ʽ� : QUERY BALANCE\n"
			"\t�깺ETF : BUYETF SZ.159901 1000000 1\n"
            "\t�깺ETF : BUYETF SH.510051 900000 1\n"
			"\t������ȯ����������: BUYCREDIT SH.601088 100 18.41\n"
			"\t������ȯ����ȯ����: SELLCREDIT SH.601088 100 18.41\n"
			"\t����Ʒ����: BUYGUARD SH.600000 100 9.9\n"
			"\t����Ʒ����: SELLGUARD SH.600000 100 9.9\n"
			"\t������ȯ����ծ��ѯ: CREDIT QUERY\n"
			"\t������ȯ��ֱ�ӻ���: CREDIT REPAY\n"
            "\t������ȯ�����ȯ��ѯ: CREDIT STOCK LIST\n"
            "\t������ȯ������ȯ��ѯ: CREDIT COLLATERALS STOCKS\n"
            "\t������ȯ����ȯͷ���ѯ: CREDIT SECULEND QUOTA\n"
            "\t������ȯ���ʲ���ծ��ѯ: CREDIT BALANCE DEBT\n"
            "\t������ȯ��������ȯ��Լ��ѯ: CREDIT CONTRACTS\n"
            "\t������ȯ���ɳ�������ѯ: CREDIT REIMBURSIBLE BALANCE\n"
            "\t������ȯ����ȯ��Լ������Ϣ: CREDIT CONTRACTSUMMARY\n"
            "\t��Ȩ    ����Ȩ�ʽ���Ϣ��ѯ: OPTION FUND\n"
            "\t��Ȩ    ����Ȩ�ֲ���Ϣ��ѯ: OPTION POSITION\n"
            "\tETF     ��ETF��Ϣ��ѯ: ETF INFO\n"
            "\tETF     ��ETF�ɷֹ���Ϣ��ѯ: ETF COMPONENT INFO\n"

			"\t �˳� : q \n" << std::endl;

		std::cout << "please input :";
		std::string input;
		getline(std::cin, input);
		std::cout << "your input is: #" << input << "#" << std::endl;
		if (input == "q")
			return 0;

		std::regex reg3("^QUERY ACCOUNT$"); //��ѯ�����˻�
		std::regex reg4("^QUERY POSITION$"); //��ѯ�ֲ�
		std::regex reg5("^QUERY DETAIL$"); //��ѯ�ɽ���ϸ
		std::regex reg6("^QUERY BALANCE$"); //��ѯ�ʽ����
        std::regex reg7("^QUERY ORDER$");   //��ѯί��

		std::smatch result;
		//�µ�
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
				req.StkBiz = 181; // ETF�깺
			else if (command == "SELLETF")
				req.StkBiz = 182; // ETF���
			else if (command == "BUYCREDIT")
			{
				req.StkBiz = 702; // ��������
				isCredit = true;
			}
			else if (command == "SELLCREDIT")
			{
				req.StkBiz = 703; // ��ȯ����
				isCredit = true;
			}
			else if (command == "BUYGUARD")
			{
				req.StkBiz = 700; //����Ʒ����
				isCredit = true;
			}
			else if (command == "SELLGUARD")
			{
				req.StkBiz = 701; //����Ʒ����
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

			if (price == "MKT") // �м۵�
			{
				req.StkBizAction = 121; // ���ųɽ�ʣ��
				snprintf(req.OrderPrice, sizeof(req.OrderPrice), "0");

			}
			else
			{
				req.StkBizAction = 100; //�޼۵�
				snprintf(req.OrderPrice, sizeof(req.OrderPrice), "%s", price.c_str());
			}

            snprintf(req.OrderRef, sizeof(req.OrderRef), "%s", "1111111111111111");

			g_TradeApi->OnReqOrderTicket(0, &req);
			std::cout << "place order finished" << std::endl;
		}
		else if (regex_match(input, result, std::regex("^CANCEL (SH|SZ) (\\S+)$")))
		{
			//����
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
			//��ɶ��˺�
			COXReqTradeAcctField req;
			memset(&req, 0, sizeof(req));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqTradeAccounts(0, &req);

		}
		else if (regex_match(input, reg4))
		{
			//���Ʊ�ֲ�
			COXReqPositionField req;
			memset(&req, 0, sizeof(req));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqQueryPositions(0, &req);
		}
		else if (regex_match(input, reg5))
		{
			// ��ɽ���ϸ
			COXReqFilledDetailField reqFilledDetailField;
			memset(&reqFilledDetailField, 0, sizeof(reqFilledDetailField));
			reqFilledDetailField.AcctType = OX_ACCOUNT_STOCK;
			snprintf(reqFilledDetailField.Account, sizeof(reqFilledDetailField.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqQueryFilledDetails(0, &reqFilledDetailField);
		}
		else if (regex_match(input, reg6))
		{
			// ��ѯ�ʽ�	
			COXReqBalanceField req;
			memset(&req, 0, sizeof(COXReqBalanceField));
			req.AcctType = OX_ACCOUNT_STOCK;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			g_TradeApi->OnReqQueryBalance(0, &req);
		}
        else if (regex_match(input, reg7)) {
            // ��ѯί��	
            COXReqOrdersField req;
            memset(&req, 0, sizeof(COXReqOrdersField));
            req.AcctType = OX_ACCOUNT_STOCK;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqQueryOrders(0, &req);

        }
		// ������ȯ��ѯ��ծ
		else if (regex_match(input, std::regex("CREDIT QUERY")))
		{
			COXReqCreditBalanceDebt req;
			memset(&req, 0, sizeof(COXReqCreditBalanceDebt));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			req.Currency = '0';
			g_TradeApi->OnReqCreditBalanceDebt(0, &req);
		}
		// ������ȯֱ�ӻ���
		else if (regex_match(input, result, std::regex("^CREDIT REPAY (\\S+)$")))
		{
			auto money = result[1].str();
			COXReqCreditRepay req;
			memset(&req, 0, sizeof(COXReqCreditRepay));
			req.AcctType = g_acctType;
			snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
			snprintf(req.RepayContractAmt, sizeof(req.RepayContractAmt), "%s", money.c_str());
			req.RepayType = '0'; // '0' ��������Ƿ��; '1'�������ʷ���
			g_TradeApi->OnReqCreditRepay(0, &req);
		}
        //���ȯ��ѯ
        else if (regex_match(input, result, std::regex("CREDIT STOCK LIST")))
        {
            
            COXReqCreditTargetStocks req;
            memset(&req, 0, sizeof(COXReqCreditTargetStocks));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditTargetStocks(0, &req);
        }
        //����ȯ��ѯ
        else if (regex_match(input, result, std::regex("CREDIT COLLATERALS STOCKS")))
        {

            COXReqCreditCollateralsStocks req;
            memset(&req, 0, sizeof(COXReqCreditCollateralsStocks));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditCollateralsStocks(0, &req);
        }
        //��ȯͷ���ѯ
        else if (regex_match(input, result, std::regex("CREDIT SECULEND QUOTA")))
        {

            COXReqCreditSecuLendQuota req;
            memset(&req, 0, sizeof(COXReqCreditSecuLendQuota));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            snprintf(req.CashNo, sizeof(req.CashNo), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditSecuLendQuota(0, &req);
        }
        //�ʲ���ծ��ѯ
        else if (regex_match(input, result, std::regex("CREDIT BALANCE DEBT")))
        {

            COXReqCreditBalanceDebt req;
            memset(&req, 0, sizeof(COXReqCreditBalanceDebt));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditBalanceDebt(0, &req);
        }
        //������ȯ��Լ��ѯ
        else if (regex_match(input, result, std::regex("CREDIT CONTRACTS")))
        {

            COXReqCreditContracts req;
            memset(&req, 0, sizeof(COXReqCreditContracts));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditContracts(0, &req);
        }
        //�ɳ�������ѯ
        else if (regex_match(input, result, std::regex("CREDIT REIMBURSIBLE BALANCE")))
        {

            COXReqCreditReimbursibleBalance req;
            memset(&req, 0, sizeof(req));
            req.AcctType = g_acctType;
            snprintf(req.Account, sizeof(req.Account), "%s", g_acct.c_str());
            g_TradeApi->OnReqCreditReimbursibleBalance(0, &req);
        }
        //��ȯ��Լ������Ϣ
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
#ifdef _WIN32
	// 尝试切换到bin目录，确保Tradelog.prop等配置文件能被正确找到
	// 获取可执行文件所在目录
	char exePath[MAX_PATH];
	GetModuleFileNameA(NULL, exePath, MAX_PATH);
	std::string exeDir = exePath;
	size_t lastSlash = exeDir.find_last_of("\\/");
	if (lastSlash != std::string::npos) {
		exeDir = exeDir.substr(0, lastSlash + 1);
	}
	
	// 尝试切换到bin目录（相对于可执行文件目录）
	std::string binDir = exeDir;
	// 如果可执行文件在bin目录下，直接使用
	// 如果在其他目录（如demo目录），尝试切换到../bin
	if (binDir.find("bin") == std::string::npos) {
		binDir = exeDir + "..\\bin\\";
	}
	
	// 尝试切换到bin目录
	if (SetCurrentDirectoryA(binDir.c_str())) {
		std::cout << "Working directory set to: " << binDir << std::endl;
	} else {
		// 如果失败，尝试直接使用exe目录（假设exe在bin目录下）
		if (SetCurrentDirectoryA(exeDir.c_str())) {
			std::cout << "Working directory set to: " << exeDir << std::endl;
		} else {
			std::cerr << "Warning: Failed to set working directory. Current dir: " << exeDir << std::endl;
		}
	}
#endif

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
	
	//��ȡini���õ��˺�
	g_acct = reader.Get("user", "acct", "");
	g_passwd = reader.Get("user", "password", "");
    auto acctType = reader.Get("user", "acct_type", "0");
    g_acctType =(OXAccountType) acctType.data()[0];

	g_shTrdAcct = reader.Get("user", "sh_trade_account", ""); 
	g_szTrdAcct = reader.Get("user", "sz_trade_account", "");
	

	

	printf("user.acct=[%s],user.sh_trade_account=[%s],user.sz_trade_account=[%s]\n", g_acct.c_str(), g_shTrdAcct.c_str(), g_szTrdAcct.c_str());
	// ��ȡ���ҳ�ʼ�����׽ӿ�
	g_TradeApi = gxCreateTradeApi();
    std::cout <<"gxCreateTradeApi g_TradeApi " << g_TradeApi<<std::endl;
    StkSpi stkSpi;
    g_TradeApi->RegisterSpi(&stkSpi);
    std::cout << "RegisterSpi g_TradeApi " << g_TradeApi << std::endl;
    const char *pError = nullptr;
	int iInitRet = g_TradeApi->Init(&pError);
    printf("Init return %d, error info %s \n", iInitRet, pError);
    std::cout << "Init g_TradeApi " << g_TradeApi << std::endl;

	// ��¼
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
