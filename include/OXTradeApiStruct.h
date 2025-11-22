#ifndef _OX_TRADE_API_STRUCT_H_
#define _OX_TRADE_API_STRUCT_H_

#include <stdint.h>
#include "OXTradeApiType.h"
#include "OXTradeApiConst.h"

#pragma pack(1)

struct CRspErrorField
{
	int  ErrorId;
	char ErrorInfo[OX_ERRORINFO_LENGTH];
};

struct COXReqLogonField
{
	OXAccountType	AcctType;			     //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)
	char Password[OX_PASSWORD_LENGTH];      //交易密码(必需)
	char Reserved[OX_RESERVED_LENGTH];      //保留字段
};

struct COXReqTradeAcctField
{
	OXAccountType	AcctType;			     //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)
};

struct COXReqOrdersField
{
	OXAccountType	AcctType;			     //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)

	char     BoardId[OX_BOARDID_LENGTH];	 //交易板块	
	char     Symbol[OX_SYMBOL_LENGTH];	     //代码
    int64_t  OrderNo;				         //委托编号
	char     QueryPos[OX_QUERYPOS_LENGTH];	 //定位串
    char     QueryFlag; 			         // '1' 可撤单, 不送查询所有
};

struct COXReqBalanceField
{
	OXAccountType	AcctType;			     //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)
};

struct COXReqPositionField
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char ExchangeId;			            //交易市场(弃用)
	char BoardId[OX_BOARDID_LENGTH];		//交易板块	
	char Symbol[OX_SYMBOL_LENGTH];			//代码
};

struct COXReqPositionExField
{
    OXAccountType	AcctType;	            //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
};

struct COXReqFilledDetailField
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char BoardId[OX_BOARDID_LENGTH];		//交易板块	
	char Symbol[OX_SYMBOL_LENGTH];			//代码

    int64_t  OrderNo;				         //委托编号
	char QueryPos[OX_QUERYPOS_LENGTH];		 //定位串
};


struct COXReqOrderTicketField
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)

	char Trdacct[OX_TRDACCT_LENGTH];       //股东账号
	char BoardId[OX_BOARDID_LENGTH];       //交易板块
	int  StkBiz;                            //交易业务
	int  StkBizAction;                      //交易业务指令
	char Symbol[OX_SYMBOL_LENGTH];         //代码
	     
	uint32_t OrderQty;  
	char OrderPrice[OX_ORDERPRICE_LENGTH]; //委托价格
	
    char OrderRef[OX_ORDER_REF_LENGTH];
    char TrdCodeCls;

    //20220419 add 委托扩展信息
    char TrdExInfo[OX_TRD_EXT_INFO_LENGTH]; //委托扩展信息
};

struct COXOrderItem
{
    char Trdacct[OX_TRDACCT_LENGTH];       //股东账号
    char BoardId[OX_BOARDID_LENGTH];       //交易板块
    
    int  StkBiz;                           //交易业务
    int  StkBizAction;                     //交易业务指令
 
    char Symbol[OX_SYMBOL_LENGTH];         //代码
    uint32_t OrderQty;                     //委托数量
    char OrderPrice[OX_ORDERPRICE_LENGTH]; //委托价格

    char OrderRef[OX_ORDER_REF_LENGTH];    //客户委托信息
};

struct COXReqBatchOrderTicketField
{
    OXAccountType	AcctType;	                //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		    //资金账号(必需)
    int  StkBiz;                                //交易业务
    int  StkBizAction;                          //交易业务指令

    uint16_t TotalCount;                        //总委托笔数
    COXOrderItem orderArray[MAX_ORDERS_COUNT];  //委托信息 

};


struct COXReqCancelTicketField
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char BoardId[OX_BOARDID_LENGTH];		//交易板块
    uint32_t  OrderDate;		            //委托日期
    int64_t   OrderNo;			            //委托号
};


struct COXReqCreditTargetStocks
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)

	char ExchangeId;                        //交易市场
	char BoardId[OX_BOARDID_LENGTH];		//交易板块
	char Symbol[OX_SYMBOL_LENGTH];			//代码
	char CurrEnableFI;			            //当日融资
	char CurrEnableSL;			            //当日融券
};

struct COXReqCreditRepay
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)

	char RepayType;                         // '0'偿还融资欠款，'1'偿还融券费用
	char RepayContractAmt[OX_ORDERPRICE_LENGTH];	// 偿还金额                    
};

struct COXRspCreditRepay
{
	char CuacctCode[16];		// 资产账户
	char RealRepayAmt[16];		// 实际还款金额
	char Currency;				// '0' 人民币
	char RepayContractAmt[16];		// 偿还金额
};
struct COXReqCreditCollateralsStocks
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)

	char ExchangeId;                        //交易市场
	char BoardId[OX_BOARDID_LENGTH];		//交易板块
	char Symbol[OX_SYMBOL_LENGTH];			//代码
};

struct COXReqCreditBalanceDebt
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char Currency;                          //货币代码	
};


struct COXReqCreditContracts
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)

	int  BgnDate;                           //开始日期
	int  EndDate;                           //结束日期
	char OrderId[OX_ORDERID_LENGTH];       //合同序号
	char ContractType;                      //合约类型，'0' 融资，‘1’融券

	char CustCode[OX_CUSTCODE_LENGTH];    //客户代码
	char ExchangeId;                       //交易市场
	char BoardId[OX_BOARDID_LENGTH];	   //交易板块

	char Trdacct[OX_TRDACCT_LENGTH];      //交易账户
	char Symbol[OX_SYMBOL_LENGTH];        //证券代码
	int  IntOrg;                           //内部机构
	int  OpOrg;                            //操作机构
	char ContractStatus;                   //合约状态
	char RepayFlag;                        //平仓状态
};

