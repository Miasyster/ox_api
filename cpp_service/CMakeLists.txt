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

# 主服务程序（空项目测试用）
add_executable(ox_service
    src/main.cpp
)

# 链接国信OX SDK库
target_link_libraries(ox_service
    GuosenOXAPI
)

# 设置输出目录
set_target_properties(ox_service PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

