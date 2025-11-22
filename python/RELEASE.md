# 发布说明

本文档说明了如何创建和发布 stock_ox 的新版本。

## 发布前准备

### 1. 更新版本号

#### 在 `stock_ox/__init__.py` 中更新版本号

```python
__version__ = "0.1.0"  # 更新为新的版本号
```

#### 在 `setup.py` 中更新版本号

```python
version="0.1.0",  # 更新为新的版本号
```

### 2. 更新 CHANGELOG.md

在 `CHANGELOG.md` 顶部添加新版本条目：

```markdown
## [0.2.0] - 2024-XX-XX

### 新增功能
- ...

### 修复
- ...

### 变更
- ...
```

### 3. 运行测试

确保所有测试通过：

```bash
cd python
pytest tests/ -v
```

### 4. 检查代码质量

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

### 5. 更新文档

- 检查 README.md 是否需要更新
- 检查文档是否是最新的
- 确保示例代码可以运行

## 构建发布包

### 1. 清理之前的构建

```bash
cd python
rm -rf build/ dist/ *.egg-info/
```

### 2. 构建源码包和 Wheel 包

```bash
python setup.py sdist bdist_wheel
```

这将创建：
- `dist/stock_ox-0.1.0.tar.gz` - 源码包
- `dist/stock_ox-0.1.0-py3-none-any.whl` - Wheel 包

### 3. 检查构建的包

```bash
# 检查包内容
tar -tzf dist/stock_ox-0.1.0.tar.gz

# 检查 Wheel 包
unzip -l dist/stock_ox-0.1.0-py3-none-any.whl
```

## 发布到 PyPI（测试）

### 1. 安装 twine

```bash
pip install twine
```

### 2. 上传到 PyPI 测试服务器

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

需要提供 PyPI 测试账户的用户名和密码。

### 3. 测试安装

```bash
pip install --index-url https://test.pypi.org/simple/ stock-ox
```

## 发布到 PyPI（正式）

### 1. 验证包

```bash
twine check dist/*
```

### 2. 上传到 PyPI

```bash
twine upload dist/*
```

需要提供 PyPI 账户的用户名和密码（或 API token）。

### 3. 验证发布

访问 https://pypi.org/project/stock-ox/ 查看包是否已发布。

## 创建 Git 标签

### 1. 提交更改

```bash
git add .
git commit -m "Release version 0.1.0"
```

### 2. 创建标签

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
```

### 3. 推送标签

```bash
git push origin v0.1.0
```

## 创建 GitHub Release

1. 访问 GitHub 仓库的 Releases 页面
2. 点击 "Draft a new release"
3. 选择刚才创建的标签（v0.1.0）
4. 填写发布标题和描述（可以从 CHANGELOG.md 复制）
5. 上传构建的包文件（可选）
6. 点击 "Publish release"

## 发布后任务

### 1. 更新文档

- 更新项目网站（如果有）
- 更新 README.md 中的版本信息

### 2. 通知用户

- 发布公告（如果有邮件列表或论坛）
- 更新项目状态

### 3. 监控反馈

- 监控 GitHub Issues
- 收集用户反馈
- 准备下一个小版本的修复

## 版本号规则

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号（MAJOR）**：不兼容的 API 修改
- **次版本号（MINOR）**：向后兼容的功能性新增
- **修订号（PATCH）**：向后兼容的问题修正

### 版本号示例

- `0.1.0` - 初始版本
- `0.1.1` - 修复 bug
- `0.2.0` - 新增功能（查询功能）
- `1.0.0` - 稳定版本
- `1.0.1` - 修复 bug
- `1.1.0` - 新增功能（信用交易）
- `2.0.0` - 重大变更（不兼容的 API 修改）

## 发布检查清单

发布前请确认：

- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] 所有测试通过
- [ ] 代码质量检查通过
- [ ] 文档已更新
- [ ] 示例代码可以运行
- [ ] 构建包成功
- [ ] 包验证通过
- [ ] Git 标签已创建
- [ ] GitHub Release 已创建

## 自动化发布（计划中）

未来可以配置 GitHub Actions 自动：
1. 运行测试
2. 构建包
3. 发布到 PyPI
4. 创建 GitHub Release

## 获取帮助

如有问题，请：
- 查看 PyPI 文档：https://packaging.python.org/
- 查看 twine 文档：https://twine.readthedocs.io/
- 创建 GitHub Issue

