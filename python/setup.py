"""安装脚本"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="stock-ox",
    version="0.1.0",
    description="国信证券 OX 交易 API Python 封装",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Stock OX Team",
    author_email="stock-ox-team@example.com",
    url="https://github.com/your-username/stock-ox",
    project_urls={
        "Bug Reports": "https://github.com/your-username/stock-ox/issues",
        "Source": "https://github.com/your-username/stock-ox",
        "Documentation": "https://github.com/your-username/stock-ox/tree/main/python/docs",
    },
    packages=find_packages(exclude=['tests', 'examples']),
    python_requires=">=3.7",
    install_requires=[
        # 基础依赖将在后续开发中添加
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'flake8>=5.0.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'pylint>=2.15.0',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords="stock trading api guosen securities",
    zip_safe=False,
)

