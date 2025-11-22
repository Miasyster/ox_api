# 安装说明

本文档提供了 stock_ox 的详细安装说明。

## 系统要求

### 操作系统

- **Windows** (必需)
  - Windows 7 或更高版本
  - 32 位或 64 位系统
  - DLL 文件只能在 Windows 环境下加载

### Python 版本

- **Python 3.7 或更高版本**
  - Python 3.7
  - Python 3.8
  - Python 3.9
  - Python 3.10
  - Python 3.11
  - Python 3.12

### 依赖项

当前版本没有外部依赖（仅使用 Python 标准库）。

## 安装方法

### 方法一：从源码安装（推荐）

#### 1. 克隆或下载项目

```bash
git clone https://github.com/your-username/stock-ox.git
cd stock-ox/python
```

或者下载 ZIP 文件并解压。

#### 2. 安装包

```bash
# 基础安装
pip install -e .

# 安装开发依赖（推荐）
pip install -e ".[dev]"
```

#### 3. 验证安装

```bash
python -c "from stock_ox import OXTradeApi; print('安装成功！')"
```

### 方法二：从 PyPI 安装（计划中）

一旦包发布到 PyPI，可以使用以下命令安装：

```bash
pip install stock-ox
```

### 方法三：从 Wheel 文件安装

如果提供了 Wheel 文件（`.whl`），可以使用：

```bash
pip install stock_ox-0.1.0-py3-none-any.whl
```

## 开发环境设置

### 1. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac（注意：实际只能在 Windows 上运行）
python -m venv .venv
source .venv/bin/activate
```

### 2. 安装开发依赖

```bash
pip install -r requirements-dev.txt
```

开发依赖包括：
- `pytest>=7.0.0` - 测试框架
- `pytest-cov>=4.0.0` - 测试覆盖率
- `flake8>=5.0.0` - 代码检查
- `black>=23.0.0` - 代码格式化
- `mypy>=1.0.0` - 类型检查
- `pylint>=2.15.0` - 代码分析

### 3. 验证开发环境

```bash
# 运行测试
pytest

# 检查代码风格
flake8 stock_ox/

# 格式化代码
black stock_ox/
```

## DLL 文件配置

### 1. DLL 文件位置

DLL 文件应该位于项目根目录的 `bin/` 目录下：

```
stock-ox/
├── bin/
│   ├── GuosenOXAPI.dll       # 主 DLL 文件
│   ├── config/
│   │   └── config.ini        # 配置文件
│   └── ...                   # 其他 DLL 文件
└── python/
    └── stock_ox/
        └── ...
```

### 2. 自动查找 DLL

API 会自动查找 DLL 文件，查找顺序：
1. 指定的 DLL 路径（如果提供）
2. 相对于项目根目录的 `bin/GuosenOXAPI.dll`
3. 相对于当前工作目录的 `bin/GuosenOXAPI.dll`

### 3. 手动指定 DLL 路径

```python
from stock_ox import OXTradeApi

# 指定 DLL 路径
api = OXTradeApi(dll_path="C:/path/to/GuosenOXAPI.dll")
api.init()
```

## 配置文件

### 配置文件位置

配置文件位于：`bin/config/config.ini`

### 配置文件内容

```ini
# 账户配置
acct=110060035050
password=111111
acct_type=3

# 股东账号配置
sh_trade_account=A197407210
sz_trade_account=0000035074
```

**注意：** 实际使用时，请修改为您的账户信息，不要将密码硬编码在代码中。

## 快速测试

### 1. 基本功能测试

```python
from stock_ox import OXTradeApi

try:
    api = OXTradeApi()
    api.init()
    print("✓ API 初始化成功")
    api.stop()
except Exception as e:
    print(f"✗ 错误: {e}")
```

### 2. 运行示例代码

```bash
cd python
python examples/trading_example.py
```

### 3. 运行测试套件

```bash
cd python
pytest tests/ -v
```

## 常见安装问题

### 问题 1: DLL 加载失败

**错误信息：**
```
OXDllError: Failed to load DLL
```

**解决方法：**
1. 确认 DLL 文件存在
2. 确认 DLL 文件路径正确
3. 确认在 Windows 环境下运行
4. 检查 DLL 文件是否损坏

### 问题 2: 模块导入失败

**错误信息：**
```
ModuleNotFoundError: No module named 'stock_ox'
```

**解决方法：**
1. 确认已正确安装包
2. 确认虚拟环境已激活
3. 使用 `pip install -e .` 重新安装

### 问题 3: 依赖项缺失

**错误信息：**
```
ImportError: No module named 'xxx'
```

**解决方法：**
```bash
pip install -r requirements-dev.txt
```

### 问题 4: 权限错误

**错误信息：**
```
PermissionError: [Errno 13] Permission denied
```

**解决方法：**
1. 以管理员身份运行
2. 检查文件和目录权限
3. 使用虚拟环境

## 卸载

### 卸载包

```bash
pip uninstall stock-ox
```

### 清理虚拟环境

```bash
# 删除虚拟环境
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows
```

## 升级

### 升级到新版本

```bash
# 从源码升级
cd python
git pull
pip install -e . --upgrade

# 从 PyPI 升级（计划中）
pip install stock-ox --upgrade
```

## 验证安装

### 检查版本

```python
from stock_ox import __version__
print(f"stock_ox 版本: {__version__}")
```

### 检查功能

```python
from stock_ox import OXTradeApi
from stock_ox.types import AccountType
from stock_ox.constants import BOARD_SH, STK_BIZ_BUY

# 检查所有模块是否正常导入
print("✓ 所有模块导入成功")

# 检查 API 类是否可用
api = OXTradeApi()
print(f"✓ API 类创建成功: {type(api)}")
```

## 获取帮助

如果遇到安装问题：

1. 查看 [常见问题解答](docs/FAQ.md)
2. 查看 [快速入门指南](docs/QUICKSTART.md)
3. 创建 GitHub Issue
4. 查看示例代码：`examples/` 目录

## 下一步

安装完成后，请查看：

- [快速入门指南](docs/QUICKSTART.md) - 开始使用 API
- [完整使用示例](docs/USAGE_EXAMPLES.md) - 查看详细示例
- [API 参考文档](docs/API_REFERENCE.md) - 完整的 API 文档