struct COXReqCreditSecuLendQuota
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char CashNo[OX_CASHNO_LENGTH];			//头寸编号(必填)
};

struct COXReqCreditReimbursibleBalance
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
};

struct COXReqCreditSLContractSummary
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char BoardId[OX_BOARDID_LENGTH];		//交易板块
	char Symbol[OX_SYMBOL_LENGTH];			//证券代码
};


struct COXReqStockOptionBalance
{
	OXAccountType	AcctType;	            //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		//资金账号(必需)
	char Currency;			                //货币代码
};

struct COXReqStockOptionPositions
{
    OXAccountType	AcctType;	              //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		  //资金账号(必需)

    char BoardId[OX_BOARDID_LENGTH];		  //交易板块
    char TrdAcct[OX_TRDACCT_LENGTH];		  //交易账户
    char OptNum[OX_OPTNUM_LENGTH];           //合约编码    
    char OptUndlCode[OX_OPTUNDLCODE_LENGTH];                   //标的证券代码  
    char Stkpbu[OX_STKPBU_LENGTH];			  //交易单元    
    char OptSide;                             //持仓方向    
    char OptCvdFlag;                          //备兑标志    
};


struct COXReqETFInfo
{
    OXAccountType	AcctType;	              //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		  //资金账号(必需)

    char BoardId[OX_BOARDID_LENGTH];		  //交易板块
    char ETFCode[OX_SYMBOL_LENGTH];			  //ETF代码(一级市场代码)	
};

struct COXReqETFComponentInfo
{
    OXAccountType	AcctType;	              //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		  //资金账号(必需)

    char BoardId[OX_BOARDID_LENGTH];		  //交易板块(必需)
    char ETFCode[OX_SYMBOL_LENGTH];			  //ETF代码(一级市场代码)(必需)
    char ETFMode;                             //'0':老模式 ‘1’:跨市场全额申赎模式 ‘2’:跨市场净额担保交收
};



struct COXRspLogonField
{
	int  IntOrg;		                     //内部机构            
	char CustCode[OX_CUSTCODE_LENGTH];		 //客户代码
	OXAccountType	AcctType;	             //账户类型(必需)
	char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)

};

struct COXRspTradeAcctField
{
	char CustCode[OX_CUSTCODE_LENGTH];		//客户代码
	char Account[OX_ACCOUNT_LENGTH];       //资金账号
	char ExchangeId;		                //交易市场
	char BoardId[OX_BOARDID_LENGTH];		//交易板块
	char TrdAcctStatus;		                //账户状态
	char TrdAcct[OX_TRDACCT_LENGTH];		//证券账户
	char TrdAcctType;		                //交易账户类别
};

struct COXRspOrderField
{
	char QueryPos[OX_QUERYPOS_LENGTH];
	char Account[OX_ACCOUNT_LENGTH];      //资金账号
	char CustCode[OX_CUSTCODE_LENGTH];    //客户代码
	char Trdacct[OX_TRDACCT_LENGTH];
	char BoardId[OX_BOARDID_LENGTH];
	int  StkBiz;
	int  StkBizAction;
	char Symbol[OX_SYMBOL_LENGTH];

	int32_t  OrderDate;
	char OrderTime[OX_ORDERTIME_LENGTH];
    int64_t  OrderNo;
	
    char OrderRef[OX_ORDER_REF_LENGTH];
	char OrderState;
	char ExeInfo[OX_EXEINFO_LENGTH];
	uint32_t OrderQty;
	char OrderPrice[OX_ORDERPRICE_LENGTH];
	int32_t  FilledQty;
	int32_t  CanceledQty;
	char FilledAmt[OX_FILLEDAMT_LENGTH];
};

struct COXRspBalanceField
{
	char    CustCode[OX_CUSTCODE_LENGTH];		//客户代码
	char    Account[OX_ACCOUNT_LENGTH];       //资金账号
	char	Currency;			                       // 货币
	char    AccountWorth[OX_ACCOUNTWORTH_LENGTH];	   //资产总值
	char	FundValue[OX_FUNDVALUE_LENGTH];		   //资金资产
	char    MarketValue[OX_MARKETVALUE_LENGTH];	   //市值

	char    FundPreBalance[OX_FUNDPREBALANCE_LENGTH]; //资金昨日余额
	char    FundBalance[OX_FUNDBALANCE_LENGTH];	   //资金余额
	char    Avaiable[OX_AVAIABLE_LENGTH];		       //资金可用金额
};

struct COXRspPositionField
{
            
