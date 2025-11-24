// 配置管理模块单元测试
#include "../include/config.h"
#include <iostream>
#include <cassert>
#include <fstream>
#include <filesystem>

using namespace ox_service;

// 测试辅助函数：创建临时配置文件
std::string createTempConfigFile(const std::string& content) {
    std::string temp_path = "./test_config_temp.json";
    std::ofstream file(temp_path);
    file << content;
    file.close();
    return temp_path;
}

// 清理临时文件
void cleanupTempFile(const std::string& path) {
    if (std::filesystem::exists(path)) {
        std::filesystem::remove(path);
    }
}

// 测试1: 默认配置
void test_default_config() {
    std::cout << "Test 1: Default config..." << std::endl;
    ConfigManager config;
    
    assert(config.getConfig().server.host == "127.0.0.1");
    assert(config.getConfig().server.port == 8080);
    assert(config.getConfig().server.threads == 4);
    assert(config.getConfig().ox_sdk.dll_path == "./bin/GuosenOXAPI.dll");
    assert(config.getConfig().log.level == LogLevel::INFO);
    
    assert(config.validate());
    std::cout << "  ✓ Default config test passed" << std::endl;
}

// 测试2: 从文件加载配置
void test_load_from_file() {
    std::cout << "Test 2: Load from file..." << std::endl;
    
    std::string json_content = R"({
        "server": {
            "host": "0.0.0.0",
            "port": 9090,
            "threads": 8
        },
        "ox_sdk": {
            "dll_path": "./test/GuosenOXAPI.dll",
            "config_path": "./test/config.ini"
        },
        "log": {
            "level": "debug",
            "file": "./test.log",
            "console_output": false
        }
    })";
    
    std::string temp_file = createTempConfigFile(json_content);
    
    ConfigManager config;
    assert(config.loadFromFile(temp_file));
    
    assert(config.getConfig().server.host == "0.0.0.0");
    assert(config.getConfig().server.port == 9090);
    assert(config.getConfig().server.threads == 8);
    assert(config.getConfig().ox_sdk.dll_path == "./test/GuosenOXAPI.dll");
    assert(config.getConfig().log.level == LogLevel::DEBUG);
    assert(config.getConfig().log.console_output == false);
    
    assert(config.validate());
    
    cleanupTempFile(temp_file);
    std::cout << "  ✓ Load from file test passed" << std::endl;
}

// 测试3: 部分配置（使用默认值）
void test_partial_config() {
    std::cout << "Test 3: Partial config (with defaults)..." << std::endl;
    
    std::string json_content = R"({
        "server": {
            "port": 9999
        }
    })";
    
    std::string temp_file = createTempConfigFile(json_content);
    
    ConfigManager config;
    assert(config.loadFromFile(temp_file));
    
    // 部分配置应该使用默认值
    assert(config.getConfig().server.host == "127.0.0.1"); // 默认值
    assert(config.getConfig().server.port == 9999); // 配置值
    assert(config.getConfig().server.threads == 4); // 默认值
    
    cleanupTempFile(temp_file);
    std::cout << "  ✓ Partial config test passed" << std::endl;
}

// 测试4: 配置验证
void test_config_validation() {
    std::cout << "Test 4: Config validation..." << std::endl;
    
    // 测试无效端口
    ConfigManager config1;
    config1.getConfig().server.port = 0; // 无效端口
    assert(!config1.validate());
    
    // 测试无效线程数
    ConfigManager config2;
    config2.getConfig().server.threads = 0; // 无效线程数
    assert(!config2.validate());
    
    // 测试空DLL路径
    ConfigManager config3;
    config3.getConfig().ox_sdk.dll_path = ""; // 空路径
    assert(!config3.validate());
    
    std::cout << "  ✓ Config validation test passed" << std::endl;
}

// 测试5: 日志级别转换
void test_log_level_conversion() {
    std::cout << "Test 5: Log level conversion..." << std::endl;
    
    assert(LogConfig::stringToLevel("debug") == LogLevel::DEBUG);
    assert(LogConfig::stringToLevel("info") == LogLevel::INFO);
    assert(LogConfig::stringToLevel("warn") == LogLevel::WARN);
    assert(LogConfig::stringToLevel("error") == LogLevel::ERROR);
    assert(LogConfig::stringToLevel("unknown") == LogLevel::INFO); // 默认值
    
    assert(LogConfig::levelToString(LogLevel::DEBUG) == "debug");
    assert(LogConfig::levelToString(LogLevel::INFO) == "info");
    assert(LogConfig::levelToString(LogLevel::WARN) == "warn");
    assert(LogConfig::levelToString(LogLevel::ERROR) == "error");
    
    std::cout << "  ✓ Log level conversion test passed" << std::endl;
}

// 测试6: 配置热加载
void test_config_reload() {
    std::cout << "Test 6: Config reload..." << std::endl;
    
    std::string json_content1 = R"({
        "server": {
            "port": 8080
        }
    })";
    
    std::string temp_file = createTempConfigFile(json_content1);
    
    ConfigManager config;
    config.loadFromFile(temp_file);
    assert(config.getConfig().server.port == 8080);
    
    // 修改配置文件
    std::string json_content2 = R"({
        "server": {
            "port": 9090
        }
    })";
    std::ofstream file(temp_file);
    file << json_content2;
    file.close();
    
    // 检查文件是否已修改
    assert(config.isConfigModified());
    
    // 重新加载
    assert(config.reload());
    assert(config.getConfig().server.port == 9090);
    
    cleanupTempFile(temp_file);
    std::cout << "  ✓ Config reload test passed" << std::endl;
}

// 测试7: 无效JSON文件
void test_invalid_json() {
    std::cout << "Test 7: Invalid JSON..." << std::endl;
    
    std::string invalid_json = "{ invalid json }";
    std::string temp_file = createTempConfigFile(invalid_json);
    
    ConfigManager config;
    assert(!config.loadFromFile(temp_file)); // 应该加载失败
    
    cleanupTempFile(temp_file);
    std::cout << "  ✓ Invalid JSON test passed" << std::endl;
}

// 主测试函数
int main() {
    std::cout << "=== Config Module Unit Tests ===" << std::endl;
    std::cout << std::endl;
    
    try {
        test_default_config();
        test_load_from_file();
        test_partial_config();
        test_config_validation();
        test_log_level_conversion();
        test_config_reload();
        test_invalid_json();
        
        std::cout << std::endl;
        std::cout << "=== All tests passed! ===" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}

