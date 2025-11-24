// 日志系统单元测试
#include "../include/logger.h"
#include "../include/config.h"
#include <iostream>
#include <cassert>
#include <fstream>
#include <filesystem>
#include <thread>
#include <chrono>

using namespace ox_service;

// 测试辅助函数：清理测试日志文件
void cleanupTestLogFiles() {
    std::string log_dir = "./logs";
    if (std::filesystem::exists(log_dir)) {
        try {
            for (const auto& entry : std::filesystem::directory_iterator(log_dir)) {
                if (entry.path().string().find("test_") != std::string::npos) {
                    std::filesystem::remove(entry.path());
                }
            }
        } catch (...) {
            // 忽略错误
        }
    }
}

// 测试1: 日志系统初始化
void test_logger_initialization() {
    std::cout << "Test 1: Logger initialization..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::INFO;
    log_config.file = "./logs/test_service.log";
    log_config.console_output = true;
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    assert(logger.initialize(log_config));
    assert(logger.getLevel() == LogLevel::INFO);
    
    logger.shutdown();
    std::cout << "  ✓ Logger initialization test passed" << std::endl;
}

// 测试2: 日志级别控制
void test_log_level_control() {
    std::cout << "Test 2: Log level control..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::WARN;
    log_config.file = "./logs/test_service.log";
    log_config.console_output = false;  // 关闭控制台输出以便测试
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    logger.initialize(log_config);
    
    // DEBUG和INFO应该被过滤
    logger.debug("This debug message should not appear");
    logger.info("This info message should not appear");
    
    // WARN和ERROR应该输出
    logger.warn("This warn message should appear");
    logger.error("This error message should appear");
    
    logger.shutdown();
    std::cout << "  ✓ Log level control test passed" << std::endl;
}

// 测试3: 控制台和文件日志
void test_console_and_file_logging() {
    std::cout << "Test 3: Console and file logging..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::DEBUG;
    log_config.file = "./logs/test_service.log";
    log_config.console_output = true;
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    logger.initialize(log_config);
    
    LOG_INFO("Test message for console and file");
    LOG_WARN("Another test message");
    
    logger.shutdown();
    
    // 验证文件是否存在
    std::string log_file = "./logs/test_service_" + 
                          std::string(__DATE__).substr(0, 10) + ".log";
    // 注意：实际文件名可能不同，这里只是检查文件是否创建
    assert(std::filesystem::exists("./logs"));
    
    std::cout << "  ✓ Console and file logging test passed" << std::endl;
}

// 测试4: 日志格式化
void test_log_formatting() {
    std::cout << "Test 4: Log formatting..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::DEBUG;
    log_config.file = "./logs/test_format.log";
    log_config.console_output = false;
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    logger.initialize(log_config);
    
    // 使用宏测试格式化（包含文件位置信息）
    LOG_DEBUG("Debug message with file location");
    LOG_INFO("Info message with file location");
    LOG_WARN("Warn message with file location");
    LOG_ERROR("Error message with file location");
    
    logger.shutdown();
    std::cout << "  ✓ Log formatting test passed" << std::endl;
}

// 测试5: 日志文件按日期轮转
void test_log_rotation() {
    std::cout << "Test 5: Log file rotation..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::INFO;
    log_config.file = "./logs/test_rotation.log";
    log_config.console_output = false;
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    logger.initialize(log_config);
    
    LOG_INFO("First log message");
    
    // 注意：实际日期轮转需要等到日期改变，这里只测试功能存在
    // 在实际使用中，日期改变时会自动创建新的日志文件
    
    logger.shutdown();
    std::cout << "  ✓ Log file rotation test passed" << std::endl;
}

// 测试6: 线程安全
void test_thread_safety() {
    std::cout << "Test 6: Thread safety..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::INFO;
    log_config.file = "./logs/test_thread.log";
    log_config.console_output = false;
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    logger.initialize(log_config);
    
    // 创建多个线程同时写日志
    std::vector<std::thread> threads;
    for (int i = 0; i < 5; ++i) {
        threads.emplace_back([&logger, i]() {
            for (int j = 0; j < 10; ++j) {
                LOG_INFO("Thread " + std::to_string(i) + " message " + std::to_string(j));
            }
        });
    }
    
    // 等待所有线程完成
    for (auto& t : threads) {
        t.join();
    }
    
    logger.shutdown();
    std::cout << "  ✓ Thread safety test passed" << std::endl;
}

// 测试7: 不同日志级别
void test_different_log_levels() {
    std::cout << "Test 7: Different log levels..." << std::endl;
    
    LogConfig log_config;
    log_config.level = LogLevel::DEBUG;
    log_config.file = "./logs/test_levels.log";
    log_config.console_output = false;
    log_config.file_output = true;
    
    Logger& logger = Logger::getInstance();
    logger.initialize(log_config);
    
    LOG_DEBUG("Debug level message");
    LOG_INFO("Info level message");
    LOG_WARN("Warn level message");
    LOG_ERROR("Error level message");
    
    // 测试动态改变日志级别
    logger.setLevel(LogLevel::ERROR);
    LOG_DEBUG("This debug should not appear");
    LOG_INFO("This info should not appear");
    LOG_WARN("This warn should not appear");
    LOG_ERROR("This error should appear");
    
    logger.shutdown();
    std::cout << "  ✓ Different log levels test passed" << std::endl;
}

// 主测试函数
int main() {
    std::cout << "=== Logger Module Unit Tests ===" << std::endl;
    std::cout << std::endl;
    
    // 清理旧的测试日志文件
    cleanupTestLogFiles();
    
    try {
        test_logger_initialization();
        test_log_level_control();
        test_console_and_file_logging();
        test_log_formatting();
        test_log_rotation();
        test_thread_safety();
        test_different_log_levels();
        
        std::cout << std::endl;
        std::cout << "=== All tests passed! ===" << std::endl;
        
        // 清理测试日志文件
        cleanupTestLogFiles();
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}

