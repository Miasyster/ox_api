# 第三方依赖库

本目录包含项目使用的第三方单头文件库。

## 依赖库列表

### 1. cpp-httplib
- **文件**: `httplib.h`
- **版本**: 最新版本（从GitHub master分支获取）
- **用途**: HTTP服务器和客户端库
- **GitHub**: https://github.com/yhirose/cpp-httplib
- **使用方式**: 直接包含 `#include "httplib.h"`

### 2. nlohmann/json
- **文件**: `json.hpp`
- **版本**: 最新版本（从GitHub develop分支获取）
- **用途**: JSON解析和序列化
- **GitHub**: https://github.com/nlohmann/json
- **使用方式**: 直接包含 `#include "json.hpp"`，然后使用 `using json = nlohmann::json;`

## 更新依赖库

如果需要更新依赖库，可以运行以下命令：

```powershell
# 更新 cpp-httplib
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/yhirose/cpp-httplib/master/httplib.h" -OutFile "httplib.h"

# 更新 nlohmann/json
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nlohmann/json/develop/single_include/nlohmann/json.hpp" -OutFile "json.hpp"
```

## 验证

运行测试程序验证依赖库是否正确集成：

```bash
cd build
cmake ..
cmake --build . --config Release
.\bin\Release\test_dependencies.exe
```

