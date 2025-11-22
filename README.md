# Stock OX - 国信证券 OX 交易 API

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

国信证券 OX 交易 API 的完整解决方案，包含原始 C++ SDK 和 Python 封装库。

## 📋 项目概述

本项目提供了**国信证券（Guosen Securities）OX 交易 API** 的完整实现，支持：

- ✅ **现货交易** - 股票买卖、ETF 申购赎回
- ✅ **期权交易** - 期权合约交易
- ✅ **期货交易** - 期货合约交易
- ✅ **信用交易** - 融资融券业务
- ✅ **查询功能** - 资金查询、持仓查询、委托查询等

项目包含两部分：

1. **C++ SDK** - 国信证券提供的原始 SDK（包含 DLL、头文件、示例代码）
2. **Python 封装** - 使用 ctypes 封装的 Python 库，提供简洁易用的 Python 接口

## 🎯 特性

### Python 封装特性

- ✅ **简洁易用的 API** - 提供 Pythonic 的接口，易于使用
- ✅ **完整的交易功能** - 支持下单、撤单、批量下单等
- ✅ **异步回调机制** - 支持委托回报、成交回报等回调
- ✅ **类型安全** - 使用类型注解和枚举类型
- ✅ **完善的文档** - 提供详细的使用文档和示例代码
- ✅ **高测试覆盖率** - 包含完整的单元测试和集成测试（87% 覆盖率）

### C++ SDK 特性

- ✅ **完整的 API 接口** - 涵盖所有交易和查询功能
- ✅ **回调机制** - 支持异步响应和推送
- ✅ **示例代码** - 提供 C++ 使用示例
- ✅ **官方文档** - 包含 API 使用说明文档

## 📁 项目结构

```
stock_ox/
├── bin/                        # C++ SDK 运行时文件和配置
│   ├── config/                 # 配置文件目录
│   │   └── config.ini          # 用户账户配置
│   ├── LOG/                    # 日志目录
│   ├── UA/                     # UA 相关配置
│   ├── GuosenOXAPI.dll         # 核心动态库
│   ├── uaAPI.dll               # UA API 动态库
│   ├── uaAuth.dll              # UA 认证动态库
│   ├── uaCrypto.dll            # UA 加密动态库
│   ├── uaPacker.dll            # UA 打包动态库
│   └── ...
├── demo/                       # C++ SDK 示例代码
│   ├── config/                 # 示例配置文件
│   ├── main.cpp                # 主程序示例
│   ├── demo.sln                # Visual Studio 解决方案
│   └── ...
├── doc/                        # C++ SDK 文档
│   └── API使用说明.docx        # API 使用文档
├── include/                    # C++ SDK 头文件
│   ├── OXTradeApi.h            # 主 API 头文件
│   ├── OXTradeApiConst.h       # 常量定义
│   ├── OXTradeApiStruct.h      # 数据结构定义
│   └── OXTradeApiType.h        # 类型定义
├── lib/                        # C++ SDK 静态库文件
│   └── GuosenOXAPI.lib         # 核心静态库
├── python/                     # Python 封装代码
│   ├── stock_ox/               # Python 包
│   │   ├── api.py              # 核心 API 封装
│   │   ├── spi.py              # 回调接口封装
│   │   ├── structs.py          # 数据结构定义
│   │   ├── constants.py        # 常量定义
│   │   ├── types.py           # 类型枚举
│   │   ├── dll_loader.py       # DLL 加载器
│   │   ├── utils.py            # 工具函数
│   │   └── exceptions.py       # 异常定义
│   ├── tests/                  # 测试代码
│   │   ├── test_api.py         # API 测试
│   │   ├── test_order.py       # 下单功能测试
│   │   ├── test_cancel.py      # 撤单功能测试
│   │   ├── test_batch_order.py # 批量下单测试
│   │   └── test_integration.py # 集成测试
│   ├── examples/               # 示例代码
│   │   ├── trading_example.py  # 完整交易示例
│   │   ├── order_example.py    # 下单示例
│   │   └── query_example.py    # 查询示例（占位）
│   ├── docs/                   # 文档
│   │   ├── QUICKSTART.md       # 快速入门指南
│   │   ├── USAGE_EXAMPLES.md   # 完整使用示例
│   │   ├── API_REFERENCE.md    # API 参考文档
│   │   └── FAQ.md              # 常见问题解答
│   ├── setup.py                # 安装脚本
│   ├── requirements.txt        # 依赖列表
│   ├── README.md               # Python 包文档
│   ├── INSTALL.md              # 安装说明
│   ├── CHANGELOG.md            # 更新日志
│   └── RELEASE.md              # 发布说明
├── origin_readme.md            # C++ SDK 项目解析文档
├── plan.md                     # Python 封装开发计划
└── README.md                   # 本文档
```