	int   IntOrg;                                  //内部机构            
	char  CustCode[OX_CUSTCODE_LENGTH];           //客户代码            
	char  Account[OX_ACCOUNT_LENGTH];             //资产账户            
	char  BoardId[OX_BOARDID_LENGTH];             //交易板块            
	char  Stkpbu[OX_STKPBU_LENGTH];               //交易单元            
	char  Currency;                                //货币代码            
	char  Symbol[OX_SYMBOL_LENGTH];               //证券代码            
	char  StkName[OX_STKNAME_LENGTH];             //证券名称            
	char  StkCls;                                  //证券类别            
	int64_t StkPrebln;                             //证券昨日余额        
	int64_t StkBln;                                //证券余额            
	int64_t StkAvl;                                //证券可用数量        
	int64_t StkFrz;                                //证券冻结数量        
	int64_t StkUfz;                                //证券解冻数量        
	int64_t StkTrdFrz;                             //证券交易冻结数量    
	int64_t StkTrdUfz;                             //证券交易解冻数量    
	int64_t StkTrdOtd;                             //证券交易在途数量    
	char  StkBcost[OX_STKBCOST_LENGTH];           //证券买入成本        
	char  StkBcostRlt[OX_STKBCOSTRLT_LENGTH];     //证券买入成本（实时）
	char  StkPlamt[OX_STKPLAMT_LENGTH];           //证券盈亏金额        
	char  StkPlamtRlt[OX_STKPLAMTRLT_LENGTH];     //证券盈亏金额（实时）
	char  MktVal[OX_MKTVA_LENGTH];                //市值                
	char  CostPrice[OX_COSTPRICE_LENGTH];         //成本价格            
	char  ProIncome[OX_PROINCOME_LENGTH];         //参考盈亏            
	char  StkCalMktvale[OX_STKCALMKTVALE_LENGTH]; //市值计算标识        
	int64_t StkQty;                                //当前拥股数          
	char  CurrentPrice[OX_CURRENTPRICE_LENGTH];   //最新价格            
	char  ProfitPrice[OX_PROFITPRICE_LENGTH];     //参考成本价          
	int64_t StkDiff;                               //可申赎数量          
	int64_t StkTrdUnfrz;                           //已申赎数量          
	char  Trdacct[OX_TRDACCT_LENGTH];             //交易账户            
	char  Income[OX_INCOME_LENGTH];               //盈亏                
	int64_t StkRemain;                             //余券可用数量        
	char  AveragePrice[OX_AVERAGEPRICE_LENGTH];   //买入均价  
    int64_t StkTrdEtfCreationCount;               //ETF申购数量
    int64_t StkTrdEtfRedemptionCount;             //ETF赎回数量
	int64_t StkSale;                               //卖出冻结数量
};

struct COXRspPositionExField
{

    int   IntOrg;                                 //内部机构            
    char  CustCode[OX_CUSTCODE_LENGTH];           //客户代码            
    char  Account[OX_ACCOUNT_LENGTH];             //资产账户            
    char  BoardId[OX_BOARDID_LENGTH];             //交易板块            
    char  Stkpbu[OX_STKPBU_LENGTH];               //交易单元            
    char  Trdacct[OX_TRDACCT_LENGTH];             //股东账号         
    char  Currency;                                //货币代码            
    char  Symbol[OX_SYMBOL_LENGTH];               //证券代码                
    char  StkCls;                                  //证券类别           

    int64_t StkAvl;                                //证券可用数量        
    int64_t StkQty;                                //当前拥股数          

    int64_t StkBln;                                //证券余额            
    
    int64_t StkTrdFrz;                             //证券交易冻结数量    
    int64_t StkTrdUfz;                             //证券交易解冻数量    
    int64_t StkTrdOtd;                             //证券交易在途数量    
    int64_t StkTrdBln;                             //证券交易扎差数量    
         
    int64_t StkDiff;                               //可申赎数量          
    int64_t StkTrdUnfrz;                           //已申赎数量          
                
};


struct COXRspFilledDetailField
{
    char      QueryPos[OX_QUERYPOS_LENGTH];        //定位串
    char      Account[OX_ACCOUNT_LENGTH];          //资产账户            
	char      Trdacct[OX_TRDACCT_LENGTH];          //交易账户
	int32_t   OrderDate;                            //委托日期
	int64_t   OrderNo;                              //委托编号
	char      OrderId[OX_ORDERID_LENGTH];          //合同序号 

	char      BoardId[OX_BOARDID_LENGTH];          //交易板块
	char      Symbol[OX_SYMBOL_LENGTH];            //证券代码
	int       StkBiz;                               //交易业务
	int       StkBizAction;                         //业务活动

	char      FilledType;                           //成交类型
	char      TradeSn[OX_TRADESN_LENGTH];          //成交编号
	int64_t   FilledQty;                            //成交数量
	char      FilledPrice[OX_FILLEDPRICE_LENGTH];  //成交价格
	char      FilledTime[OX_FILLEDTIME_LENGTH];    //成交时间

    int32_t   ErrId;			                    //错误ID
    char      ErrMessage[OX_ERRORINFO_LENGTH];	    //错误信息
    
    char      OrderRef[OX_ORDER_REF_LENGTH];        //自定义委托编号 2023-03-15 add 
};

struct COXRspCancelTicketField
{
	char     Account[OX_ACCOUNT_LENGTH];          //资产账户            
	char     BoardId[OX_BOARDID_LENGTH];
			 
    uint32_t OrderDate;
    int64_t  OrderNo;
	char     OrderState;  //未用
    char     ExeInfo[OX_EXEINFO_LENGTH];
	int      StkBiz;
	int      StkBizAction;
	char     Symbol[OX_SYMBOL_LENGTH];

};

struct COXRspBatchCancelTicketField
{
	char     Account[OX_ACCOUNT_LENGTH];          //资产账户            
	char     BoardId[OX_BOARDID_LENGTH];

	char     OrderId[OX_ORDERID_LENGTH];
	int32_t  OrderBsn; //委托批号
	int32_t  CancelRet; // 返回值 0：表示成功 -1：表示失败
	char     RetInfo[OX_RET_INFO_LENGTH];
};


