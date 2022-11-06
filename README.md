# MicroPython-DevTool
&nbsp;&nbsp;轻量化集成，协助MicroPython快捷编程调试


![image](https://user-images.githubusercontent.com/58870893/179134987-adce9ce5-733b-4643-835a-aadbc13acefd.png)


## 项目简介
&nbsp;&nbsp;本项目基于 [MicroPython](https://micropython.org/) 官网提供的SDK，提供了功能完善的 MicroPython 设备的文件管理，代码编辑，在线调试用户界面。<br>

1. 用户界面基于PySide6完成，提供了界面的designer源项目，方便用户界面的开发。
2. 基于pySerial实现串口调试通讯功能，兼容多种操作系统。
3. 提供了一个用PySide实现的代码文本编辑器，提供了代码高亮功能。
4. 提供了文件与文件夹管理功能：创建代码及目录，查看管理文件夹内的内容。
5. 项目可打包成单个可执行文件，使用方便。

## 安装本项目
### 1、直接下载已构建完成的可执行程序（Windows）：
&nbsp;&nbsp;&nbsp;&nbsp;在[这里](https://github.com/umeiko/MicroPython-DevTool/releases/tag/mpydt1.3.0)下载已构建完成.exe文件，可直接运行使用，无需额外配置。
### 2、利用python环境运行本项目
&nbsp;&nbsp;&nbsp;&nbsp;clone本项目的仓库地址

    git clone https://github.com/umeiko/MicroPython-DevTool.git
&nbsp;&nbsp;&nbsp;&nbsp;进入项目目录

    cd MicroPython-DevTool
&nbsp;&nbsp;&nbsp;&nbsp;安装需要的依赖库

    pip install -r requirments.txt
&nbsp;&nbsp;&nbsp;&nbsp;运行主程序

    python main.py


## 主要特性
&nbsp;&nbsp;&nbsp;&nbsp;主界面会列出当前运行目录与MicroPython单片机内的文件及目录，右击这些文件可以对文件进行操作。


![image](https://user-images.githubusercontent.com/58870893/179017048-b2f63cd5-69e5-47af-a812-e5b94351e491.png)


在连接到 MicroPython 单片机的情况下，可调出调试界面，实时通过串口界面对设备进行repl调试。

（ 支持 Tab【代码补全】、Ctrl+B【停止当前程序运行】）

![image](https://user-images.githubusercontent.com/58870893/170490165-a2c9ec12-24f0-48a8-abe5-393d0184afc1.png)

直接双击文件夹会进入目录，直接双击文件则会调出代码编辑器，可以直接编辑文件，退出时会自动保存。

（ 【Ctrl +】 【Ctrl -】 调整文本尺寸 ）


![image](https://user-images.githubusercontent.com/58870893/179019896-c589bb2c-55d6-4f62-a511-b11209acb763.png)
<br><br>
## 常见问题
1. 无法选择到端口，插上单片机后端口列表是空的
    - 确认连接正常，确认数据线支持数据传输，确认单片机具备串口芯片。
    - 安装对应的串口芯片驱动程序。
2. 能够看见端口，但无法选择这个端口
    - 确认这个端口 就是 单片机所对应的端口（可在设备管理器中拔插单片机确认）
    - 确认单片机中烧录了MicroPython固件 （[烧录工具](https://github.com/umeiko/ESPTOOL-GUI), [固件下载](https://micropython.org/download/)）
3. 如何打开别的文件目录
    - 试试把需要打开的文件夹直接拖到窗口里 (Windows可用，其它平台兼容性未知)
4. 已知问题
    - 合宙C3无串口芯片版，通讯时与pySerial模块有兼容性问题，会导致程序卡死
