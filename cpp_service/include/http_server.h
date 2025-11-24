#ifndef HTTP_SERVER_H
#define HTTP_SERVER_H

#include "config.h"
#include "logger.h"
#include "error_handler.h"
#include "../third_party/json.hpp"
#include "../third_party/httplib.h"
#include <string>
#include <functional>
#include <memory>
#include <map>

namespace ox_service {

// 请求处理器类型定义
using RequestHandler = std::function<void(const httplib::Request&, httplib::Response&)>;

// HTTP服务器类
class HttpServer {
public:
    HttpServer();
    ~HttpServer();
    
    // 禁用拷贝构造和赋值
    HttpServer(const HttpServer&) = delete;
    HttpServer& operator=(const HttpServer&) = delete;
    
    // 初始化服务器
    bool initialize(const ServerConfig& config);
    
    // 注册路由
    void registerRoute(const std::string& method, const std::string& path, RequestHandler handler);
    
    // 便捷方法：注册GET路由
    void get(const std::string& path, RequestHandler handler);
    
    // 便捷方法：注册POST路由
    void post(const std::string& path, RequestHandler handler);
    
    // 便捷方法：注册PUT路由
    void put(const std::string& path, RequestHandler handler);
    
    // 便捷方法：注册DELETE路由
    void del(const std::string& path, RequestHandler handler);
    
    // 启动服务器
    bool start();
    
    // 停止服务器
    void stop();
    
    // 检查服务器是否运行
    bool isRunning() const { return is_running_; }
    
    // 启用/禁用CORS
    void enableCORS(bool enable = true) { cors_enabled_ = enable; }
    
    // 启用/禁用请求日志
    void enableRequestLogging(bool enable = true) { request_logging_enabled_ = enable; }
    
    // 设置CORS允许的源
    void setCORSOrigin(const std::string& origin) { cors_origin_ = origin; }

private:
    // 处理CORS预检请求
    void handleCORS(httplib::Response& res);
    
    // 记录请求日志
    void logRequest(const httplib::Request& req, const httplib::Response& res);
    
    // 解析JSON请求体
    nlohmann::json parseJsonBody(const std::string& body);
    
    // 发送JSON响应
    void sendJsonResponse(httplib::Response& res, const nlohmann::json& json, int status = 200);
    
    // 发送错误响应
    void sendErrorResponse(httplib::Response& res, ErrorCode code, const std::string& detail = "", int status = 400);
    
    // 发送成功响应
    void sendSuccessResponse(httplib::Response& res, const nlohmann::json& data = nlohmann::json::object(), int status = 200);
    
    // 通用路由处理器（包含中间件）
    void handleRoute(const httplib::Request& req, httplib::Response& res, RequestHandler handler);
    
    std::unique_ptr<httplib::Server> server_;
    ServerConfig config_;
    bool is_running_;
    bool cors_enabled_;
    bool request_logging_enabled_;
    std::string cors_origin_;
    
    // 路由映射：method+path -> handler
    std::map<std::string, RequestHandler> routes_;
};

} // namespace ox_service

#endif // HTTP_SERVER_H