struct COXOrderFilledField
{
	char     Account[OX_ACCOUNT_LENGTH];
	char     Trdacct[OX_TRDACCT_LENGTH];        
	char     Symbol[OX_SYMBOL_LENGTH];
	char     ExchangeId;
    char     BoardId[OX_BOARDID_LENGTH];
	
	int      StkBiz;
	int      StkBizAction;
	char     TradeSn[OX_TRADESN_LENGTH];
    int64_t  OrderNo;
    char     OrderRef[OX_ORDER_REF_LENGTH];
	
	int64_t  FilledQty;
	char     FilledPrice[OX_FILLEDPRICE_LENGTH];
    char     FilledAmt[OX_FILLEDAMT_LENGTH];
	int32_t  FilledDate;
	char     FilledTime[OX_FILLEDTIME_LENGTH];
    int32_t  ErrorId;
	char     RetMessage[OX_RETMESSAGE_LENGTH];

};

struct COXOrderTicket
{
	OXAccountType	AcctType;	
	char            Account[OX_ACCOUNT_LENGTH];

	char            Trdacct[OX_TRDACCT_LENGTH];
	char            BoardId[OX_BOARDID_LENGTH];
	int             StkBiz;
	int             StkBizAction;
	char            Symbol[OX_SYMBOL_LENGTH];

	char            OrderRef[OX_ORDER_REF_LENGTH];
	uint32_t        OrderQty;
	char            OrderPrice[OX_ORDERPRICE_LENGTH];

	int32_t         InsertDate;
    char            InsertTime[OX_ORDERTIME_LENGTH];  //委托时间 2023-03-15 add 
    int64_t         OrderNo;
	
	char            OrderState;
    int32_t         ErrorId;
	char            ExeInfo[OX_EXEINFO_LENGTH];
	int64_t         FilledQty;
	int64_t         CanceledQty;
	char            FilledAmt[OX_FILLEDAMT_LENGTH];
};


struct COXReqFuturePositionField
{
    OXAccountType	AcctType;			     //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)
    char Symbol[OX_SYMBOL_LENGTH];           //合约代码
};

struct COXReqOptionMarginRiskDegreeField
{
    OXAccountType	AcctType;			     //账户类型(必需)
    char Account[OX_ACCOUNT_LENGTH];		 //资金账号(必需)
    char Currency;                           //货币代码
};

struct COXRspCreditTargetStocksField
{
	char   QueryPos[OX_QUERYPOS_LENGTH];            //定位串        
	char   ExchangeId;                               //证券交易所    
	char   BoardId[OX_BOARDID_LENGTH];              //交易板块      
	char   Symbol[OX_SYMBOL_LENGTH];                //证券代码      
	char   StkName[OX_STKNAME_LENGTH];              //证券名称      
	char   FIMarginRatio[OX_CREDIT_DOUBLE_LENGTH];  //融资保证金比例  
	char   SLMarginRatio[OX_CREDIT_DOUBLE_LENGTH];  //融券保证金比例
	char   CurrEnableFI;                             //当日融资标志  
	char   CurrEnableSL;                             //当日融券标志  
    char   CreditFundCtl;                            //融资交易标志
    char   CreditStkCtl;                             //融资交易标志
};

struct COXRspCreditCollatalStocksField
{
	char   QueryPos[OX_QUERYPOS_LENGTH];        //定位串        
	char   ExchangeId;                           //证券交易所    
	char   BoardId[OX_BOARDID_LENGTH];          //交易板块      
	char   Symbol[OX_SYMBOL_LENGTH];            //证券代码      
	char   StkName[OX_STKNAME_LENGTH];          //证券名称      
	char   CollatRatio[OX_CREDIT_DOUBLE_LENGTH];//担保品折算率  
};

struct COXRspCreditBalanceDebtField
{
	char   CustCode[OX_CUSTCODE_LENGTH];                          //客户代码        
	char   Account[OX_ACCOUNT_LENGTH];		                       //资金账号 
	char   Currency;                                               //货币代码    

	char   FIRate[OX_STKNAME_LENGTH];                             //融资利率        
	char SLRate[OX_STKNAME_LENGTH];                               //融券利率        
	char FreeIntRate[OX_STKNAME_LENGTH];                          //罚息利率        
	char   CreditStatus[OX_STKNAME_LENGTH];                       //信用状态        
	char MarginRate[OX_STKNAME_LENGTH];                           //维持担保比例    
	char RealRate[OX_STKNAME_LENGTH];                             //实时担保比例    
	char TotalAssert[OX_STKNAME_LENGTH];                          //总资产          
	char TotalDebts[OX_STKNAME_LENGTH];                           //总负债          
	char MarginValue[OX_STKNAME_LENGTH];                          //保证金可用余额  
	char FundAvl[OX_STKNAME_LENGTH];                              //资金可用金额    
	char FundBln[OX_STKNAME_LENGTH];                              //资金余额        
	char SlAmt[OX_STKNAME_LENGTH];                                //融券卖出所得资金
	char GuaranteOut[OX_STKNAME_LENGTH];                          //可转出担保资产  
	char ColMktVal[OX_STKNAME_LENGTH];                            //担保证券市值    
	char FiAmt[OX_STKNAME_LENGTH];                                //融资本金        
	char TotalFiFee[OX_STKNAME_LENGTH];                           //融资息费        
	char FiTotalDebts[OX_STKNAME_LENGTH];                         //融资负债合计    
	char SlMktVal[OX_STKNAME_LENGTH];                             //应付融券市值    
	char TotalSlFee[OX_STKNAME_LENGTH];                           //融券息费        
	char SLTotalDebts[OX_STKNAME_LENGTH];                         //融券负债合计    
	char FICredit[OX_STKNAME_LENGTH];                             //融资授信额度    
	char FICreditAvl[OX_STKNAME_LENGTH];                          //融资可用额度    
	char FICreditFrz[OX_STKNAME_LENGTH];                          //融资额度冻结    
	char SLCredit[OX_STKNAME_LENGTH];                             //融券授信额度    
	char SLCreditAvl[OX_STKNAME_LENGTH];                          //融券可用额度    
	char SLCreditFrz[OX_STKNAME_LENGTH];                          //融券额度冻结    
	char Rights[OX_STKNAME_LENGTH];                               //红利权益        
	char RightsUncomer[OX_STKNAME_LENGTH];                        //红利权益（在途）
	int64_t  RightsQty;                                            //红股权益        
	int64_t  RightsQtyUncomer;                                     //红股权益（在途）  
	char TotalCredit[OX_STKNAME_LENGTH];                          //总额度          
	char TotalCreditAvl[OX_STKNAME_LENGTH];                       //总可用额度      

};

