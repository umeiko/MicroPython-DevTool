# MicroPython-DevTool
&nbsp;&nbsp;轻量化集成，协助MicroPython快捷编程调试

## 项目简介
&nbsp;&nbsp;本项目基于 MicroPython 官网提供的SDK，提供了功能完善的 MicroPython 设备的文件管理，代码编辑，在线调试用户界面。<br>

1. 用户界面基于PySide6完成，提供了界面的designer源项目，方便用户界面的开发。
2. 基于pySerial实现串口调试通讯功能，兼容多种操作系统。
3. 提供了一个用Pyside实现的代码文本编辑器，提供了代码高亮功能。
4. 提供了文件与文件夹管理功能：创建代码及目录，查看管理文件夹内的内容。
5. 项目可打包成单个可执行文件，使用方便。

## 安装本项目
### 1、直接下载已构建完成的可执行程序（Windows）：
&nbsp;&nbsp;&nbsp;&nbsp;在[这里](https://github.com/umeiko/MicroPython-DevTool/releases/tag/mpydt1.3.0)下载已构建完成.exe文件，可直接运行使用，无需额外配置。
### 2、利用python环境运行本项目
&nbsp;&nbsp;&nbsp;&nbsp;clone本项目的仓库地址

    git clone https://github.com/umeiko/MicroPython-DevTool.git
&nbsp;&nbsp;&nbsp;&nbsp;安装需要的依赖库

    pip install -r requirments.txt
&nbsp;&nbsp;&nbsp;&nbsp;运行主程序

    python main.py


## 主要特性
&nbsp;&nbsp;&nbsp;&nbsp;主界面会列出当前运行目录与MicroPython单片机内的文件及目录，右击这些文件可以对文件进行操作。

![image](https://user-images.githubusercontent.com/58870893/170489860-74f274b7-83ed-415c-a5db-948518faa883.png)

简单上传下载

![image](https://user-images.githubusercontent.com/58870893/168427809-52abb129-84a6-41ab-8411-997472b20d69.png)
![image](https://user-images.githubusercontent.com/58870893/168427818-9e27c9e7-6493-4735-9579-ef517c66eac8.png)

调试程序，支持Tab自动补全代码

![image](https://user-images.githubusercontent.com/58870893/170490165-a2c9ec12-24f0-48a8-abe5-393d0184afc1.png)

双击直接打开并编辑代码,支持代码高亮

(Ctrl +) (Ctrl -) 调整文本尺寸，退出自动保存

![D1HDST}KDAEJ4H} V`~Z8E](https://user-images.githubusercontent.com/58870893/173001527-6e189802-9a08-435f-abba-303f6eebaeeb.png)
