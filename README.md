# SmartUSBHub 系统服务

此软件包提供了一个系统服务，封装了 SmartUSBHub 的功能，允许不同进程通过标准化的 RESTful API 与 SmartUSBHub 设备进行交互。

## 功能特性

- 自动设备发现和连接
- 用于控制 SmartUSBHub 的 RESTful API
- 通过 HTTP 请求实现多进程访问
- 针对 Ubuntu 的 systemd 服务集成
- 简单的安装和卸载过程

## 安装

1. 确保您的系统已安装 Python 3 和 pip。

2. 使用 sudo 运行安装脚本：

   ```bash
   sudo ./install_service.sh
   ```

   此脚本将：
   - 在 `/opt/smartusbhub` 创建服务目录
   - 将必要文件复制到服务目录
   - 安装 Python 依赖项
   - 创建并启用 systemd 服务
   - 启动服务

## 使用方法

安装完成后，服务将运行并通过 HTTP 请求访问。服务提供以下 API 端点：

### 获取设备信息

```
GET http://localhost:80891/device/info
```

返回连接的 SmartUSBHub 设备的信息。

### 获取通道电源状态

```
GET http://localhost:80891/channel/power/{channel}
```

返回指定通道（1-4）的电源状态。

### 设置通道电源状态

```
POST http://localhost:80891/channel/power?channels={channels}&state={state}
```

设置一个或多个通道的电源状态。
- `channels`：以逗号分隔的通道号列表（1-4）
- `state`：0 表示关闭，1 表示开启

### 获取通道数据线状态

```
GET http://localhost:80891/channel/dataline/{channel}
```

返回指定通道（1-4）的数据线状态。

### 设置通道数据线状态

```
POST http://localhost:80891/channel/dataline?channels={channels}&state={state}
```

设置一个或多个通道的数据线状态。
- `channels`：以逗号分隔的通道号列表（1-4）
- `state`：0 表示断开连接，1 表示连接

## 示例

```bash
# 获取设备信息
curl http://localhost:80891/device/info

# 获取通道 1 的电源状态
curl http://localhost:80891/channel/power/1

# 开启通道 1 和 2
curl -X POST "http://localhost:80891/channel/power?channels=1,2&state=1"

# 关闭通道 3
curl -X POST "http://localhost:80891/channel/power?channels=3&state=0"

# 获取通道 1 的数据线状态
curl http://localhost:80891/channel/dataline/1

# 断开通道 2 的数据线连接
curl -X POST "http://localhost:80891/channel/dataline?channels=2&state=0"
```

## 服务管理

SmartUSBHub 服务通过 systemd 进行管理：

```bash
# 检查服务状态
sudo systemctl status smartusbhub.service

# 启动服务
sudo systemctl start smartusbhub.service

# 停止服务
sudo systemctl stop smartusbhub.service

# 重启服务
sudo systemctl restart smartusbhub.service

# 查看服务日志
sudo journalctl -u smartusbhub.service -f
```

## 卸载

要卸载服务，请使用 sudo 运行卸载脚本：

```bash
sudo ./uninstall_service.sh
```

此脚本将：
- 如果服务正在运行则停止服务
- 禁用 systemd 服务
- 删除服务文件
- 删除服务目录

## 手动安装

如果您希望手动安装服务：

1. 为服务创建目录：
   ```bash
   sudo mkdir -p /opt/smartusbhub
   ```

2. 复制必要文件：
   ```bash
   sudo cp smartusbhub_service.py /opt/smartusbhub/
   sudo cp smartusbhub.py /opt/smartusbhub/
   ```

3. 安装 Python 依赖项：
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip
   sudo pip3 install pyserial
   ```

4. 创建 systemd 服务文件：
   ```bash
   sudo cp smartusbhub.service /etc/systemd/system/
   ```

5. 重新加载 systemd 并启动服务：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable smartusbhub.service
   sudo systemctl start smartusbhub.service
   ```

## 直接脚本使用

您也可以直接运行服务脚本，而无需将其安装为 systemd 服务：

```bash
python3 smartusbhub_service.py --help

# 使用默认设置运行
python3 smartusbhub_service.py

# 使用自定义设置运行
python3 smartusbhub_service.py --port /dev/ttyUSB0 --host 0.0.0.0 --http-port 80891
```

## API 客户端示例

以下是一个简单的 Python 示例，展示如何与服务交互：

```python
import requests

# 获取设备信息
response = requests.get('http://localhost:80891/device/info')
print(response.json())

# 开启通道 1
response = requests.post('http://localhost:80891/channel/power?channels=1&state=1')
print(response.json())

# 获取通道 1 的电源状态
response = requests.get('http://localhost:80891/channel/power/1)
print(response.json())
```