## 🚀 快速开始

### Python 封装使用

#### 1. 安装

```bash
cd python
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

#### 2. 基本使用

```python
from stock_ox import OXTradeApi
from stock_ox.spi import OXTradeSpi
from stock_ox.types import AccountType
from stock_ox.constants import STK_BIZ_BUY, ORDER_TYPE_LIMIT, BOARD_SH

class MySpi(OXTradeSpi):
    def on_rsp_logon(self, request, error, is_last, field):
        if error:
            print(f"登录失败: {error.get('ErrorInfo', '')}")
        else:
            print(f"登录成功: Account={field.get('Account', '')}")
    
    def on_rtn_order(self, field):
        if field:
            print(f"委托回报: {field.get('Symbol', '')} x {field.get('OrderQty', 0)}")

# 创建 API 实例
api = OXTradeApi()
spi = MySpi()

try:
    # 初始化
    api.init()
    api.register_spi(spi)
    
    # 登录
    api.login(
        account="110060035050",
        password="111111",
        account_type=AccountType.STOCK,
        timeout=5.0
    )
    
    # 下单
    request_id = api.order(
        trdacct='A197407210',
        board_id=BOARD_SH,
        symbol='600000',
        price=10.50,
        quantity=100,
        stk_biz=STK_BIZ_BUY,
        stk_biz_action=ORDER_TYPE_LIMIT
    )
    print(f"下单成功，请求编号: {request_id}")
    
except Exception as e:
    print(f"错误: {e}")
finally:
    api.stop()
```

#### 3. 使用上下文管理器（推荐）

```python
with OXTradeApi() as api:
    api.register_spi(spi)
    api.login(account, password, account_type)
    # ... 进行交易操作 ...
# API 自动停止
```

### C++ SDK 使用

参考 `demo/` 目录下的示例代码和 `doc/API使用说明.docx` 文档。

## 📖 文档

### Python 封装文档

- 📘 [快速入门指南](python/docs/QUICKSTART.md) - 快速开始使用 Python API
- 📗 [完整使用示例](python/docs/USAGE_EXAMPLES.md) - 详细的使用示例和代码片段
- 📕 [API 参考文档](python/docs/API_REFERENCE.md) - 完整的 API 参考文档
- 📙 [常见问题解答](python/docs/FAQ.md) - FAQ 和常见问题解答
- 📚 [Python 包文档](python/README.md) - Python 包详细文档
- 📝 [安装说明](python/INSTALL.md) - 详细的安装指南
- 📋 [更新日志](python/CHANGELOG.md) - 版本更新历史
- 🚀 [发布说明](python/RELEASE.md) - 如何发布新版本

### C++ SDK 文档

- 📄 [C++ SDK 项目解析](origin_readme.md) - C++ SDK 完整解析文档
- 📄 [API 使用说明](doc/API使用说明.docx) - 官方 API 使用文档
- 💻 [C++ 示例代码](demo/main.cpp) - C++ 使用示例

### 开发文档

- 📋 [开发计划](plan.md) - Python 封装开发计划

## ✨ 功能支持

### Python 封装 - 已实现功能

- ✅ API 初始化和登录
- ✅ 下单（限价单、市价单）
- ✅ 撤单
- ✅ 批量下单
- ✅ 委托回报和成交回报回调
- ✅ 撤单响应回调

### Python 封装 - 待实现功能

#### 阶段四（查询功能）

- ⏳ 查询资金
- ⏳ 查询持仓
- ⏳ 查询委托
- ⏳ 查询成交明细
- ⏳ 查询股东账号

#### 阶段五（高级功能）

- ⏳ 信用交易（融资融券）
- ⏳ 期权交易
- ⏳ ETF 交易

### C++ SDK 功能

C++ SDK 支持所有功能，包括：

- ✅ 所有交易功能
- ✅ 所有查询功能
- ✅ 信用交易功能
- ✅ 期权交易功能
- ✅ ETF 交易功能

## 🔧 系统要求

### Python 封装

- **操作系统**: Windows 7 或更高版本（32 位或 64 位）
- **Python**: Python 3.7 或更高版本
- **依赖**: 无外部依赖（仅使用 Python 标准库）

### C++ SDK

- **操作系统**: Windows
- **编译器**: Visual Studio 2015 或更高版本
- **运行时**: Windows SDK

## 📦 安装

### Python 封装安装

详细安装说明请参考 [INSTALL.md](python/INSTALL.md)。

#### 从源码安装

```bash
cd python
pip install -e .
```

#### 从 PyPI 安装（计划中）

```bash
pip install stock-ox
```

## 🧪 测试

### 运行测试

```bash
cd python

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=stock_ox --cov-report=html