struct COXRspCreditContractField
{
	char    QueryPos[OX_QUERYPOS_LENGTH];                           //定位串
	char    CashNo[OX_CASHNO_LENGTH];                               //头寸编号
	int     TrdDate;                                                 //交易日期
	char    ContractType;                                            //合约类型
	char    Trdacct[OX_TRDACCT_LENGTH];                             //交易账户
	char    ExchangeId;                                              //交易市场
	char    BoardId[OX_BOARDID_LENGTH];                             //交易板块
	int     OpeningDate;                                             //开仓日期
	char    Symbol[OX_SYMBOL_LENGTH];                               //证券代码
	char    OrderId[OX_ORDERID_LENGTH];                             //合同序号
	char  FIDebtsAmt[OX_CREDIT_DOUBLE_LENGTH];                      //融资负债金额
	int64_t   SLDebtsQty;                                            //融券负债数量
	int64_t   RepaidQty;                                             //融券已还数量
	char  RepaidAmt[OX_CREDIT_DOUBLE_LENGTH];                       //融资已还金额
	char    ContractStatus;                                          //合约状态
	int     ContractExpireDate;                                      //合约到期日
	char  MarginRatio[OX_CREDIT_DOUBLE_LENGTH];                     //保证金比例
	char  MarginAmt[OX_CREDIT_DOUBLE_LENGTH];                       //占用保证金
	char  Rights[OX_CREDIT_DOUBLE_LENGTH];                          //未偿还权益金额
	int64_t   RightsQty;                                             //未偿还权益数量
	char  OverdueFee[OX_CREDIT_DOUBLE_LENGTH];                      //逾期未偿还息费
	int     LastRepayDate;                                           //最后偿还日期
	char    CustCode[OX_CUSTCODE_LENGTH];                           //客户代码
	char    Account[OX_ACCOUNT_LENGTH];                             //资金账号
	char    Currency;                                                //货币代码
	int     IntOrg;                                                  //内部机构
	char  OrderPrice[OX_CREDIT_DOUBLE_LENGTH];                      //委托价格
	int64_t   OrderQty;                                              //委托数量
	char  OrderAmt[OX_CREDIT_DOUBLE_LENGTH];                        //委托金额
	char  OrderFrzAmt[OX_CREDIT_DOUBLE_LENGTH];                     //委托冻结金额
	int64_t   WithdrawnQty;                                          //已撤单数量
	int64_t   MatchedQty;                                            //成交数量
	char  MatchedAmt[OX_CREDIT_DOUBLE_LENGTH];                      //成交金额
	char  RltSettAmt[OX_CREDIT_DOUBLE_LENGTH];                      //实时清算金额
	char  SLDebtsMktvalue[OX_CREDIT_DOUBLE_LENGTH];                 //融券负债市值
	int64_t   RltRepaidQty;                                          //融券实时归还数量
	char  RltRepaidAmt[OX_CREDIT_DOUBLE_LENGTH];                    //融资实时归还金额
	char  MatchedAmtRepay[OX_CREDIT_DOUBLE_LENGTH];                 //还成交金额
	int     CalIntDate;                                              //开始计息日期
	char  ContractInt[OX_CREDIT_DOUBLE_LENGTH];                     //合约利息
	char  ContractIntAccrual[OX_CREDIT_DOUBLE_LENGTH];              //利息积数
	char  OverRights[OX_CREDIT_DOUBLE_LENGTH];                      //逾期未偿还权益
	char  RightsRepay[OX_CREDIT_DOUBLE_LENGTH];                     //己偿还权益
	char  RightsRlt[OX_CREDIT_DOUBLE_LENGTH];                       //实时偿还权益
	char  OverRightsRlt[OX_CREDIT_DOUBLE_LENGTH];                   //实时偿还预期权益
	int64_t   OverRightsQty;                                         //逾期未偿还权益数量
	int64_t   RightsQtyRepay;                                        //已偿还权益数量
	int64_t   RightsQtyRlt;                                          //实时偿还权益数量
	int64_t   OverRightsQtyRlt;                                      //实时偿还逾期权益数量
	char  ContractFee[OX_CREDIT_DOUBLE_LENGTH];                     //融资融券息费
	char  FeeRepay[OX_CREDIT_DOUBLE_LENGTH];                        //己偿还息费
	char  FeeRlt[OX_CREDIT_DOUBLE_LENGTH];                          //实时偿还息费
	char  OverDuefeeRlt[OX_CREDIT_DOUBLE_LENGTH];                   //实时偿还逾期息费
	char  PuniDebts[OX_CREDIT_DOUBLE_LENGTH];                       //逾期本金罚息
	char  PuniDebtsRepay[OX_CREDIT_DOUBLE_LENGTH];                  //本金罚息偿还
	char  PuniDebtsRlt[OX_CREDIT_DOUBLE_LENGTH];                    //实时逾期本金罚息
	char  PuniFee[OX_CREDIT_DOUBLE_LENGTH];                         //利息产生的罚息
	char  PuniFeeRepay[OX_CREDIT_DOUBLE_LENGTH];                    //己偿还罚息
	char  PuniFeeRlt[OX_CREDIT_DOUBLE_LENGTH];                      //实时逾期息费罚息
	char  PuniRights[OX_CREDIT_DOUBLE_LENGTH];                      //逾期权益罚息
	char  PuniRightsRepay[OX_CREDIT_DOUBLE_LENGTH];                 //权益罚息偿还
	char  PuniRightsRlt[OX_CREDIT_DOUBLE_LENGTH];                   //实时逾期权益罚息
	int     ClosingDate;                                             //合约了结日期
	char  ClosingPrice[OX_CREDIT_DOUBLE_LENGTH];                    //合约了结价格
	int     OpOrg;                                                   //操作机构
	char    ContractCls;                                             //合约类别
	char  ProIncome[OX_CREDIT_DOUBLE_LENGTH];                       //参考盈亏
	char  PledgeCuacct[OX_CREDIT_DOUBLE_LENGTH];                    //抵押资产
	char  FIRepayAmt[OX_CREDIT_DOUBLE_LENGTH];                      //融资偿还
	int64_t   SLRepayQty;                                            //融券偿还
};


