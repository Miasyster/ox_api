# 国信证券OX API C++中间服务

基于国信证券OX C++ SDK的HTTP中间服务，提供RESTful API接口供Python客户端调用。

## 项目结构

```
cpp_service/
├── src/                      # 源代码目录
│   ├── main.cpp              # 服务入口
│   ├── api_handler.cpp       # HTTP请求处理
│   ├── ox_wrapper.cpp        # 国信OX SDK包装
│   ├── ox_spi.cpp            # 回调处理类
│   └── config.cpp            # 配置管理
├── include/                   # 头文件目录
│   ├── api_handler.h
│   ├── ox_wrapper.h
│   └── config.h
├── third_party/               # 第三方依赖库
│   ├── httplib.h             # cpp-httplib HTTP库
│   ├── json.hpp              # nlohmann/json JSON库
│   └── README.md             # 依赖库说明文档
├── config/                    # 配置文件目录
│   └── service_config.json    # 服务配置文件
├── tests/                     # 测试代码目录
├── logs/                      # 日志文件目录
├── build/                     # 构建输出目录（由CMake生成）
├── CMakeLists.txt            # CMake构建配置文件
└── .gitignore                # Git忽略文件配置
```

## 依赖要求

- **C++17编译器**：Visual Studio 2019+ 或 GCC 7+
- **CMake**：3.12+
- **第三方库**：
  - `cpp-httplib`：HTTP服务器和客户端库（单头文件）
  - `nlohmann/json`：JSON解析和序列化库（单头文件）
- **国信OX SDK**：
  - `GuosenOXAPI.lib`：SDK静态库
  - `GuosenOXAPI.dll`：SDK动态库
  - 头文件位于 `../include/`

## 构建说明

### 使用CMake构建

```bash
# 创建构建目录
mkdir build
cd build

# 配置项目
cmake ..

# 编译（Release模式）
cmake --build . --config Release

# 可执行文件位于 build/bin/Release/
```

### 使用Visual Studio

```bash
# 生成Visual Studio项目文件
cd build
cmake .. -G "Visual Studio 17 2022"

# 使用Visual Studio打开 build/ox_trading_service.sln
```

## 配置说明

配置文件位于 `config/service_config.json`，包含以下配置项：

- 服务器配置（端口、线程数等）
- OX SDK配置（DLL路径、配置文件路径等）
- 日志配置（日志级别、日志文件路径等）

## API接口

服务提供以下RESTful API接口：

- `POST /api/v1/init` - 初始化账户
- `POST /api/v1/order` - 下单
- `POST /api/v1/cancel` - 撤单
- `GET /api/v1/balance` - 查询资金
- `GET /api/v1/positions` - 查询持仓
- `GET /api/v1/orders` - 查询委托
- `GET /api/v1/filled_details` - 查询成交明细
- `GET /api/v1/health` - 健康检查

详细API文档请参考项目根目录的 `execute_plan.md`。

## 开发状态

- ✅ 环境准备与项目搭建
- ✅ 第三方依赖库集成
- ⏳ 基础框架开发（进行中）
- ⏳ SDK包装层开发
- ⏳ HTTP API接口实现

## 许可证

本项目基于国信证券OX SDK开发，请遵循相关SDK的使用许可。

