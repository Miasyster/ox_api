# Stock OX - 国信证券 OX 交易 API Python 封装

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Stock OX 是国信证券 OX 交易 API 的 Python 封装库，提供简洁易用的 Python 接口，支持现货交易、期权交易、期货交易、信用交易等。

## 特性

- ✅ **简洁易用的 API** - 提供 Pythonic 的接口，易于使用
- ✅ **完整的交易功能** - 支持下单、撤单、批量下单等
- ✅ **异步回调机制** - 支持委托回报、成交回报等回调
- ✅ **类型安全** - 使用类型注解和枚举类型
- ✅ **完善的文档** - 提供详细的使用文档和示例代码
- ✅ **高测试覆盖率** - 包含完整的单元测试和集成测试

## 功能支持

### 已实现功能

- ✅ API 初始化和登录
- ✅ 下单（限价单、市价单）
- ✅ 撤单
- ✅ 批量下单
- ✅ 委托回报和成交回报回调
- ✅ 撤单响应回调

### 待实现功能（阶段四）

- ⏳ 查询资金
- ⏳ 查询持仓
- ⏳ 查询委托
- ⏳ 查询成交明细
- ⏳ 查询股东账号

### 待实现功能（阶段五）

- ⏳ 信用交易（融资融券）
- ⏳ 期权交易
- ⏳ ETF 交易

## 安装

### 从源码安装

```bash
cd python
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

### 依赖要求

- Python 3.7+
- Windows 操作系统（DLL 文件是 Windows 专用的）

## 快速开始

### 基本使用

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
    
    # 等待回报
    import time
    time.sleep(1.0)
    
except Exception as e:
    print(f"错误: {e}")
finally:
    api.stop()
```

### 使用上下文管理器（推荐）

```python
from stock_ox import OXTradeApi

with OXTradeApi() as api:
    api.register_spi(spi)
    api.login(account, password, account_type)
    # ... 进行交易操作 ...
# API 自动停止
```

### 更多示例

查看 `examples/` 目录获取更多示例代码：
- `trading_example.py` - 完整的交易流程示例
- `order_example.py` - 下单功能示例
- `query_example.py` - 查询功能示例（待实现）

## 文档

- [快速入门指南](docs/QUICKSTART.md) - 快速开始使用 API
- [完整使用示例](docs/USAGE_EXAMPLES.md) - 详细的使用示例和代码片段
- [API 参考文档](docs/API_REFERENCE.md) - 完整的 API 参考文档
- [常见问题解答](docs/FAQ.md) - FAQ 和常见问题解答
- [示例代码](examples/) - 可运行的示例代码

## 开发

### 环境设置

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source .venv/bin/activate

# 安装依赖
pip install -r requirements-dev.txt
```

### 代码风格检查

```bash
# 使用 black 格式化代码
black stock_ox/

# 使用 flake8 检查代码
flake8 stock_ox/

# 使用 mypy 进行类型检查
mypy stock_ox/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=stock_ox --cov-report=html

# 运行特定测试
pytest tests/test_order.py -v
```

### 测试覆盖率

当前测试覆盖率：
- `api.py`: 87% 覆盖率
- `spi.py`: 79% 覆盖率
- `structs.py`: 90% 覆盖率

## 项目结构

```
python/
├── stock_ox/          # 主包
│   ├── __init__.py
│   ├── api.py         # 核心 API
│   ├── spi.py         # 回调接口
│   ├── structs.py     # 数据结构
│   ├── constants.py   # 常量定义
│   ├── types.py       # 类型枚举
│   ├── dll_loader.py  # DLL 加载器
│   ├── utils.py       # 工具函数
│   └── exceptions.py  # 异常定义
├── tests/             # 测试代码
│   ├── test_api.py
│   ├── test_order.py
│   ├── test_cancel.py
│   ├── test_batch_order.py
│   └── test_integration.py
├── examples/          # 示例代码
│   ├── trading_example.py
│   ├── order_example.py
│   └── query_example.py
├── docs/              # 文档
│   ├── QUICKSTART.md
│   ├── USAGE_EXAMPLES.md
│   ├── API_REFERENCE.md
│   └── FAQ.md
├── setup.py           # 安装脚本
└── requirements.txt   # 依赖列表
```

## 注意事项

1. **Windows 环境** - DLL 文件是 Windows 专用的，只能在 Windows 环境下运行
2. **账户信息** - 示例代码中的账户信息为测试数据，实际使用时请修改
3. **回调处理** - 回调函数是异步的，需要在回调中正确处理数据
4. **错误处理** - 始终使用 try-except 处理错误，确保在 finally 中停止 API

## 版本历史

- **v0.1.0** (2024) - 初始版本
  - 支持 API 初始化和登录
  - 支持下单、撤单、批量下单
  - 支持委托回报和成交回报回调

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 报告问题

在 GitHub 上创建 Issue，包含：
- 问题描述
- 复现步骤
- 错误信息
- 环境信息（Python 版本、操作系统等）

## 联系方式

如有问题或建议，请：
- 查看文档和示例代码
- 创建 GitHub Issue
- 查看测试代码了解使用方法

## 致谢

感谢所有贡献者和使用者的支持！