struct COXRspCreditSecuLendQuotaField
{
	char     CashNo[OX_CASHNO_LENGTH];    //头寸编号
	char     BoardId[OX_BOARDID_LENGTH];  //交易板块      
	char     Symbol[OX_SYMBOL_LENGTH];    //证券代码         
	int64_t  AssetBln;                     //头寸总额度  
	int64_t  AssetAvl;                     //头寸可用额度  

};


struct COXRspCreditReimbursibleBalField
{
	char   Account[OX_ACCOUNT_LENGTH];  //资金账号  

	char FITotalDebts[OX_CREDIT_DOUBLE_LENGTH];	//融资负债合计
	char TotalSLFee[OX_CREDIT_DOUBLE_LENGTH];      //融券息费
							             
	char CanRepayAmt[OX_CREDIT_DOUBLE_LENGTH];    //可偿还金额
	char Mayrepay[OX_CREDIT_DOUBLE_LENGTH];       //偿还可用金额
};

struct COXRspCreditSLContractSummaryField
{
	char   Account[OX_ACCOUNT_LENGTH];                          //资金账号  
	char   BoardId[OX_BOARDID_LENGTH];                          //交易板块                    
	char   Symbol[OX_SYMBOL_LENGTH];                            //证券代码            

	int64_t  OpenQty;                                            //开仓数量
	int64_t  RepayQty;                                           //归还数量
	char SettAmt[OX_CREDIT_DOUBLE_LENGTH];                      //清算金额
	char RepayAmt[OX_CREDIT_DOUBLE_LENGTH];                     //归还金额
	int64_t  OrderQty;                                           //委托数量
	int64_t  RightsQty;                                          //未偿还权益数量
	int64_t  OverRightsQty;                                      //逾期未偿还权益数量
	char CollatRatio[OX_CREDIT_DOUBLE_LENGTH];                  //担保品折算率
	char SlMarginRatio[OX_CREDIT_DOUBLE_LENGTH];                //融券保证金比例
	int64_t  RltOpenQty;                                         //实时开仓数量
	char RltSettAmt[OX_CREDIT_DOUBLE_LENGTH];                   //实时清算金额
};

struct COXRspStockOptionBalanceField
{
    char   CustCode[OX_CUSTCODE_LENGTH];               //客户代码
    char   Account[OX_ACCOUNT_LENGTH];                 //资金账号 
	char   Currency;                                    //货币代码
	int    IntOrg;                                      //内部机构
	char  AccountWorth[OX_CREDIT_DOUBLE_LENGTH];       //资产总值
	char  FundValue[OX_CREDIT_DOUBLE_LENGTH];          //资金资产
	char  StkValue[OX_CREDIT_DOUBLE_LENGTH];           //市值
	char  FundPrebln[OX_CREDIT_DOUBLE_LENGTH];         //资金昨日余额
	char  FundBln[OX_CREDIT_DOUBLE_LENGTH];            //资金余额
	char  FundAvl[OX_CREDIT_DOUBLE_LENGTH];            //资金可用
	char  FundFrz[OX_CREDIT_DOUBLE_LENGTH];            //资金冻结金额
	char  FundUfz[OX_CREDIT_DOUBLE_LENGTH];            //资金解冻金额
	char  FundTrdFrz[OX_CREDIT_DOUBLE_LENGTH];         //资金交易冻结金额
	char  FundTrdUfz[OX_CREDIT_DOUBLE_LENGTH];         //资金交易解冻金额
	char  FundTrdOtd[OX_CREDIT_DOUBLE_LENGTH];         //资金交易在途金额
	char  FundTrdBln[OX_CREDIT_DOUBLE_LENGTH];         //资金交易轧差金额
	char   FundStatus;         //资金状态
	char  MarginUsed[OX_CREDIT_DOUBLE_LENGTH];         //占用保证金
	char  MarginInclRlt[OX_CREDIT_DOUBLE_LENGTH];      //已占用保证金（含未成交）
	char  FundExeMargin[OX_CREDIT_DOUBLE_LENGTH];      //行权锁定保证金
	char  FundExeFrz[OX_CREDIT_DOUBLE_LENGTH];         //行权资金冻结金额
	char  FundFeeFrz[OX_CREDIT_DOUBLE_LENGTH];         //资金费用冻结金额
	char  Paylater[OX_CREDIT_DOUBLE_LENGTH];           //垫付资金
	char  PreadvaPay[OX_CREDIT_DOUBLE_LENGTH];         //预计垫资金额
	char  ExpPenInt[OX_CREDIT_DOUBLE_LENGTH];          //预计负债利息
	char  FundDraw[OX_CREDIT_DOUBLE_LENGTH];           //资金可取金额
	char  FundAvlRlt[OX_CREDIT_DOUBLE_LENGTH];         //资金动态可用
	char  MarginInclDyn[OX_CREDIT_DOUBLE_LENGTH];      //动态占用保证金(含未成交)
	char  DailyInAmt[OX_CREDIT_DOUBLE_LENGTH];         //当日入金
	char  DailyOutAmt[OX_CREDIT_DOUBLE_LENGTH];        //当日出金
	char  FundRealAvl[OX_CREDIT_DOUBLE_LENGTH];        //资金实际可用
};

