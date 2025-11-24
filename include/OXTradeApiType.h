#ifndef _OX_TRADE_API_TYPE_H_
#define _OX_TRADE_API_TYPE_H_

enum OXAccountType
{
	OX_ACCOUNT_STOCK	= '0',				//现货
	OX_ACCOUNT_OPTION	= '1',				//期权
	OX_ACCOUNT_FUTURE   = '2',				//期货
	OX_ACCOUNT_CREDIT   = '3'			    //信用交易
};


enum OXOrderState
{
	ORDER_STATE_NOT_REPORT          = '0',         //未报
	ORDER_STATE_REPORTING           = '1',         //正报 
	ORDER_STATE_REPORTED            = '2',         //已报
	ORDER_STATE_CANCELING           = '3',         //已报待撤
	ORDER_STATE_PARTIAL_CANCELING   = '4',         //部成待撤
	ORDER_STATE_PARTIAL_CANCELED    = '5',         //部成部撤
	ORDER_STATE_CANCELED            = '6',         //已撤
	ORDER_STATE_PARTIAL_FILLED      = '7',         //部分成交
	ORDER_STATE_FILLED              = '8',         //已成交
	ORDER_STATE_REJECTED            = '9',         //废单
	ORDER_STATE_REPORT_WAITING      = 'A',         //待报 写入报盘队列未成功
	ORDER_STATE_REPORT_ACK          = 'B',         //报盘确认 已经成功写入接口库,报盘机回写确认

    //以下状态，只适用于条件单等特殊订单
    ORDER_STATE_NEED_SEND           = 'N',	       // 需报（OCO/BRK组合，委托1触发，委托0撤单已报，委托1未报前的中间状态）                                           
    ORDER_STATE_DIVIDEND_CANCELED   = 'D',         //除权派息终止
    ORDER_STATE_EXPIRED             = 'E',         //到期终止
    ORDER_STATE_TRIGGER_AGAIN       = 'T'          //当前交易日已触发，下一交易日可再次触发。

};

#endif