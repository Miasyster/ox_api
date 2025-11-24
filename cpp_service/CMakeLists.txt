cmake_minimum_required(VERSION 3.12)
project(ox_trading_service)

# 设置C++17标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 包含目录
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
)

# 库目录
link_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/../lib
)

# 编译选项
if(MSVC)
    # Visual Studio编译选项
    add_compile_options(/W4)  # 警告级别4
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
    
    # Debug配置
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MDd")
    # Release配置
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MD /O2")
else()
    # GCC/Clang编译选项
    add_compile_options(-Wall -Wextra)
    
    # Debug配置
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
    # Release配置
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")
endif()

# 测试依赖库的源文件
add_executable(test_dependencies
    src/test_dependencies.cpp
)

# 设置输出目录
set_target_properties(test_dependencies PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# 配置模块库
add_library(config_lib
    src/config.cpp
)

# 日志模块库
add_library(logger_lib
    src/logger.cpp
)

# 日志模块依赖配置模块
target_link_libraries(logger_lib
    config_lib
)

# 主服务程序（空项目测试用）
add_executable(ox_service
    src/main.cpp
)

# 链接国信OX SDK库和配置模块
target_link_libraries(ox_service
    config_lib
    GuosenOXAPI
)

# 设置输出目录
set_target_properties(ox_service PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# 配置模块单元测试
add_executable(test_config
    tests/test_config.cpp
    src/config.cpp
)

target_link_libraries(test_config
    config_lib
)

# 日志模块单元测试
add_executable(test_logger
    tests/test_logger.cpp
    src/logger.cpp
    src/config.cpp
)

target_link_libraries(test_logger
    logger_lib
    config_lib
)

# 错误处理模块库
add_library(error_handler_lib
    src/error_handler.cpp
)

# HTTP服务器模块库
add_library(http_server_lib
    src/http_server.cpp
)

# HTTP服务器依赖其他模块
target_link_libraries(http_server_lib
    logger_lib
    config_lib
    error_handler_lib
)

# 错误处理模块单元测试
add_executable(test_error_handler
    tests/test_error_handler.cpp
    src/error_handler.cpp
)

target_link_libraries(test_error_handler
    error_handler_lib
)

# HTTP服务器模块单元测试
add_executable(test_http_server
    tests/test_http_server.cpp
    src/http_server.cpp
    src/logger.cpp
    src/config.cpp
    src/error_handler.cpp
)

target_link_libraries(test_http_server
    http_server_lib
    logger_lib
    config_lib
    error_handler_lib
)

# 设置输出目录
set_target_properties(test_config PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

set_target_properties(test_logger PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

set_target_properties(test_error_handler PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

set_target_properties(test_http_server PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# 阶段2.2验收测试
add_executable(test_2_2_acceptance
    tests/test_2_2_acceptance.cpp
    src/http_server.cpp
    src/logger.cpp
    src/config.cpp
    src/error_handler.cpp
)

target_link_libraries(test_2_2_acceptance
    http_server_lib
    logger_lib
    config_lib
    error_handler_lib
)

set_target_properties(test_2_2_acceptance PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

