#include "../include/error_handler.h"
#include <sstream>

namespace ox_service {

// 获取单例实例
ErrorHandler& ErrorHandler::getInstance() {
    static ErrorHandler instance;
    return instance;
}

// 构造函数
ErrorHandler::ErrorHandler() {
    initializeErrorMap();
}

// 初始化错误码映射
void ErrorHandler::initializeErrorMap() {
    error_map_[ErrorCode::SUCCESS] = ErrorInfo(
        ErrorCode::SUCCESS,
        "Success",
        "Operation completed successfully"
    );
    
    error_map_[ErrorCode::NOT_INITIALIZED] = ErrorInfo(
        ErrorCode::NOT_INITIALIZED,
        "Not Initialized",
        "Service or SDK is not initialized"
    );
    
    error_map_[ErrorCode::LOGIN_FAILED] = ErrorInfo(
        ErrorCode::LOGIN_FAILED,
        "Login Failed",
        "Failed to login to trading account"
    );
    
    error_map_[ErrorCode::INVALID_PARAM] = ErrorInfo(
        ErrorCode::INVALID_PARAM,
        "Invalid Parameter",
        "Invalid or missing parameter in request"
    );
    
    error_map_[ErrorCode::ORDER_FAILED] = ErrorInfo(
        ErrorCode::ORDER_FAILED,
        "Order Failed",
        "Failed to place or cancel order"
    );
    
    error_map_[ErrorCode::NETWORK_ERROR] = ErrorInfo(
        ErrorCode::NETWORK_ERROR,
        "Network Error",
        "Network connection error occurred"
    );
    
    error_map_[ErrorCode::CONFIG_ERROR] = ErrorInfo(
        ErrorCode::CONFIG_ERROR,
        "Configuration Error",
        "Configuration file error or missing configuration"
    );
    
    error_map_[ErrorCode::SDK_ERROR] = ErrorInfo(
        ErrorCode::SDK_ERROR,
        "SDK Error",
        "OX SDK internal error"
    );
    
    error_map_[ErrorCode::TIMEOUT] = ErrorInfo(
        ErrorCode::TIMEOUT,
        "Timeout",
        "Operation timeout"
    );
    
    error_map_[ErrorCode::UNKNOWN_ERROR] = ErrorInfo(
        ErrorCode::UNKNOWN_ERROR,
        "Unknown Error",
        "An unknown error occurred"
    );
}

// 获取错误信息
ErrorInfo ErrorHandler::getErrorInfo(ErrorCode code) const {
    auto it = error_map_.find(code);
    if (it != error_map_.end()) {
        return it->second;
    }
    return error_map_.at(ErrorCode::UNKNOWN_ERROR);
}

// 获取错误消息
std::string ErrorHandler::getErrorMessage(ErrorCode code) const {
    return getErrorInfo(code).message;
}

// 创建错误响应
ErrorResponse ErrorHandler::createErrorResponse(ErrorCode code, const std::string& detail) const {
    ErrorInfo info = getErrorInfo(code);
    ErrorResponse response(code, info.message, detail.empty() ? info.detail : detail);
    return response;
}

// 创建成功响应
SuccessResponse ErrorHandler::createSuccessResponse(const nlohmann::json& data) {
    return SuccessResponse(data);
}

// 从错误码创建JSON响应字符串
std::string ErrorHandler::toJsonString(ErrorCode code, const std::string& detail) const {
    ErrorResponse response = createErrorResponse(code, detail);
    return toJsonString(response);
}

// 从ErrorResponse创建JSON字符串
std::string ErrorHandler::toJsonString(const ErrorResponse& response) const {
    nlohmann::json j = response.toJson();
    return j.dump(2);
}

// 从SuccessResponse创建JSON字符串
std::string ErrorHandler::toJsonString(const SuccessResponse& response) {
    nlohmann::json j = response.toJson();
    return j.dump(2);
}

// ErrorResponse转换为JSON
nlohmann::json ErrorResponse::toJson() const {
    nlohmann::json j;
    j["status"] = status;
    j["error_code"] = error_code;
    j["message"] = message;
    if (!detail.empty()) {
        j["detail"] = detail;
    }
    return j;
}

// SuccessResponse转换为JSON
nlohmann::json SuccessResponse::toJson() const {
    nlohmann::json j;
    j["status"] = status;
    j["data"] = data;
    return j;
}

} // namespace ox_service

