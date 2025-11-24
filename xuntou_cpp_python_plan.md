# 迅投量化交易完整流程计划（C++中间服务 + Python客户端）

## 目标
搭建一个完整的量化交易系统，通过迅投 C++ SDK 提供下单和行情功能，由 Python 客户端负责策略逻辑，实现自动化交易。

---

## 系统架构

```
+----------------+       HTTP/gRPC        +------------------+       SDK调用      +----------------+
| Python客户端   | --------------------> | C++中间服务      | ----------------> | 迅投C++ SDK     |
| (策略 &风控)  | <-------------------- | (REST/gRPC API)  | <---------------- | (下单 &行情)   |
+----------------+                        +------------------+                  +----------------+
```

### 组成模块
1. **Python客户端**
   - 策略逻辑
   - 风控控制
   - 自动下单触发
   - 日志记录 & 监控

2. **C++中间服务**
   - 提供 HTTP/gRPC 接口
   - 接收下单和行情请求
   - 调用迅投 C++ SDK 执行操作
   - 返回执行结果

3. **迅投 C++ SDK**
   - 提供账户初始化、行情获取、下单、撤单等功能

---

## 开发计划

### 1. C++中间服务开发

**1.1 环境准备**
- 安装 C++17 编译器
- 安装依赖库：
  - REST: Crow / cpp-httplib / Pistache
  - JSON: nlohmann/json
- 链接迅投 C++ SDK

**1.2 服务功能**
- 初始化账户
- 下单接口
- 查询订单接口
- 查询实时行情接口
- 可选: 撤单接口

**1.3 服务示例接口**
```http
POST /init
{
  "api_key": "xxx",
  "api_secret": "xxx",
  "account_id": "xxx"
}

POST /order
{
  "symbol": "600519",
  "side": "buy",
  "quantity": 100,
  "price": 2500.0
}

GET /quote?symbol=600519
```

**1.4 返回示例**
```json
{
  "status": "success",
  "order_id": "123456",
  "message": "Order placed successfully"
}
```

**1.5 部署**
- Linux: 使用 systemd 或 Docker 部署服务
- Windows: 直接可执行程序或 Windows Service

---

### 2. Python客户端开发

**2.1 环境准备**
```bash
pip install requests pandas numpy
```

**2.2 模块功能**
- 数据获取: 调用 C++服务 / 行情接口
- 策略生成: 信号计算
- 风控: 仓位控制、单日亏损限制
- 下单: 调用 C++服务下单接口
- 日志 & 监控: 本地日志 + 邮件/微信通知

**2.3 样例代码**
```python
import requests

BASE_URL = "http://127.0.0.1:5000"

# 获取行情
resp = requests.get(f"{BASE_URL}/quote", params={"symbol":"600519"})
quote = resp.json()
price = quote['last_price']

# 风控判断
if price < 3000:  # 简单示例
    order = requests.post(f"{BASE_URL}/order", json={
        "symbol":"600519",
        "side":"buy",
        "quantity":100,
        "price":price
    })
    print(order.json())
```

**2.4 自动化执行**
- Linux: `cron` 每分钟/每小时运行
- Windows: Task Scheduler 定时任务

---

### 3. 风控与监控
- 单日最大亏损控制
- 仓位上限控制
- 异常报警（Python发送邮件/微信）
- 日志记录每笔下单和返回状态

---

### 4. 测试计划
1. **服务独立测试**：使用 Postman 或 curl 测试 C++ 服务接口
2. **Python客户端测试**：使用模拟信号或历史行情回测下单逻辑
3. **全流程测试**：Python策略 -> C++服务 -> SDK下单 -> 返回结果

---

### 5. 部署计划
1. 部署 C++ 中间服务（服务器 / Docker）
2. 配置 Python客户端定时任务
3. 启动监控日志系统
4. 初始小资金回测下单

---

### 6. 扩展功能
- 多策略、多账户支持
- gRPC 替代 HTTP 提升性能
- 数据缓存与行情加速
- 风控策略可动态配置

---

**备注**：所有 API 需严格控制频率，遵循券商/迅投接口限制，确保安全和稳定。