#include "../include/config.h"
#include "../third_party/json.hpp"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

using json = nlohmann::json;

namespace ox_service {

// ServerConfig 验证
bool ServerConfig::validate() const {
    if (port < 1 || port > 65535) {
        return false;
    }
    if (threads < 1 || threads > 32) {
        return false;
    }
    if (host.empty()) {
        return false;
    }
    return true;
}

// OXSDKConfig 验证
bool OXSDKConfig::validate() const {
    if (dll_path.empty()) {
        return false;
    }
    if (config_path.empty()) {
        return false;
    }
    return true;
}

// LogConfig 验证
bool LogConfig::validate() const {
    if (file.empty() && file_output) {
        return false;
    }
    return true;
}

// 字符串转日志级别
LogLevel LogConfig::stringToLevel(const std::string& level) {
    std::string lower_level = level;
    std::transform(lower_level.begin(), lower_level.end(), lower_level.begin(), 
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    
    if (lower_level == "debug") return LogLevel::DEBUG;
    if (lower_level == "info") return LogLevel::INFO;
    if (lower_level == "warn") return LogLevel::WARN;
    if (lower_level == "error") return LogLevel::ERROR;
    
    return LogLevel::INFO; // 默认返回INFO
}

// 日志级别转字符串
std::string LogConfig::levelToString(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG: return "debug";
        case LogLevel::INFO: return "info";
        case LogLevel::WARN: return "warn";
        case LogLevel::ERROR: return "error";
        default: return "info";
    }
}

// ServiceConfig 验证
bool ServiceConfig::validate() const {
    if (!server.validate()) {
        return false;
    }
    if (!ox_sdk.validate()) {
        return false;
    }
    if (!log.validate()) {
        return false;
    }
    return true;
}

// ConfigManager 构造函数
ConfigManager::ConfigManager() {
    loadDefaults();
}

// ConfigManager 析构函数
ConfigManager::~ConfigManager() = default;

// 加载默认配置
void ConfigManager::loadDefaults() {
    // 使用结构体的默认值
    config_ = ServiceConfig();
}

// 从文件加载配置
bool ConfigManager::loadFromFile(const std::string& config_path) {
    config_path_ = config_path;
    
    std::ifstream file(config_path);
    if (!file.is_open()) {
        std::cerr << "Failed to open config file: " << config_path << std::endl;
        return false;
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string json_content = buffer.str();
    file.close();
    
    if (!parseFromJson(json_content)) {
        std::cerr << "Failed to parse config file: " << config_path << std::endl;
        return false;
    }
    
    updateFileTime();
    return true;
}

// 从JSON解析配置
bool ConfigManager::parseFromJson(const std::string& json_content) {
    try {
        json j = json::parse(json_content);
        
        // 解析服务器配置
        if (j.contains("server")) {
            auto& server = j["server"];
            if (server.contains("host")) {
                config_.server.host = server["host"].get<std::string>();
            }
            if (server.contains("port")) {
                config_.server.port = server["port"].get<int>();
            }
            if (server.contains("threads")) {
                config_.server.threads = server["threads"].get<int>();
            }
        }
        
        // 解析OX SDK配置
        if (j.contains("ox_sdk")) {
            auto& ox_sdk = j["ox_sdk"];
            if (ox_sdk.contains("dll_path")) {
                config_.ox_sdk.dll_path = ox_sdk["dll_path"].get<std::string>();
            }
            if (ox_sdk.contains("config_path")) {
                config_.ox_sdk.config_path = ox_sdk["config_path"].get<std::string>();
            }
        }
        
        // 解析日志配置
        if (j.contains("log")) {
            auto& log = j["log"];
            if (log.contains("level")) {
                config_.log.level = LogConfig::stringToLevel(log["level"].get<std::string>());
            }
            if (log.contains("file")) {
                config_.log.file = log["file"].get<std::string>();
            }
            if (log.contains("console_output")) {
                config_.log.console_output = log["console_output"].get<bool>();
            }
            if (log.contains("file_output")) {
                config_.log.file_output = log["file_output"].get<bool>();
            }
        }
        
        return true;
    } catch (const json::exception& e) {
        std::cerr << "JSON parse error: " << e.what() << std::endl;
        return false;
    } catch (...) {
        std::cerr << "Unknown error parsing JSON config" << std::endl;
        return false;
    }
}

// 验证配置
bool ConfigManager::validate() const {
    return config_.validate();
}

// 重新加载配置
bool ConfigManager::reload() {
    if (config_path_.empty()) {
        return false;
    }
    return loadFromFile(config_path_);
}

// 更新文件修改时间
void ConfigManager::updateFileTime() {
    try {
        if (std::filesystem::exists(config_path_)) {
            last_modified_time_ = std::filesystem::last_write_time(config_path_);
        }
    } catch (const std::filesystem::filesystem_error& e) {
        std::cerr << "Failed to get file time: " << e.what() << std::endl;
    }
}

// 检查配置文件是否已修改
bool ConfigManager::isConfigModified() const {
    if (config_path_.empty()) {
        return false;
    }
    
    try {
        if (!std::filesystem::exists(config_path_)) {
            return false;
        }
        
        auto current_time = std::filesystem::last_write_time(config_path_);
        return current_time != last_modified_time_;
    } catch (const std::filesystem::filesystem_error& e) {
        std::cerr << "Failed to check file time: " << e.what() << std::endl;
        return false;
    }
}

} // namespace ox_service

