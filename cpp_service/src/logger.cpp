#include "../include/logger.h"
#include <iostream>
#include <chrono>
#include <sstream>
#include <iomanip>

namespace ox_service {

// 获取单例实例
Logger& Logger::getInstance() {
    static Logger instance;
    return instance;
}

// 初始化日志系统
bool Logger::initialize(const LogConfig& config) {
    std::lock_guard<std::mutex> lock(log_mutex_);
    
    if (initialized_) {
        shutdown();
    }
    
    current_level_ = config.level;
    console_output_ = config.console_output;
    file_output_ = config.file_output;
    log_file_base_path_ = config.file;
    
    if (file_output_ && !log_file_base_path_.empty()) {
        if (!openLogFile()) {
            return false;
        }
    }
    
    initialized_ = true;
    return true;
}

// 关闭日志系统
void Logger::shutdown() {
    std::lock_guard<std::mutex> lock(log_mutex_);
    
    if (log_file_.is_open()) {
        closeLogFile();
    }
    
    initialized_ = false;
}

// 析构函数
Logger::~Logger() {
    shutdown();
}

// Debug日志
void Logger::debug(const std::string& message, const std::string& file, int line) {
    if (shouldLog(LogLevel::DEBUG)) {
        log(LogLevel::DEBUG, message, file, line);
    }
}

// Info日志
void Logger::info(const std::string& message, const std::string& file, int line) {
    if (shouldLog(LogLevel::INFO)) {
        log(LogLevel::INFO, message, file, line);
    }
}

// Warn日志
void Logger::warn(const std::string& message, const std::string& file, int line) {
    if (shouldLog(LogLevel::WARN)) {
        log(LogLevel::WARN, message, file, line);
    }
}

// Error日志
void Logger::error(const std::string& message, const std::string& file, int line) {
    if (shouldLog(LogLevel::ERROR)) {
        log(LogLevel::ERROR, message, file, line);
    }
}

// 设置日志级别
void Logger::setLevel(LogLevel level) {
    std::lock_guard<std::mutex> lock(log_mutex_);
    current_level_ = level;
}

// 检查是否应该输出日志
bool Logger::shouldLog(LogLevel level) const {
    return static_cast<int>(level) >= static_cast<int>(current_level_);
}

// 内部日志输出方法
void Logger::log(LogLevel level, const std::string& message, const std::string& file, int line) {
    if (!initialized_) {
        return;
    }
    
    std::lock_guard<std::mutex> lock(log_mutex_);
    
    // 检查并执行日志文件轮转
    if (file_output_) {
        checkAndRotateLogFile();
    }
    
    // 格式化消息
    std::string formatted_msg = formatMessage(level, message, file, line);
    
    // 输出到控制台
    if (console_output_) {
        std::cout << formatted_msg << std::endl;
    }
    
    // 输出到文件
    if (file_output_ && log_file_.is_open()) {
        log_file_ << formatted_msg << std::endl;
        log_file_.flush();  // 立即刷新，确保日志及时写入
    }
}

// 格式化日志消息
std::string Logger::formatMessage(LogLevel level, const std::string& message, 
                                   const std::string& file, int line) {
    std::ostringstream oss;
    
    // 时间戳
    oss << "[" << getCurrentTime() << "] ";
    
    // 日志级别
    oss << "[" << getLevelString(level) << "] ";
    
    // 文件位置信息（如果提供）
    if (!file.empty() && line > 0) {
        // 只取文件名，不包含路径
        std::filesystem::path file_path(file);
        oss << "[" << file_path.filename().string() << ":" << line << "] ";
    }
    
    // 日志消息
    oss << message;
    
    return oss.str();
}

// 获取当前时间字符串
std::string Logger::getCurrentTime() const {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;
    
    std::tm tm_buf;
#ifdef _WIN32
    localtime_s(&tm_buf, &time_t);
#else
    localtime_r(&time_t, &tm_buf);
#endif
    
    std::ostringstream oss;
    oss << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S");
    oss << "." << std::setfill('0') << std::setw(3) << ms.count();
    
    return oss.str();
}

// 获取日志级别字符串
std::string Logger::getLevelString(LogLevel level) const {
    switch (level) {
        case LogLevel::DEBUG: return "DEBUG";
        case LogLevel::INFO:  return "INFO ";
        case LogLevel::WARN:  return "WARN ";
        case LogLevel::ERROR: return "ERROR";
        default: return "UNKNOWN";
    }
}

// 检查并执行日志文件轮转
void Logger::checkAndRotateLogFile() {
    if (log_file_base_path_.empty()) {
        return;
    }
    
    std::string current_date = getCurrentTime().substr(0, 10);  // 获取日期部分 YYYY-MM-DD
    
    // 如果日期改变，需要轮转日志文件
    if (current_date != last_log_date_) {
        closeLogFile();
        last_log_date_ = current_date;
        openLogFile();
    }
}

// 获取日志文件名（带日期）
std::string Logger::getLogFileName() const {
    if (log_file_base_path_.empty()) {
        return "";
    }
    
    std::string current_date = getCurrentTime().substr(0, 10);  // YYYY-MM-DD
    
    std::filesystem::path base_path(log_file_base_path_);
    std::filesystem::path dir = base_path.parent_path();
    std::filesystem::path filename = base_path.filename();
    std::filesystem::path stem = filename.stem();
    std::filesystem::path extension = filename.extension();
    
    // 创建带日期的文件名：原文件名_YYYY-MM-DD.扩展名
    std::filesystem::path new_filename = stem;
    new_filename += "_";
    new_filename += current_date;
    new_filename += extension;
    
    if (!dir.empty()) {
        return (dir / new_filename).string();
    } else {
        return new_filename.string();
    }
}

// 打开日志文件
bool Logger::openLogFile() {
    if (log_file_base_path_.empty()) {
        return false;
    }
    
    // 获取带日期的日志文件名
    log_file_path_ = getLogFileName();
    
    // 确保日志目录存在
    std::filesystem::path log_path(log_file_path_);
    std::filesystem::path log_dir = log_path.parent_path();
    if (!log_dir.empty() && !std::filesystem::exists(log_dir)) {
        try {
            std::filesystem::create_directories(log_dir);
        } catch (const std::filesystem::filesystem_error& e) {
            std::cerr << "Failed to create log directory: " << e.what() << std::endl;
            return false;
        }
    }
    
    // 打开日志文件（追加模式）
    log_file_.open(log_file_path_, std::ios::app);
    if (!log_file_.is_open()) {
        std::cerr << "Failed to open log file: " << log_file_path_ << std::endl;
        return false;
    }
    
    // 更新最后日志日期
    last_log_date_ = getCurrentTime().substr(0, 10);
    
    return true;
}

// 关闭日志文件
void Logger::closeLogFile() {
    if (log_file_.is_open()) {
        log_file_.close();
    }
}

} // namespace ox_service

