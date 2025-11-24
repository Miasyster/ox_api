#ifndef LOGGER_H
#define LOGGER_H

#include "config.h"
#include <string>
#include <fstream>
#include <mutex>
#include <memory>
#include <sstream>
#include <iomanip>
#include <ctime>
#include <filesystem>

namespace ox_service {

// 日志类
class Logger {
public:
    // 获取单例实例
    static Logger& getInstance();
    
    // 初始化日志系统
    bool initialize(const LogConfig& config);
    
    // 关闭日志系统
    void shutdown();
    
    // 日志输出方法（带文件位置信息）
    void debug(const std::string& message, 
               const std::string& file = "", 
               int line = 0);
    
    void info(const std::string& message, 
              const std::string& file = "", 
              int line = 0);
    
    void warn(const std::string& message, 
              const std::string& file = "", 
              int line = 0);
    
    void error(const std::string& message, 
               const std::string& file = "", 
               int line = 0);
    
    // 设置日志级别
    void setLevel(LogLevel level);
    
    // 获取当前日志级别
    LogLevel getLevel() const { return current_level_; }
    
    // 检查是否应该输出日志
    bool shouldLog(LogLevel level) const;
    
    // 禁用拷贝构造和赋值
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

private:
    Logger() = default;
    ~Logger();
    
    // 内部日志输出方法
    void log(LogLevel level, 
             const std::string& message, 
             const std::string& file = "", 
             int line = 0);
    
    // 格式化日志消息
    std::string formatMessage(LogLevel level, 
                              const std::string& message, 
                              const std::string& file = "", 
                              int line = 0);
    
    // 获取当前时间字符串
    std::string getCurrentTime() const;
    
    // 获取日志级别字符串
    std::string getLevelString(LogLevel level) const;
    
    // 检查并执行日志文件轮转
    void checkAndRotateLogFile();
    
    // 获取日志文件名（带日期）
    std::string getLogFileName() const;
    
    // 打开日志文件
    bool openLogFile();
    
    // 关闭日志文件
    void closeLogFile();
    
    LogLevel current_level_ = LogLevel::INFO;
    std::ofstream log_file_;
    std::string log_file_path_;
    std::string log_file_base_path_;
    bool console_output_ = true;
    bool file_output_ = true;
    std::mutex log_mutex_;
    bool initialized_ = false;
    std::string last_log_date_;  // 用于日期轮转
};

// 便捷宏定义
#define LOG_DEBUG(msg) Logger::getInstance().debug(msg, __FILE__, __LINE__)
#define LOG_INFO(msg) Logger::getInstance().info(msg, __FILE__, __LINE__)
#define LOG_WARN(msg) Logger::getInstance().warn(msg, __FILE__, __LINE__)
#define LOG_ERROR(msg) Logger::getInstance().error(msg, __FILE__, __LINE__)

} // namespace ox_service

#endif // LOGGER_H