# 运行特定测试
pytest tests/test_order.py -v
```

### 测试覆盖率

当前测试覆盖率：

- `api.py`: **87%** 覆盖率
- `spi.py`: **79%** 覆盖率
- `structs.py`: **90%** 覆盖率

## 📊 项目状态

### Python 封装开发进度

- ✅ **阶段一**: 环境准备和基础框架（已完成）
- ✅ **阶段二**: 核心 API 和登录功能（已完成）
- ✅ **阶段三**: 交易功能（下单、撤单、批量下单）（已完成）
- ⏳ **阶段四**: 查询功能（进行中）
- ⏳ **阶段五**: 高级功能（信用交易、期权、ETF）（计划中）
- ✅ **阶段六**: 测试和文档（已完成）
- ✅ **阶段七**: 打包发布（已完成）

详细进度请参考 [plan.md](plan.md)。

## 🛠️ 开发

### 开发环境设置

```bash
cd python

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 代码质量工具

```bash
# 代码格式化
black stock_ox/ tests/

# 代码检查
flake8 stock_ox/ tests/

# 类型检查
mypy stock_ox/

# 代码分析
pylint stock_ox/
```

### 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 版本历史

详细版本历史请参考 [CHANGELOG.md](python/CHANGELOG.md)。

### v0.1.0 (当前版本)

- ✅ 核心交易功能（下单、撤单、批量下单）
- ✅ 基础回调机制
- ✅ 完整的测试和文档

## ⚠️ 注意事项

1. **Windows 环境** - DLL 文件是 Windows 专用的，只能在 Windows 环境下运行
2. **账户信息** - 示例代码中的账户信息为测试数据，实际使用时请修改为您的账户信息
3. **回调处理** - 回调函数是异步的，需要在回调中正确处理数据
4. **错误处理** - 始终使用 try-except 处理错误，确保在 finally 中停止 API

## 📄 许可证

MIT License

## 👥 贡献者

感谢所有贡献者！

## 📞 联系方式

如有问题或建议，请：

- 📝 创建 GitHub Issue
- 📖 查看文档和示例代码
- 💬 查看常见问题解答：[FAQ.md](python/docs/FAQ.md)

## 🔗 相关链接

- [Python 包文档](python/README.md)
- [快速入门指南](python/docs/QUICKSTART.md)
- [API 参考文档](python/docs/API_REFERENCE.md)
- [完整使用示例](python/docs/USAGE_EXAMPLES.md)
- [开发计划](plan.md)

## 🙏 致谢

感谢国信证券提供的 OX 交易 API SDK。

---

**Stock OX Team** - 让证券交易更简单

