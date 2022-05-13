from mainWindow import Ui_MainWindow
import Serial_Core
from PySide6 import QtCore
from PySide6.QtGui import QIcon, QShortcut,QAction,QCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QListWidgetItem, QMenu
import sys
import os


main_window = Ui_MainWindow() # 主界面
app = QApplication(sys.argv)
w = QMainWindow()
main_window.setupUi(w)
serial_manager = Serial_Core.Serial_Manager()

global_options = {
    "temp_ports_list": [],
    "last_port"      : 0,
    "skin_mode"      : "Classic",
}

def init_methods():
    fresh_PC_files()
    load_options()


def close_methods(*args):
    save_options()


def bind_methods():
    """为组件绑定功能"""
    serial_manager.port_erro_signal.connect(func_for_serial_erro)
    serial_manager.fresh_signal.connect(func_for_fresh_MCU_files)
    main_window.port_select.mousePressEvent = func_for_show_ports
    main_window.port_select.currentIndexChanged.connect(func_for_select_port) 
    main_window.port_select.wheelEvent=lambda *args: None
    main_window.MCU_files.customContextMenuRequested.connect(create_right_menu_MCU)
    main_window.PC_files.customContextMenuRequested.connect(create_right_menu_PC)
    main_window.restart_MCU.clicked.connect(serial_manager.reboot)

def func_for_show_ports(*args):
    """展示串口的函数"""
    fresh_ports()
    print(global_options)
    main_window.port_select.showPopup()

def fresh_ports():
    """刷新系统当前连接的串口设备"""
    global main_window
    main_window.port_select.setItemText(0, "断开连接")
    ports, names = serial_manager.scan_ports()

    for k, i in enumerate(global_options["temp_ports_list"]):
        # 删除已不存在的端口
        if i not in ports:
            main_window.port_select.removeItem(k+1)
            if global_options["temp_ports_list"]:
                global_options["temp_ports_list"].pop(k)
    
    for k, i in enumerate(names):
        # 添加新出现的端口
        if ports[k] not in global_options["temp_ports_list"]:
            main_window.port_select.addItem(i)
            if global_options["temp_ports_list"]:
                global_options["temp_ports_list"].append(ports[k])
    if not global_options["temp_ports_list"]:
        global_options["temp_ports_list"] = ports

def func_for_select_port(*args):
    """选择连接到某个串口"""
    index = args[0]
    main_window.statusBar.showMessage(f'连接{global_options["temp_ports_list"][index-1]}')
    if index > 0:
        serial_manager.open_port(global_options["temp_ports_list"][index-1])
    else:
        serial_manager.close_port()
    global_options["last_port"] = index
    
def create_right_menu_MCU():
    """右键菜单"""
    menu   = QMenu()
    action_1 = QAction(text="下载到本地")
    action_1.triggered.connect(lambda:file_transport("MCU", main_window.MCU_files.currentItem().text()))
    menu.addAction(action_1)
    action_2 = QAction(text="删除")
    action_2.triggered.connect(lambda:remove_file("MCU", main_window.MCU_files.currentItem().text()))
    menu.addAction(action_2)
    menu.exec(QCursor.pos())
    print(main_window.MCU_files.currentItem().text())

def create_right_menu_PC():
    """右键菜单"""
    menu   = QMenu()
    action_1 = QAction(text="上传到单片机")
    action_1.triggered.connect(lambda:file_transport("PC", main_window.PC_files.currentItem().text()))
    menu.addAction(action_1)
    action_2 = QAction(text="删除")
    action_2.triggered.connect(lambda:remove_file("PC", main_window.PC_files.currentItem().text()))
    menu.addAction(action_2)
    menu.exec(QCursor.pos())

def save_options():
    """导出主窗口的配置到文件中"""
    import json as json
    with open("main_config.json", 'w') as js_file:
        js_string = json.dumps(global_options, sort_keys=True, indent=4, separators=(',', ': '))
        js_file.write(js_string)

def func_for_serial_erro(*args):
    """串口异常处理的函数"""
    serial_manager.close_port()
    main_window.port_select.setItemText(0, "连接失败, 请重试")
    main_window.port_select.setCurrentIndex(0)
    main_window.statusBar.showMessage(args[0])

def func_for_fresh_MCU_files(lst:list):
    """刷新单片机内的文件"""
    main_window.MCU_files.clear()
    for i in lst:
        a = QListWidgetItem()
        a.setText(i.decode())
        main_window.MCU_files.addItem(a)
    main_window.MCU_files.setCurrentRow(0)

def fresh_PC_files():
    """刷新电脑的文件"""
    main_window.PC_files.clear()
    for i in os.listdir():
        if os.path.isfile(i):
            a = QListWidgetItem()
            a.setText(i)
            main_window.PC_files.addItem(a)
    main_window.PC_files.setCurrentRow(0)

def file_transport(device:str, file_name:str):
    """传输文件"""
    if serial_manager.pyb is not None:
        if device == "PC":
            try:
                serial_manager.pyb.fs_put(file_name, file_name)
                serial_manager.fresh_files()
            except Exception as e:
                func_for_serial_erro(str(e))
        elif device == "MCU":
            try:
                serial_manager.pyb.fs_get(file_name, file_name)
                fresh_PC_files()
            except Exception as e:
                func_for_serial_erro(str(e))
    else:
        main_window.statusBar.showMessage("未连接！传输无效")

def remove_file(device:str, file_name:str):
    """删除文件"""
    if device == "PC":
        os.remove(file_name)
        fresh_PC_files()
    elif device == "MCU":
        if serial_manager.pyb is not None:
            try:
                serial_manager.pyb.fs_rm(file_name)
                serial_manager.fresh_files()
            except Exception as e:
                func_for_serial_erro(str(e))
        else:
            main_window.statusBar.showMessage("未连接！删除无效")

def load_options():
    global global_options
    import json as json
    try:
        with open("main_config.json", 'r') as js_file:
            temp_robo_options = json.load(js_file)
    except BaseException as e:
        with open("main_config.json", 'w') as js_file:
            js_string = json.dumps(global_options, sort_keys=True, indent=4, separators=(',', ': '))
            js_file.write(js_string)
        temp_robo_options = global_options.copy()

def main():
    bind_methods()
    init_methods()
    w.closeEvent = close_methods
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()