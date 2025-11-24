#ifndef CONFIG_H
#define CONFIG_H

#include <string>
#include <memory>
#include <chrono>
#include <filesystem>

namespace ox_service {

// 日志级别枚举
enum class LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
};

// 服务器配置结构体
struct ServerConfig {
    std::string host = "127.0.0.1";
    int port = 8080;
    int threads = 4;
    
    bool validate() const;
};

// OX SDK配置结构体
struct OXSDKConfig {
    std::string dll_path = "./bin/GuosenOXAPI.dll";
    std::string config_path = "./bin/config/config.ini";
    
    bool validate() const;
};

// 日志配置结构体
struct LogConfig {
    LogLevel level = LogLevel::INFO;
    std::string file = "./logs/service.log";
    bool console_output = true;
    bool file_output = true;
    
    bool validate() const;
    static LogLevel stringToLevel(const std::string& level);
    static std::string levelToString(LogLevel level);
};

// 完整配置结构体
struct ServiceConfig {
    ServerConfig server;
    OXSDKConfig ox_sdk;
    LogConfig log;
    
    bool validate() const;
};

// 配置管理类
class ConfigManager {
public:
    ConfigManager();
    ~ConfigManager();
    
    // 禁用拷贝构造和赋值
    ConfigManager(const ConfigManager&) = delete;
    ConfigManager& operator=(const ConfigManager&) = delete;
    
    // 加载配置文件
    bool loadFromFile(const std::string& config_path);
    
    // 加载默认配置
    void loadDefaults();
    
    // 获取配置
    const ServiceConfig& getConfig() const { return config_; }
    ServiceConfig& getConfig() { return config_; }
    
    // 验证配置
    bool validate() const;
    
    // 重新加载配置（热加载）
    bool reload();
    
    // 获取配置文件路径
    std::string getConfigPath() const { return config_path_; }
    
    // 检查配置文件是否已修改（用于热加载）
    bool isConfigModified() const;
    
private:
    ServiceConfig config_;
    std::string config_path_;
    std::filesystem::file_time_type last_modified_time_;
    
    // 从JSON对象解析配置
    bool parseFromJson(const std::string& json_content);
    
    // 更新文件修改时间
    void updateFileTime();
};

} // namespace ox_service

#endif // CONFIG_H

