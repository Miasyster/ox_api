"""
核心 API 模块

封装 GuosenOXTradeApi 类，提供 Pythonic 的 API 接口。
"""

import sys
import threading
import time
from typing import Optional
from ctypes import c_int, c_char_p, POINTER, byref, cast, c_void_p

from .dll_loader import DLLoader
from .spi import OXTradeSpi
from .types import AccountType
from .exceptions import OXDllError, OXConnectionError, OXLoginError
from .structs import COXReqLogonField, COXReqOrderTicketField, COXReqCancelTicketField, COXReqBatchOrderTicketField, COXOrderItem
from .exceptions import OXDllError, OXConnectionError, OXLoginError, OXOrderError


class _OXTradeSpiWrapper(OXTradeSpi):
    """SPI 包装类，用于处理登录回调并转发到用户 SPI"""
    
    def __init__(self, user_spi: OXTradeSpi, api: 'OXTradeApi'):
        """初始化包装类
        
        Args:
            user_spi: 用户提供的 SPI 实例
            api: API 实例引用
        """
        super().__init__()
        self.user_spi = user_spi
        self.api = api
    
    def on_connected(self) -> int:
        """连接建立回调"""
        return self.user_spi.on_connected()
    
    def on_disconnected(self) -> int:
        """连接断开回调"""
        return self.user_spi.on_disconnected()
    
    def on_rsp_logon(self, request: int, error: Optional[dict], 
                     is_last: bool, field: Optional[dict]) -> None:
        """登录响应回调"""
        # 先调用用户 SPI
        self.user_spi.on_rsp_logon(request, error, is_last, field)
        
        # 然后处理登录响应（更新登录状态）
        self.api._handle_login_response(request, error, field)
    
    def on_rsp_trade_accounts(self, request: int, error: Optional[dict], 
                              is_last: bool, field: Optional[dict]) -> None:
        """交易账户响应回调"""
        self.user_spi.on_rsp_trade_accounts(request, error, is_last, field)
    
    def on_rtn_order(self, field: Optional[dict]) -> None:
        """委托回报回调"""
        self.user_spi.on_rtn_order(field)
    
    def on_rtn_order_filled(self, field: Optional[dict]) -> None:
        """成交回报回调"""
        self.user_spi.on_rtn_order_filled(field)
    
    def on_rsp_cancel_ticket(self, request: int, error: Optional[dict], 
                             field: Optional[dict]) -> None:
        """撤单响应回调"""
        self.user_spi.on_rsp_cancel_ticket(request, error, field)
    
    def on_rsp_batch_order(self, request: int, error: Optional[dict], 
                           field: Optional[dict]) -> None:
        """批量下单响应回调"""
        self.user_spi.on_rsp_batch_order(request, error, field)


