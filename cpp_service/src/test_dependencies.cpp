// 测试第三方依赖库是否可以正确编译和链接
#include "../third_party/httplib.h"
#include "../third_party/json.hpp"
#include <iostream>

using json = nlohmann::json;

int main() {
    std::cout << "Testing cpp-httplib and nlohmann/json..." << std::endl;
    
    // 测试 nlohmann/json
    json j;
    j["status"] = "success";
    j["message"] = "Dependencies test";
    j["version"] = 1.0;
    
    std::cout << "JSON test: " << j.dump(2) << std::endl;
    
    // 测试 cpp-httplib (仅创建服务器实例，不实际启动)
    httplib::Server svr;
    std::cout << "httplib Server instance created successfully" << std::endl;
    
    std::cout << "All dependencies compiled and linked successfully!" << std::endl;
    return 0;
}

