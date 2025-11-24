// 错误处理模块单元测试
#include "../include/error_handler.h"
#include <iostream>
#include <cassert>
#include <sstream>

using namespace ox_service;

// 测试1: 错误码枚举
void test_error_code_enum() {
    std::cout << "Test 1: Error code enum..." << std::endl;
    
    assert(static_cast<int>(ErrorCode::SUCCESS) == 0);
    assert(static_cast<int>(ErrorCode::NOT_INITIALIZED) == 1001);
    assert(static_cast<int>(ErrorCode::LOGIN_FAILED) == 1002);
    assert(static_cast<int>(ErrorCode::INVALID_PARAM) == 1003);
    assert(static_cast<int>(ErrorCode::ORDER_FAILED) == 1004);
    assert(static_cast<int>(ErrorCode::NETWORK_ERROR) == 1005);
    
    std::cout << "  ✓ Error code enum test passed" << std::endl;
}

// 测试2: 获取错误信息
void test_get_error_info() {
    std::cout << "Test 2: Get error info..." << std::endl;
    
    ErrorHandler& handler = ErrorHandler::getInstance();
    
    ErrorInfo info1 = handler.getErrorInfo(ErrorCode::SUCCESS);
    (void)handler;  // 避免未使用警告
    assert(info1.code == ErrorCode::SUCCESS);
    assert(info1.message == "Success");
    
    ErrorInfo info2 = handler.getErrorInfo(ErrorCode::LOGIN_FAILED);
    assert(info2.code == ErrorCode::LOGIN_FAILED);
    assert(info2.message == "Login Failed");
    
    ErrorInfo info3 = handler.getErrorInfo(ErrorCode::INVALID_PARAM);
    assert(info3.code == ErrorCode::INVALID_PARAM);
    assert(info3.message == "Invalid Parameter");
    
    std::cout << "  ✓ Get error info test passed" << std::endl;
}

// 测试3: 获取错误消息
void test_get_error_message() {
    std::cout << "Test 3: Get error message..." << std::endl;
    
    ErrorHandler& handler = ErrorHandler::getInstance();
    
    assert(handler.getErrorMessage(ErrorCode::SUCCESS) == "Success");
    assert(handler.getErrorMessage(ErrorCode::NETWORK_ERROR) == "Network Error");
    assert(handler.getErrorMessage(ErrorCode::TIMEOUT) == "Timeout");
    
    std::cout << "  ✓ Get error message test passed" << std::endl;
}

// 测试4: 创建错误响应
void test_create_error_response() {
    std::cout << "Test 4: Create error response..." << std::endl;
    
    ErrorHandler& handler = ErrorHandler::getInstance();
    
    ErrorResponse response1 = handler.createErrorResponse(ErrorCode::LOGIN_FAILED);
    assert(response1.status == "error");
    assert(response1.error_code == static_cast<int>(ErrorCode::LOGIN_FAILED));
    assert(response1.message == "Login Failed");
    
    ErrorResponse response2 = handler.createErrorResponse(
        ErrorCode::INVALID_PARAM, 
        "Missing required field: account"
    );
    assert(response2.status == "error");
    assert(response2.error_code == static_cast<int>(ErrorCode::INVALID_PARAM));
    assert(response2.message == "Invalid Parameter");
    assert(response2.detail == "Missing required field: account");
    
    std::cout << "  ✓ Create error response test passed" << std::endl;
}

// 测试5: 创建成功响应
void test_create_success_response() {
    std::cout << "Test 5: Create success response..." << std::endl;
    
    nlohmann::json data;
    data["order_id"] = "123456";
    data["status"] = "placed";
    
    SuccessResponse response = ErrorHandler::createSuccessResponse(data);
    assert(response.status == "success");
    assert(response.data["order_id"] == "123456");
    assert(response.data["status"] == "placed");
    
    SuccessResponse empty_response = ErrorHandler::createSuccessResponse();
    assert(empty_response.status == "success");
    assert(empty_response.data.is_object());
    
    std::cout << "  ✓ Create success response test passed" << std::endl;
}