struct COXRspStockOptionPositionField
{
	char  CustCode[OX_CUSTCODE_LENGTH];         //客户代码
	char  Account[OX_ACCOUNT_LENGTH];           //资金账号  	
	int   IntOrg;                                //内部机构
	char  ExchangeId;                            //交易市场            
	char  BoardId[OX_BOARDID_LENGTH];           //交易板块
										         
	char  Stkpbu[OX_STKPBU_LENGTH];             //交易单元	
	char  Trdacct[OX_TRDACCT_LENGTH];           //交易账户
	char  SubacctCode[OX_SUBACCTCODE_LENGTH];   //证券账户子编码
	char  OptTrdacct[OX_OPTTRDACCT_LENGTH];     //期权合约账户
	char  Currency;                              //货币代码
	char  OptNum[OX_OPTNUM_LENGTH];             //合约编码
	char  OptCode[OX_OPTCODE_LENGTH];           //合约代码
	char  OptName[OX_OPTNAME_LENGTH];           //合约简称	
	char  OptType;                               //合约类型
	char  OptSide;                               //持仓方向	
	char  OptCvdFlag;                            //备兑标志
							      
	int64_t OptPrebln;                           //合约昨日余额	
	int64_t OptBln;                              //合约余额
	int64_t OptAvl;                              //合约可用数量	
	int64_t OptFrz;                              //合约冻结数量
	int64_t OptUfz;                              //合约解冻数量	
	int64_t OptTrdFrz;                           //合约交易冻结数量
	int64_t OptTrdUfz;                           //合约交易解冻数量	
	int64_t OptTrdOtd;                           //合约交易在途数量
	int64_t OptTrdBln;                           //合约交易轧差数量	
	int64_t OptClrFrz;                           //合约清算冻结数量
	int64_t OptClrUfz;                           //合约清算解冻数量	
	int64_t OptClrOtd;                           //合约清算在途数量

    char OptBcost[OX_OPTBCOST_LENGTH];            //合约买入成本	
    char OptBcostRlt[OX_OPTBCOSTRLT_LENGTH];      //合约买入成本（实时）
    char OptPlamt[OX_OPTPLAMT_LENGTH];            //合约盈亏金额	
    char OptPlamtRlt[OX_OPTPLAMTRLT_LENGTH];      //合约盈亏金额（实时）
    char OptMktVal[OX_OPTMKTVAL_LENGTH];          //合约市值	
    char OptPremium[OX_OPTPREMIUM_LENGTH];        //权利金
    char OptMargin[OX_OPTMARGIN_LENGTH];          //保证金	
    char OptClsProfit[OX_OPTCLSPROFIT_LENGTH];    //当日平仓盈亏
    char SumClsProfit[OX_SUMCLSPROFIT_LENGTH];    //累计平仓盈亏	
    char OptFloatProfit[OX_OPTFLOATPROFIT_LENGTH];//浮动盈亏
    char TotalProfit[OX_TOTALPROFIT_LENGTH];      //总盈亏	

    int64_t OptCvdAsset;                           //备兑股份数量	
	int64_t OptRealPosi;                           //合约实际持仓
	int64_t OptClsUnmatched;                       //合约平仓挂单数量
	int64_t OptDailyOpenRlt;                       //当日累计开仓数量
	char OptUndlCode[OX_OPTUNDLCODE_LENGTH];       //标的证券代码
    int64_t CombedQty;                             //参与组合的期权合约持仓数量
							      
};


