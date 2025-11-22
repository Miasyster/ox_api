# Stock OX - 国信证券 OX 交易 API Python 封装

## 简介

Stock OX 是国信证券 OX 交易 API 的 Python 封装库，提供简洁易用的 Python 接口，支持：

- 现货交易
- 期权交易
- 期货交易
- 信用交易（融资融券）
- ETF 交易
- 各种查询功能

## 安装

```bash
# 从源码安装
cd python
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

## 快速开始

```python
from stock_ox import OXTradeApi, AccountType

# 创建 API 实例
api = OXTradeApi()

# 初始化
api.init()

# 登录
api.login(account="110060035050", password="111111", account_type=AccountType.STOCK)

# 使用 API...
```

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

# 使用 pylint 检查代码
pylint stock_ox/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=stock_ox --cov-report=html
```

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
├── examples/          # 示例代码
├── setup.py           # 安装脚本
└── requirements.txt   # 依赖列表
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