// 测试6: 错误响应JSON格式
void test_error_response_json() {
    std::cout << "Test 6: Error response JSON format..." << std::endl;
    
    ErrorHandler& handler = ErrorHandler::getInstance();
    
    ErrorResponse response = handler.createErrorResponse(
        ErrorCode::ORDER_FAILED,
        "Insufficient balance"
    );
    
    nlohmann::json j = response.toJson();
    assert(j["status"] == "error");
    assert(j["error_code"] == static_cast<int>(ErrorCode::ORDER_FAILED));
    assert(j["message"] == "Order Failed");
    assert(j["detail"] == "Insufficient balance");
    
    std::cout << "  ✓ Error response JSON format test passed" << std::endl;
}

// 测试7: 成功响应JSON格式
void test_success_response_json() {
    std::cout << "Test 7: Success response JSON format..." << std::endl;
    
    nlohmann::json data;
    data["session_id"] = "abc123";
    data["account"] = "620000259568";
    
    SuccessResponse response = ErrorHandler::createSuccessResponse(data);
    nlohmann::json j = response.toJson();
    
    assert(j["status"] == "success");
    assert(j["data"]["session_id"] == "abc123");
    assert(j["data"]["account"] == "620000259568");
    
    std::cout << "  ✓ Success response JSON format test passed" << std::endl;
}

// 测试8: JSON字符串转换
void test_json_string_conversion() {
    std::cout << "Test 8: JSON string conversion..." << std::endl;
    
    ErrorHandler& handler = ErrorHandler::getInstance();
    
    // 测试错误响应JSON字符串
    std::string error_json = handler.toJsonString(ErrorCode::CONFIG_ERROR, "Config file not found");
    assert(error_json.find("error") != std::string::npos);
    assert(error_json.find("1006") != std::string::npos);
    assert(error_json.find("Configuration Error") != std::string::npos);
    
    // 测试成功响应JSON字符串
    nlohmann::json data;
    data["result"] = "ok";
    SuccessResponse success_response = ErrorHandler::createSuccessResponse(data);
    std::string success_json = ErrorHandler::toJsonString(success_response);
    assert(success_json.find("success") != std::string::npos);
    assert(success_json.find("result") != std::string::npos);
    
    std::cout << "  ✓ JSON string conversion test passed" << std::endl;
}

// 测试9: 未知错误码处理
void test_unknown_error_code() {
    std::cout << "Test 9: Unknown error code handling..." << std::endl;
    
    ErrorHandler& handler = ErrorHandler::getInstance();
    
    // 测试一个不存在的错误码（通过强制转换）
    ErrorCode unknown_code = static_cast<ErrorCode>(99999);
    ErrorInfo info = handler.getErrorInfo(unknown_code);
    
    // 应该返回UNKNOWN_ERROR的信息
    assert(info.code == ErrorCode::UNKNOWN_ERROR || 
           info.message == "Unknown Error");
    
    std::cout << "  ✓ Unknown error code handling test passed" << std::endl;
}

// 测试10: 错误信息结构体
void test_error_info_struct() {
    std::cout << "Test 10: Error info struct..." << std::endl;
    
    ErrorInfo info1;
    assert(info1.code == ErrorCode::SUCCESS);
    assert(info1.message.empty());
    assert(info1.detail.empty());
    
    ErrorInfo info2(ErrorCode::NETWORK_ERROR, "Connection failed", "Timeout after 30s");
    assert(info2.code == ErrorCode::NETWORK_ERROR);
    assert(info2.message == "Connection failed");
    assert(info2.detail == "Timeout after 30s");
    
    std::cout << "  ✓ Error info struct test passed" << std::endl;
}

// 主测试函数
int main() {
    std::cout << "=== Error Handler Module Unit Tests ===" << std::endl;
    std::cout << std::endl;
    
    try {
        test_error_code_enum();
        test_get_error_info();
        test_get_error_message();
        test_create_error_response();
        test_create_success_response();
        test_error_response_json();
        test_success_response_json();
        test_json_string_conversion();
        test_unknown_error_code();
        test_error_info_struct();
        
        std::cout << std::endl;
        std::cout << "=== All tests passed! ===" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}

