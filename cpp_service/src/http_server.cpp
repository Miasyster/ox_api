#include "../include/http_server.h"
#include <sstream>
#include <iostream>
#include <thread>
#include <chrono>

namespace ox_service {

// 构造函数
HttpServer::HttpServer()
    : server_(std::make_unique<httplib::Server>())
    , is_running_(false)
    , cors_enabled_(true)
    , request_logging_enabled_(true)
    , cors_origin_("*")
{
}

// 析构函数
HttpServer::~HttpServer() {
    stop();
}

// 初始化服务器
bool HttpServer::initialize(const ServerConfig& config) {
    if (!config.validate()) {
        LOG_ERROR("Invalid server configuration");
        return false;
    }
    
    config_ = config;
    
    // 设置默认错误处理器
    server_->set_error_handler([](const httplib::Request& req, httplib::Response& res) {
        ErrorHandler& error_handler = ErrorHandler::getInstance();
        std::string json_str = error_handler.toJsonString(
            ErrorCode::NETWORK_ERROR,
            "Request handler not found"
        );
        res.set_content(json_str, "application/json");
        res.status = 404;
    });
    
    // 设置默认异常处理器（如果支持）
    // 注意：某些版本的httplib可能不支持set_exception_handler
    // 如果编译失败，可以注释掉这部分代码
    
    // 注册健康检查路由
    get("/health", [](const httplib::Request& req, httplib::Response& res) {
        nlohmann::json response;
        response["status"] = "ok";
        response["service"] = "ox_trading_service";
        res.set_content(response.dump(2), "application/json");
        res.status = 200;
    });
    
    LOG_INFO("HTTP server initialized on " + config.host + ":" + std::to_string(config.port));
    return true;
}

// 注册路由
void HttpServer::registerRoute(const std::string& method, const std::string& path, RequestHandler handler) {
    std::string key = method + ":" + path;
    routes_[key] = handler;
    
    // 注册到httplib服务器
    if (method == "GET") {
        server_->Get(path, [this, handler](const httplib::Request& req, httplib::Response& res) {
            handleRoute(req, res, handler);
        });
    } else if (method == "POST") {
        server_->Post(path, [this, handler](const httplib::Request& req, httplib::Response& res) {
            handleRoute(req, res, handler);
        });
    } else if (method == "PUT") {
        server_->Put(path, [this, handler](const httplib::Request& req, httplib::Response& res) {
            handleRoute(req, res, handler);
        });
    } else if (method == "DELETE") {
        server_->Delete(path, [this, handler](const httplib::Request& req, httplib::Response& res) {
            handleRoute(req, res, handler);
        });
    }
}

// 注册GET路由
void HttpServer::get(const std::string& path, RequestHandler handler) {
    registerRoute("GET", path, handler);
}

// 注册POST路由
void HttpServer::post(const std::string& path, RequestHandler handler) {
    registerRoute("POST", path, handler);
}

// 注册PUT路由
void HttpServer::put(const std::string& path, RequestHandler handler) {
    registerRoute("PUT", path, handler);
}

// 注册DELETE路由
void HttpServer::del(const std::string& path, RequestHandler handler) {
    registerRoute("DELETE", path, handler);
}

// 启动服务器
bool HttpServer::start() {
    if (is_running_) {
        LOG_WARN("Server is already running");
        return false;
    }
    
    if (!server_) {
        LOG_ERROR("Server not initialized");
        return false;
    }
    
    // 启动服务器（在后台线程）
    std::thread server_thread([this]() {
        is_running_ = true;
        LOG_INFO("Starting HTTP server on " + config_.host + ":" + std::to_string(config_.port));
        
        if (!server_->listen(config_.host.c_str(), config_.port)) {
            LOG_ERROR("Failed to start HTTP server");
            is_running_ = false;
        }
    });
    
    server_thread.detach();
    
    // 等待一小段时间确保服务器启动
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    if (is_running_) {
        LOG_INFO("HTTP server started successfully");
        return true;
    }
    
    return false;
}

// 停止服务器
void HttpServer::stop() {
    if (is_running_ && server_) {
        server_->stop();
        is_running_ = false;
        LOG_INFO("HTTP server stopped");
    }
}

// 处理CORS预检请求
void HttpServer::handleCORS(httplib::Response& res) {
    if (cors_enabled_) {
        res.set_header("Access-Control-Allow-Origin", cors_origin_);
        res.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization");
        res.set_header("Access-Control-Max-Age", "3600");
    }
}

// 记录请求日志
void HttpServer::logRequest(const httplib::Request& req, const httplib::Response& res) {
    if (request_logging_enabled_) {
        std::ostringstream oss;
        oss << req.method << " " << req.path << " - " << res.status;
        if (!req.body.empty()) {
            oss << " (body: " << req.body.length() << " bytes)";
        }
        LOG_INFO(oss.str());
    }
}

// 解析JSON请求体
nlohmann::json HttpServer::parseJsonBody(const std::string& body) {
    try {
        if (body.empty()) {
            return nlohmann::json::object();
        }
        return nlohmann::json::parse(body);
    } catch (const nlohmann::json::exception& e) {
        LOG_ERROR("Failed to parse JSON body: " + std::string(e.what()));
        return nlohmann::json();
    }
}

// 发送JSON响应
void HttpServer::sendJsonResponse(httplib::Response& res, const nlohmann::json& json, int status) {
    res.set_content(json.dump(2), "application/json");
    res.status = status;
    handleCORS(res);
}

// 发送错误响应
void HttpServer::sendErrorResponse(httplib::Response& res, ErrorCode code, const std::string& detail, int status) {
    ErrorHandler& error_handler = ErrorHandler::getInstance();
    ErrorResponse error_resp = error_handler.createErrorResponse(code, detail);
    sendJsonResponse(res, error_resp.toJson(), status);
}

// 发送成功响应
void HttpServer::sendSuccessResponse(httplib::Response& res, const nlohmann::json& data, int status) {
    SuccessResponse success_resp = ErrorHandler::createSuccessResponse(data);
    sendJsonResponse(res, success_resp.toJson(), status);
}

// 通用路由处理器（包含中间件）
void HttpServer::handleRoute(const httplib::Request& req, httplib::Response& res, RequestHandler handler) {
    // 处理OPTIONS请求（CORS预检）
    if (req.method == "OPTIONS") {
        handleCORS(res);
        res.status = 200;
        return;
    }
    
    // 记录请求开始时间
    auto start_time = std::chrono::steady_clock::now();
    
    try {
        // 调用实际的处理函数
        handler(req, res);
        
        // 处理CORS
        handleCORS(res);
        
        // 记录请求日志
        logRequest(req, res);
        
        // 记录响应时间
        auto end_time = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        if (request_logging_enabled_) {
            LOG_DEBUG("Request completed in " + std::to_string(duration.count()) + "ms");
        }
    } catch (const std::exception& e) {
        LOG_ERROR("Exception in route handler: " + std::string(e.what()));
        sendErrorResponse(res, ErrorCode::UNKNOWN_ERROR, e.what(), 500);
    } catch (...) {
        LOG_ERROR("Unknown exception in route handler");
        sendErrorResponse(res, ErrorCode::UNKNOWN_ERROR, "Internal server error", 500);
    }
}

} // namespace ox_service