class OXTradeApi:
    """OX 交易 API 主类"""
    
    def __init__(self, config_path: Optional[str] = None, dll_path: Optional[str] = None):
        """初始化 API 实例
        
        Args:
            config_path: 配置文件路径（可选）
            dll_path: DLL 文件路径（可选，自动查找）
        """
        self.dll_loader = DLLoader(dll_path)
        self.api_ptr = None
        self.dll_path = dll_path
        self.config_path = config_path
        self.spi: Optional[OXTradeSpi] = None
        self._initialized = False
        self._logged_in = False
        self._login_event = threading.Event()
        self._request_id = 0
        self._account = ''
        self._acct_type = AccountType.STOCK
    
    def init(self, err_msg: Optional[list] = None) -> int:
        """初始化 API
        
        Args:
            err_msg: 错误消息列表（可选），如果提供，初始化失败时会填充错误消息
        
        Returns:
            返回码：0 表示成功，非 0 表示失败
        
        Raises:
            OXDllError: 如果 DLL 加载失败
            OXConnectionError: 如果初始化失败
        """
        try:
            # 加载 DLL
            self.dll_loader.load()
            
            # 创建 API 实例
            self.api_ptr = self.dll_loader.create_api()
            
            if self.api_ptr is None or self.api_ptr == 0:
                error_msg = "Failed to create API instance"
                if err_msg is not None:
                    err_msg.append(error_msg)
                raise OXConnectionError(error_msg)
            
            # 注册 SPI（如果已设置）
            if self.spi is not None:
                self._register_spi_internal()
            
            # 调用 Init 虚函数
            # 注意：这里需要通过虚函数表调用 Init
            # 对于测试环境，我们暂时不实际调用 DLL
            init_result = self._call_init_virtual(err_msg)
            
            if init_result == 0:
                self._initialized = True
            else:
                error_msg = f"Init failed with return code: {init_result}"
                if err_msg is not None and err_msg:
                    error_msg = err_msg[0] if err_msg else error_msg
                raise OXConnectionError(error_msg)
            
            return init_result
            
        except OXDllError:
            raise
        except Exception as e:
            raise OXConnectionError(f"API initialization failed: {e}") from e
    
    def stop(self) -> None:
        """停止 API"""
        if self._initialized and self.api_ptr:
            # 调用 Stop 虚函数
            self._call_stop_virtual()
            self._initialized = False
        
        if self.api_ptr:
            self.dll_loader.release_api(self.api_ptr)
            self.api_ptr = None
        
        self._logged_in = False
        self._login_event.clear()
    
    def register_spi(self, spi: OXTradeSpi) -> None:
        """注册回调接口
        
        Args:
            spi: 回调接口实例
        """
        # 包装 SPI 以处理登录回调
        if not isinstance(spi, _OXTradeSpiWrapper):
            spi = _OXTradeSpiWrapper(spi, self)
        
        self.spi = spi
        
        # 如果已经初始化，立即注册
        if self._initialized and self.api_ptr:
            self._register_spi_internal()
    
    def _register_spi_internal(self) -> None:
        """内部方法：注册 SPI 到 DLL
        
        注意：由于 C++ 虚函数调用的复杂性，这里先预留接口。
        实际实现可能需要 C 包装层或通过虚函数表调用。
        """
        # TODO: 实现 RegisterSpi 虚函数调用
        # 对于测试环境，我们只保存 SPI 引用
        pass
    
    def login(self, account: str, password: str, 
              account_type: AccountType = AccountType.STOCK,
              timeout: float = 30.0) -> bool:
        """用户登录
        
        Args:
            account: 资金账号
            password: 密码
            account_type: 账户类型
            timeout: 登录超时时间（秒），默认 30 秒
        
        Returns:
            是否登录成功
        
        Raises:
            OXConnectionError: 如果 API 未初始化
            OXLoginError: 如果登录失败
        """
        if not self._initialized:
            raise OXConnectionError("API not initialized, call init() first")
        
        if not self.spi:
            raise OXLoginError("SPI not registered, call register_spi() first")
        
        # 重置登录状态
        self._logged_in = False
        self._login_event.clear()
        
        # 创建登录请求结构体
        req = COXReqLogonField.from_dict({
            'AcctType': account_type.value,
            'Account': account,
            'Password': password,
        })
        
        # 调用 OnReqLogon 虚函数
        request_id = self._get_next_request_id()
        result = self._call_logon_virtual(request_id, req)
        
        if result != 0:
            raise OXLoginError(f"Login request failed with return code: {result}")
        
        # 等待登录回调
        if self._login_event.wait(timeout):
            return self._logged_in
        else:
            raise OXLoginError("Login timeout")
    
    def _get_next_request_id(self) -> int:
        """获取下一个请求 ID"""
        self._request_id += 1
        return self._request_id
    
    def _call_init_virtual(self, err_msg: Optional[list] = None) -> int:
        """调用 Init 虚函数
        
        注意：这是一个占位实现。实际需要通过虚函数表调用。
        对于测试环境，返回 0（成功）。
        """
        # TODO: 实现虚函数调用
        # 在实际环境中，需要通过虚函数表调用 Init
        # 这里先返回成功，供测试使用
        return 0
    
    def _call_stop_virtual(self) -> None:
        """调用 Stop 虚函数
        
        注意：这是一个占位实现。实际需要通过虚函数表调用。
        """
        # TODO: 实现虚函数调用
        pass
    
    def _call_logon_virtual(self, request_id: int, req: COXReqLogonField) -> int:
        """调用 OnReqLogon 虚函数
        
        注意：这是一个占位实现。实际需要通过虚函数表调用。
        对于测试环境，模拟登录请求并触发回调。
        """
        # TODO: 实现虚函数调用
        # 在实际环境中，需要通过虚函数表调用 OnReqLogon
        # 这里先模拟触发回调，供测试使用
        if self.spi:
            # 模拟登录成功回调
            threading.Thread(target=self._simulate_login_callback, args=(request_id,), daemon=True).start()
        return 0
    
    def _simulate_login_callback(self, request_id: int) -> None:
        """模拟登录回调（仅用于测试）"""
        if self.spi:
            # 模拟延迟
            time.sleep(0.1)
            # 创建成功响应
            from .structs import CRspErrorField, COXRspLogonField
            from .spi import convert_error_field, convert_rsp_field
            
            error = CRspErrorField()
            error.ErrorId = 0
            
            field = COXRspLogonField()
            field.IntOrg = 0
            field.AcctType = ord('0')
            # 设置 Account 字段
            from ctypes import memmove, addressof
            from .utils import encode_str
            from .constants import OX_ACCOUNT_LENGTH
            account_bytes = encode_str('110060035050')[:OX_ACCOUNT_LENGTH].ljust(OX_ACCOUNT_LENGTH, b'\x00')
            memmove(addressof(field) + 4 + 24, account_bytes, OX_ACCOUNT_LENGTH)  # IntOrg(4) + CustCode(24)
            
            error_dict = convert_error_field(error)
            field_dict = convert_rsp_field(field)
            
            # 调用 SPI 回调（包装类会处理登录状态更新）
            self.spi.on_rsp_logon(request_id, error_dict, True, field_dict)
    
    def _handle_login_response(self, request_id: int, error: Optional[dict], field: Optional[dict]) -> None:
        """处理登录响应回调"""
        if error and error.get('ErrorId', 0) != 0:
            # 登录失败
            self._logged_in = False
        else:
            # 登录成功
            self._logged_in = True
            # 保存账户信息供后续使用
            if field:
                self._account = field.get('Account', '')
                acct_type_str = field.get('AcctType', '0')
                if acct_type_str:
                    from .types import AccountType
                    try:
                        self._acct_type = AccountType.from_char(acct_type_str)
                    except:
                        self._acct_type = AccountType.STOCK
        
        self._login_event.set()
    
    def is_initialized(self) -> bool:
        """检查 API 是否已初始化
        
        Returns:
            如果已初始化返回 True，否则返回 False
        """
        return self._initialized
    
    def is_logged_in(self) -> bool:
        """检查是否已登录
        
        Returns:
            如果已登录返回 True，否则返回 False
        """
        return self._logged_in
    
    def __enter__(self):
        """上下文管理器入口"""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
    
    def order(self, trdacct: str, board_id: str, symbol: str, 
              price: float, quantity: int,
              stk_biz: int = 100, stk_biz_action: int = 100,
              order_ref: str = '', trd_code_cls: str = '',
              trd_ex_info: str = '') -> int:
        """下单
        
        Args:
            trdacct: 股东账号
            board_id: 交易板块（如 "10" 表示上海，"00" 表示深圳）
            symbol: 证券代码
            price: 委托价格
            quantity: 委托数量
            stk_biz: 证券业务（默认 100 表示买入）
            stk_biz_action: 证券业务指令（默认 100 表示限价单）
            order_ref: 客户委托信息（可选）
            trd_code_cls: 交易代码分类（可选）
            trd_ex_info: 委托扩展信息（可选）
        
        Returns:
            请求编号，如果失败返回 -1
        
        Raises:
            OXConnectionError: 如果 API 未初始化或未登录
            OXOrderError: 如果下单请求失败
        """
        if not self._initialized:
            raise OXConnectionError("API not initialized, call init() first")
        
        if not self._logged_in:
            raise OXConnectionError("Not logged in, call login() first")
        
        if not self.spi:
            raise OXOrderError("SPI not registered, call register_spi() first")
        
        # 获取账户信息（从登录响应中获取，如果没有则使用默认值）
        # 在实际使用中，账户信息应该从登录响应中获取
        account = getattr(self, '_account', '')
        if not account:
            raise OXOrderError("Account not available. Please login first and ensure login response contains account information.")
        acct_type = getattr(self, '_acct_type', AccountType.STOCK)
        
        # 创建下单请求结构体
        req_dict = {
            'AcctType': acct_type.value if hasattr(acct_type, 'value') else acct_type,
            'Account': account,
            'Trdacct': trdacct,
            'BoardId': board_id,
            'StkBiz': stk_biz,
            'StkBizAction': stk_biz_action,
            'Symbol': symbol,
            'OrderQty': quantity,
            'OrderPrice': price,
            'OrderRef': order_ref,
            'TrdCodeCls': trd_code_cls,
            'TrdExInfo': trd_ex_info,
        }
        
        req = COXReqOrderTicketField.from_dict(req_dict)
        
        # 调用 OnReqOrderTicket 虚函数
        request_id = self._get_next_request_id()
        result = self._call_order_virtual(request_id, req)
        
        if result != 0:
            raise OXOrderError(f"Order request failed with return code: {result}")
        
        return request_id
    
    def _call_order_virtual(self, request_id: int, req: COXReqOrderTicketField) -> int:
        """调用 OnReqOrderTicket 虚函数
        
        注意：这是一个占位实现。实际需要通过虚函数表调用。
        对于测试环境，模拟下单请求并触发回调。
        """
        # TODO: 实现虚函数调用
        # 在实际环境中，需要通过虚函数表调用 OnReqOrderTicket
        # 这里先模拟触发回调，供测试使用
        if self.spi:
            # 模拟委托回报回调
            threading.Thread(target=self._simulate_order_callback, args=(request_id, req,), daemon=True).start()
        return 0
    
    def _simulate_order_callback(self, request_id: int, req: COXReqOrderTicketField) -> None:
        """模拟委托回报回调（仅用于测试）"""
        if self.spi:
            # 模拟延迟
            time.sleep(0.1)
            # 创建委托回报字典（简化实现，直接使用字典）
            from .utils import decode_str
            
            req_dict = req.to_dict()
            order_ticket_dict = {
                'AcctType': req_dict['AcctType'],
                'Account': req_dict['Account'],
                'Trdacct': req_dict['Trdacct'],
                'BoardId': req_dict['BoardId'],
                'StkBiz': req_dict['StkBiz'],
                'StkBizAction': req_dict['StkBizAction'],
                'Symbol': req_dict['Symbol'],
                'OrderRef': req_dict['OrderRef'],
                'OrderQty': req_dict['OrderQty'],
                'OrderPrice': req_dict['OrderPrice'],
                'OrderNo': 123456789012345,
                'OrderState': '0',  # 正常状态
                'FilledQty': 0,
                'CanceledQty': 0,
                'InsertDate': 20240101,
                'InsertTime': '',
                'ErrorId': 0,
                'ExeInfo': '',
                'FilledAmt': '0.00',
            }
            
            # 调用 SPI 回调
            self.spi.on_rtn_order(order_ticket_dict)
    
    def cancel(self, board_id: str, order_no: int, order_date: Optional[int] = None) -> int:
        """撤单
        
        Args:
            board_id: 交易板块（如 "10" 表示上海，"00" 表示深圳）
            order_no: 委托号
            order_date: 委托日期（可选，如果不提供则使用当前日期）
        
        Returns:
            请求编号，如果失败返回 -1
        
        Raises:
            OXConnectionError: 如果 API 未初始化或未登录
            OXOrderError: 如果撤单请求失败
        """
        if not self._initialized:
            raise OXConnectionError("API not initialized, call init() first")
        
        if not self._logged_in:
            raise OXConnectionError("Not logged in, call login() first")
        
        if not self.spi:
            raise OXOrderError("SPI not registered, call register_spi() first")
        
        # 获取账户信息
        account = getattr(self, '_account', '')
        if not account:
            raise OXOrderError("Account not available. Please login first and ensure login response contains account information.")
        acct_type = getattr(self, '_acct_type', AccountType.STOCK)
        
        # 如果未提供委托日期，使用当前日期（格式：YYYYMMDD）
        if order_date is None:
            from datetime import date
            today = date.today()
            order_date = today.year * 10000 + today.month * 100 + today.day
        
        # 创建撤单请求结构体
        req_dict = {
            'AcctType': acct_type.value if hasattr(acct_type, 'value') else acct_type,
            'Account': account,
            'BoardId': board_id,
            'OrderDate': order_date,
            'OrderNo': order_no,
        }
        
        req = COXReqCancelTicketField.from_dict(req_dict)
        
        # 调用 OnReqCancelTicket 虚函数
        request_id = self._get_next_request_id()
        result = self._call_cancel_virtual(request_id, req)
        
        if result != 0:
            raise OXOrderError(f"Cancel request failed with return code: {result}")
        
        return request_id
    
    def _call_cancel_virtual(self, request_id: int, req: COXReqCancelTicketField) -> int:
        """调用 OnReqCancelTicket 虚函数
        
        注意：这是一个占位实现。实际需要通过虚函数表调用。
        对于测试环境，模拟撤单请求并触发回调。
        """
        # TODO: 实现虚函数调用
        # 在实际环境中，需要通过虚函数表调用 OnReqCancelTicket
        # 这里先模拟触发回调，供测试使用
        if self.spi:
            # 模拟撤单响应回调
            threading.Thread(target=self._simulate_cancel_callback, args=(request_id, req,), daemon=True).start()
        return 0
    
    def _simulate_cancel_callback(self, request_id: int, req: COXReqCancelTicketField) -> None:
        """模拟撤单响应回调（仅用于测试）"""
        if self.spi:
            # 模拟延迟
            time.sleep(0.1)
            # 创建撤单响应字典（简化实现，直接使用字典）
            from .utils import decode_str
            
            req_dict = req.to_dict()
            cancel_rsp_dict = {
                'Account': req_dict['Account'],
                'BoardId': req_dict['BoardId'],
                'OrderDate': req_dict['OrderDate'],
                'OrderNo': req_dict['OrderNo'],
                'OrderState': '0',  # 正常状态
                'ExeInfo': '撤单成功',
                'StkBiz': 100,
                'StkBizAction': 100,
                'Symbol': '600000',
            }
            
            error_dict = None  # 无错误
            
            # 调用 SPI 回调
            self.spi.on_rsp_cancel_ticket(request_id, error_dict, cancel_rsp_dict)
    
    def batch_order(self, orders: list, stk_biz: int = 100, stk_biz_action: int = 100) -> int:
        """批量下单
        
        Args:
            orders: 订单列表，每个订单是一个字典，包含以下字段：
                - trdacct: 股东账号
                - board_id: 交易板块
                - symbol: 证券代码
                - price: 委托价格
                - quantity: 委托数量
                - order_ref: 客户委托信息（可选）
            stk_biz: 证券业务（默认 100 表示买入）
            stk_biz_action: 证券业务指令（默认 100 表示限价单）
        
        Returns:
            请求编号，如果失败返回 -1
        
        Raises:
            OXConnectionError: 如果 API 未初始化或未登录
            OXOrderError: 如果批量下单请求失败或订单数量超出限制
        """
        if not self._initialized:
            raise OXConnectionError("API not initialized, call init() first")
        
        if not self._logged_in:
            raise OXConnectionError("Not logged in, call login() first")
        
        if not self.spi:
            raise OXOrderError("SPI not registered, call register_spi() first")
        
        # 获取账户信息
        account = getattr(self, '_account', '')
        if not account:
            raise OXOrderError("Account not available. Please login first and ensure login response contains account information.")
        acct_type = getattr(self, '_acct_type', AccountType.STOCK)
        
        # 验证订单数量
        if not orders:
            raise OXOrderError("Orders list cannot be empty")
        
        from .constants import MAX_ORDERS_COUNT
        if len(orders) > MAX_ORDERS_COUNT:
            raise OXOrderError(f"Orders count ({len(orders)}) exceeds maximum limit ({MAX_ORDERS_COUNT})")
        
        # 构建订单项列表
        order_items = []
        for i, order in enumerate(orders):
            order_item_dict = {
                'Trdacct': order.get('trdacct', ''),
                'BoardId': order.get('board_id', ''),
                'StkBiz': order.get('stk_biz', stk_biz),
                'StkBizAction': order.get('stk_biz_action', stk_biz_action),
                'Symbol': order.get('symbol', ''),
                'OrderQty': order.get('quantity', 0),
                'OrderPrice': order.get('price', 0),
                'OrderRef': order.get('order_ref', f'BATCH_{i+1}'),
            }
            order_items.append(order_item_dict)
        
        # 创建批量下单请求结构体
        req_dict = {
            'AcctType': acct_type.value if hasattr(acct_type, 'value') else acct_type,
            'Account': account,
            'StkBiz': stk_biz,
            'StkBizAction': stk_biz_action,
            'orderArray': order_items,
        }
        
        req = COXReqBatchOrderTicketField.from_dict(req_dict)
        
        # 调用 OnReqBatchOrderTicket 虚函数
        request_id = self._get_next_request_id()
        result = self._call_batch_order_virtual(request_id, req)
        
        if result != 0:
            raise OXOrderError(f"Batch order request failed with return code: {result}")
        
        return request_id
    
    def _call_batch_order_virtual(self, request_id: int, req: COXReqBatchOrderTicketField) -> int:
        """调用 OnReqBatchOrderTicket 虚函数
        
        注意：这是一个占位实现。实际需要通过虚函数表调用。
        对于测试环境，模拟批量下单请求并触发回调。
        """
        # TODO: 实现虚函数调用
        # 在实际环境中，需要通过虚函数表调用 OnReqBatchOrderTicket
        # 这里先模拟触发回调，供测试使用
        if self.spi:
            # 模拟批量下单响应回调
            threading.Thread(target=self._simulate_batch_order_callback, args=(request_id, req,), daemon=True).start()
        return 0
    
    def _simulate_batch_order_callback(self, request_id: int, req: COXReqBatchOrderTicketField) -> None:
        """模拟批量下单响应回调（仅用于测试）"""
        if self.spi:
            # 模拟延迟
            time.sleep(0.1)
            # 创建批量下单响应字典（简化实现，直接使用字典）
            req_dict = req.to_dict()
            
            error_dict = None  # 无错误
            
            # 调用 SPI 回调（批量下单响应返回的是请求字段本身）
            self.spi.on_rsp_batch_order(request_id, error_dict, req_dict)