struct COXRspOptionMarginRiskField
{
    char    CustCode[OX_CUSTCODE_LENGTH];               //客户代码
    char    Account[OX_ACCOUNT_LENGTH];                 //资金账号 
    char    Currency;                                   //货币代码
    int     IntOrg;                                     //内部机构
    double  FundBln;                                    //资金余额
    double  DueAddAmt;                                  //应补资金
    double  FundAvl;                                    //资金可用
    double  FundAvlReal;                                //资金实时可用金额
    double  ExchangeFundAvl;                            //可用金额(交易所)
    double  ExchangeFundAvlRlt;                         //实时可用金额(交易所)
    double  RiskRatio;                                  //风险率
    double  RiskRatioRlt;                               //实时风险率
    double  ExchangeRiskRation;                         //风险率(交易所)
    double  ExchangeRiskRatioRlt;                       //实时风险率(交易所)
    double  MarginUsed;                                 //占用保证金
    double  MarginUsedRlt;                              //实时占用保证金
    double  ExchangeMarginUsed;                         //占用保证金(交易所)
    double  ExchangeMarginUsedRlt;                      //实时占用保证金(交易所)
    double  HedgedMargin;                               //对冲后保证金
    double  HedgedMarginRlt;                            //对冲后实时保证金
    double  ExchangeHedgedMargin;                       //对冲后保证金(交易所)
    double  ExchangeHedgedMarginRlt;                    //对冲后实时保证金(交易所)
};

struct COXRspETFInfoField
{
    char BoardId[OX_BOARDID_LENGTH];		    //交易板块
    uint64_t TrdDate;						    //交易日期
    uint64_t PreTrdDate;						//前交易日
    char ETFCode[OX_SYMBOL_LENGTH];             //ETF代码
    char ETFPublish;                            //ETF发布标志 '0':不发布，'1':发布
    char ETFCRFlag;                             //ETF申赎标志 '0':不允许申购赎回，'1'允许申购赎回，'2'允许申购不允许赎回，'3'允许赎回不允许申购
    uint64_t ETFCRUnit;                         //ETF申购赎回单位
    char ETFCashRatio[OX_ETFCASHRATIO_LENGTH];  //现金替代比例
    uint64_t ETFStkNum;                         //ETF股票篮股票数
    char ETFEstmCash[OX_ETFESTMCASH_LENGTH];    //ETF股票篮现金差
    char ETFCashComp[OX_ETFCASHCOMP_LENGTH];    //基准单位现金
    char ETFNavPerCU[OX_ETFNAVPERCU_LENGTH];    //基准单位净值
    char ETFNav[OX_ETFNAV_LENGTH];              //ETF单位净值
    char ETFType;		                        //ETF类型 '1'本市场ETF,'2'跨境ETF,'3'跨市场ETF,'4'货币ETF,'5'黄金ETF,'6'单市场实物债券ETF,'7'现金债券ETF,'8'商品期货ETF
    uint64_t CreationLimit;                     //申购上限
    uint64_t RedemptionLimit;                   //赎回上限
    uint64_t CLimitPerUser;                     //单账户申购上限
    uint64_t RLimitPerUser;                     //单账户赎回上限
    char ETFMode;                               // ETF模式 
    char RiskLevel;                             //风险级别 '0'正常，'1'高风险，'2'暂停上市
    char QSETFCrFlag;                           //券商申购赎回标志
    char ETFUndlCode[OX_SYMBOL_LENGTH];         //ETF二级市场代码
};


struct COXRspETFComponentInfoField
{
    char BoardId[OX_BOARDID_LENGTH];		                              //交易板块
    char ETFCode[OX_SYMBOL_LENGTH];                                       //ETF代码
    char Symbol[OX_SYMBOL_LENGTH];                                        //证券代码 
    char StkName[OX_STKNAME_LENGTH];                                      //证券名称 
    uint64_t StkQty;                                                      //证券数量
    char ETFInsteadFlag;                                                  //现金替代标志
    char ETFOverflowRate[OX_ETFOVERFLOWRATE_LENGTH];                      //溢价比例
    char RedemptionInsteadAmt[OX_REDEMPTIONINSTEADAMT_LENGTH];            //赎回现金替代金额
    char CompentSTKEX;                                                    //成分股市场代码
    char CreationInsteadAmt[OX_CREATIONINSTEADAMT_LENGTH];                //申购现金替代金额
    char ETFMode;							                              //ETF模式
    int32_t UpdDate;						                              //更新日期
    char ETFDiscountRate[OX_ETFDISCOUNTRATE_LENGTH];                      //折价比例
};


struct COXRspFutureBalanceField
{

    char    Account[OX_ACCOUNT_LENGTH];              //资金账号
    int     TradingDay;                              //交易日期
    double  DynamicRight;	                         //动态权益
    double  FundPreBalance;                          //资金昨日余额
    double  Avaiable;                                //资金可用金额

    double	Commission;	                             //手续费
    double	CloseProfit;	                         //平仓盈亏
    double	PositionProfit;	                         //持仓盈亏

    double	UsedMargin;                             //保证金占用

};


struct COXRspFuturePositionField
{
    char  Account[OX_ACCOUNT_LENGTH];            //资金账号  	
    char  ExchangeId;                            //交易市场            
    char  Symbol[OX_SYMBOL_LENGTH];              //合约代码
 
    char  Direction;                             //持仓方向	
    char  HedgeFlag;                             //投保标记

    int64_t YdPosition;                          //上日持仓
    int64_t TodayPosition;                       //上日持仓
    int64_t Qty;                                 //持仓数量
    int64_t AvlQty;                              //持仓可平数量

    double  OpenPrice;                           //开仓均价
    double	CloseProfit;	                     //平仓盈亏
    double	PositionProfit;	                     //持仓盈亏
    double	PositionCost;	                     //持仓成本
   
    int64_t OpenVolume;                          //开仓量
    int64_t CloseVolume;                         //平仓量

    double  OpenAmount;                          //开仓金额
    double  CloseAmount;                         //平仓金额

    double	UsedMargin;                          //保证金占用
    double	Commission;	                         //手续费

};

#pragma pack()


#endif // !_OX_TRADE_API_STRUCT_H_

