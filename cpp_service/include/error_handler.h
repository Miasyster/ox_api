#ifndef ERROR_HANDLER_H
#define ERROR_HANDLER_H

#include <string>
#include <map>
#include "../third_party/json.hpp"

namespace ox_service {

// 错误码枚举
enum class ErrorCode {
    SUCCESS = 0,
    NOT_INITIALIZED = 1001,
    LOGIN_FAILED = 1002,
    INVALID_PARAM = 1003,
    ORDER_FAILED = 1004,
    NETWORK_ERROR = 1005,
    CONFIG_ERROR = 1006,
    SDK_ERROR = 1007,
    TIMEOUT = 1008,
    UNKNOWN_ERROR = 9999
};

// 错误信息结构体
struct ErrorInfo {
    ErrorCode code;
    std::string message;
    std::string detail;
    
    ErrorInfo() : code(ErrorCode::SUCCESS), message(""), detail("") {}
    ErrorInfo(ErrorCode c, const std::string& msg, const std::string& det = "")
        : code(c), message(msg), detail(det) {}
};

// 错误响应结构体（用于HTTP响应）
struct ErrorResponse {
    std::string status;
    int error_code;
    std::string message;
    std::string detail;
    
    ErrorResponse() : status("error"), error_code(0), message(""), detail("") {}
    ErrorResponse(ErrorCode code, const std::string& msg, const std::string& det = "")
        : status("error"), error_code(static_cast<int>(code)), message(msg), detail(det) {}
    
    // 转换为JSON
    nlohmann::json toJson() const;
};

// 成功响应结构体
struct SuccessResponse {
    std::string status;
    nlohmann::json data;
    
    SuccessResponse() : status("success"), data(nlohmann::json::object()) {}
    SuccessResponse(const nlohmann::json& d) : status("success"), data(d) {}
    
    // 转换为JSON
    nlohmann::json toJson() const;
};

// 错误处理类
class ErrorHandler {
public:
    // 获取单例实例
    static ErrorHandler& getInstance();
    
    // 获取错误信息
    ErrorInfo getErrorInfo(ErrorCode code) const;
    
    // 获取错误消息
    std::string getErrorMessage(ErrorCode code) const;
    
    // 创建错误响应
    ErrorResponse createErrorResponse(ErrorCode code, const std::string& detail = "") const;
    
    // 创建成功响应
    static SuccessResponse createSuccessResponse(const nlohmann::json& data = nlohmann::json::object());
    
    // 从错误码创建JSON响应
    std::string toJsonString(ErrorCode code, const std::string& detail = "") const;
    
    // 从ErrorResponse创建JSON字符串
    std::string toJsonString(const ErrorResponse& response) const;
    
    // 从SuccessResponse创建JSON字符串
    static std::string toJsonString(const SuccessResponse& response);
    
    // 禁用拷贝构造和赋值
    ErrorHandler(const ErrorHandler&) = delete;
    ErrorHandler& operator=(const ErrorHandler&) = delete;

private:
    ErrorHandler();
    
    // 初始化错误码映射
    void initializeErrorMap();
    
    // 错误码到错误信息的映射
    std::map<ErrorCode, ErrorInfo> error_map_;
};

} // namespace ox_service

#endif // ERROR_HANDLER_H

