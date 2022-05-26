from mainWindow import Ui_MainWindow
from portWindow import Ui_Dialog
import codeEditor
import Serial_Core

from PySide6.QtGui import QIcon, QShortcut, QAction,QCursor
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QListWidgetItem, QMenu, QLabel, QLineEdit, QGridLayout
import sys
import os


main_window = Ui_MainWindow() # 主界面
port_dialog = Ui_Dialog()

app = QApplication(sys.argv)
w_p = QDialog()
w = QMainWindow()
main_window.setupUi(w)
port_dialog.setupUi(w_p)
serial_manager = Serial_Core.Serial_Manager()
Cursor = port_dialog.recv_Text.textCursor()
serial_thread = None

global_options = {
    "temp_ports_list": [],
    "last_port"      : 0,
    "skin_mode"      : "Classic",
    "PC_PATH"        : ".\\",
    "Now_Focus"      : "PC"
}

supported_file_types = (".txt", ".py", ".json", 
                        ".yaml", ".c", ".h", 
                        ".ino", ".cpp", ".ui", 
                        ".csv", ".bat", ".md")

def init_methods():
    """启动函数"""
    fresh_PC_files()
    func_for_fresh_MCU_files([])

def close_methods(*args):
    pass


def bind_methods():
    """为组件绑定功能"""
    # 主界面
    serial_manager.port_erro_signal.connect(func_for_serial_erro)
    serial_manager.fresh_signal.connect(func_for_fresh_MCU_files)
    main_window.port_select.mousePressEvent = func_for_show_ports
    main_window.port_select.currentIndexChanged.connect(func_for_select_port) 
    main_window.port_select.wheelEvent=lambda *args: None
    main_window.MCU_files.customContextMenuRequested.connect(create_right_menu_MCU)
    main_window.MCU_files.itemDoubleClicked.connect(lambda x: open_file("MCU", x.text()))
    main_window.PC_files.customContextMenuRequested.connect(create_right_menu_PC)
    main_window.PC_files.itemDoubleClicked.connect(lambda x: open_file("PC", x.text()))
    main_window.restart_MCU.clicked.connect(serial_manager.reboot)
    main_window.port_exec.clicked.connect(func_open_port_dialog)
   
    # 串口调试工具
    port_dialog.Sending.clicked.connect(func_for_send_serial_msg)
    port_dialog.Clear.clicked.connect(port_dialog.recv_Text.clear)
    port_dialog.AutoLast.toggled.connect(func_jump_to_last_line)
    port_dialog.stopRun.clicked.connect(lambda: serial_thread.serial.write(b"\r\x03\x03"))
    port_dialog.rebootMCU.clicked.connect(lambda: serial_thread.serial.write(b"from machine import reset\r\nreset()\r\n"))
    w_p.rejected.connect(func_for_close_port_dialog)
    w_p.closeEvent = func_for_close_port_dialog

    # 其它设置
    shortcut_rename = QShortcut(w)
    shortcut_rename.setKey(u'F2')
    shortcut_rename.activated.connect(lambda: rename_file(main_window.PC_files.currentItem().text()))
    
    shortcut_send = QShortcut(w_p)
    shortcut_send.setKey(u'Return')
    shortcut_send.activated.connect(func_for_send_serial_msg)
    shortcut_TAB = QShortcut(w_p)
    shortcut_TAB.setKey(u'Tab')
    shortcut_TAB.activated.connect(func_for_auto_complete)
    labelWeb = QLabel()
    labelWeb.setText(
        '''<a style="font-family: 微软雅黑; color: #0000FF; font-size: 10pt;  text-decoration: none" href="https://github.com/umeiko/MicroPython-FileManager"> 关于本项目</a>'''
    )
    labelWeb.setOpenExternalLinks(True)
    main_window.statusBar.addPermanentWidget(labelWeb, stretch=0)


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

def create_right_menu_PC():
    """右键菜单"""
    menu   = QMenu()
    action_1 = QAction(text="上传到单片机")
    action_1.triggered.connect(lambda:file_transport("PC", main_window.PC_files.currentItem().text()))
    menu.addAction(action_1)

    action_3 = QAction(text="刷新")
    action_3.triggered.connect(fresh_PC_files)
    menu.addAction(action_3)

    action_4 = QAction(text="重命名")
    action_4.triggered.connect(lambda: rename_file(main_window.PC_files.currentItem().text()))
    menu.addAction(action_4)

    action_2 = QAction(text="删除")
    action_2.triggered.connect(lambda:remove_file("PC", main_window.PC_files.currentItem().text()))
    menu.addAction(action_2)
    menu.exec(QCursor.pos())

def func_for_send_serial_msg(*args):
    """发送串口信息的函数"""
    global serial_thread
    msg = port_dialog.sendingTextEdit.text()
    serial_thread.serial.write(msg.encode()+b"\r")
    port_dialog.sendingTextEdit.clear()

def func_for_auto_complete(*args):
    '''命令行代码补全函数'''
    global serial_thread
    msg = port_dialog.sendingTextEdit.text()
    serial_thread.serial.write(msg.encode()+b"\t")
    port_dialog.sendingTextEdit.clear()   

def func_jump_to_last_line(*args):
    """跳到最后一行的函数"""
    if serial_thread is not None:
        if args:
            serial_thread.jump_last = args[0]
        port_dialog.recv_Text.setTextCursor(Cursor)

def func_open_port_dialog(*args):
    """打开调试工具的函数"""
    global serial_thread, Cursor
    if serial_manager.pyb is not None:
        serial_manager.pyb.close()
        index = global_options["last_port"]
        port = global_options["temp_ports_list"][index-1]
        serial_thread = Serial_Core.Serial_Thread(port)
        serial_thread.text_sig.connect(Cursor.insertText)
        serial_thread.err_sig.connect(func_for_serial_erro)
        serial_thread.jump_sig.connect(func_jump_to_last_line)
        serial_thread.start()
        w_p.exec()

def func_for_close_port_dialog(*args):
    """关闭串口小部件时运行的函数"""
    global serial_thread
    serial_thread.isRunning = False
    serial_thread.serial.close()
    index = global_options["last_port"]
    port = global_options["temp_ports_list"][index-1]
    serial_manager.open_port(port)

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
        icon = QIcon()
        _, ext = split_file_name(i.decode())
        icon.addFile(f":/ROOT/icons/{ext[1:]}.ico", QSize(), QIcon.Normal, QIcon.Off)
        a.setIcon(icon)
        main_window.MCU_files.addItem(a)
    main_window.MCU_files.setCurrentRow(0)

def fresh_PC_files():
    """刷新电脑的文件"""
    print(global_options["PC_PATH"])
    main_window.PC_files.clear()
    files   = []
    folders = []
    if global_options["PC_PATH"] != ".\\":
        folders.append("..\\")
    for f in os.listdir(global_options["PC_PATH"]):
        i = global_options["PC_PATH"] + f
        if not i.endswith(".exe"):
            if os.path.isfile(i):
                files.append(f)
            else:
                folders.append(f)
    for i in folders:
        a = QListWidgetItem()
        a.setText(i)
        icon = QIcon()
        _, ext = split_file_name(i)
        icon.addFile(f":/ROOT/icons/folder.svg", QSize(), QIcon.Normal, QIcon.Off)
        a.setIcon(icon)
        main_window.PC_files.addItem(a)
    for i in files:   
        a = QListWidgetItem()
        a.setText(i)
        icon = QIcon()
        _, ext = split_file_name(i)
        if ext in supported_file_types:
            icon.addFile(f":/ROOT/icons/{ext[1:]}.ico", QSize(), QIcon.Normal, QIcon.Off)
        else:
            icon.addFile(f":/ROOT/icons/txt.ico", QSize(), QIcon.Normal, QIcon.Off)
        a.setIcon(icon)
        main_window.PC_files.addItem(a)
    main_window.PC_files.setCurrentRow(0)

def file_transport(device:str, file_name:str, out_name:str=None):
    """传输文件 源文件设备 文件名 另存名"""
    if out_name is None:
        out_name = file_name
    if serial_manager.pyb is not None:
        if device == "PC":
            if os.path.isdir(global_options["PC_PATH"] + file_name):
                main_window.statusBar.showMessage("不支持传输文件夹")
                return None
            if not file_name.endswith(supported_file_types):
                main_window.statusBar.showMessage("不支持传输该文件类型")
            try:
                serial_manager.pyb.enter_raw_repl()
                serial_manager.pyb.fs_put(global_options["PC_PATH"] + file_name, out_name)
                serial_manager.fresh_files()
                main_window.statusBar.showMessage(f"已传输{file_name}")
            except Exception as e:
                func_for_serial_erro(str(e))
        elif device == "MCU":
            try:
                if os.path.exists(global_options["PC_PATH"] + file_name):
                    main_window.statusBar.showMessage(f"本地文件{file_name}被替换")
                else:
                    main_window.statusBar.showMessage(f"下载文件{file_name}到本地")
                serial_manager.pyb.enter_raw_repl()
                serial_manager.pyb.fs_get(file_name, global_options["PC_PATH"] + out_name)
                serial_manager.fresh_files()
                fresh_PC_files()
            except Exception as e:
                func_for_serial_erro(str(e))
    else:
        main_window.statusBar.showMessage("未连接！传输无效")

def remove_file(device:str, file_name:str):
    """删除文件"""
    if device == "PC":
        if os.path.isdir(global_options["PC_PATH"] + file_name):
            main_window.statusBar.showMessage(f"不支持删除文件夹")
        else:
            os.remove(global_options["PC_PATH"] + file_name)
            fresh_PC_files()
    elif device == "MCU":
        if serial_manager.pyb is not None:
            try:
                serial_manager.pyb.enter_raw_repl()
                serial_manager.pyb.fs_rm(file_name)
                serial_manager.fresh_files()
                main_window.statusBar.showMessage(f"已删除{file_name}")
            except Exception as e:
                func_for_serial_erro(str(e))
        else:
            main_window.statusBar.showMessage("未连接！删除无效")

def open_file(device:str, file_name:str):
    """打开文件"""
    if device == "PC":
        if file_name == "..\\":
            go_pre_folder()
        elif os.path.isdir(global_options["PC_PATH"] + file_name):
            open_folder(file_name)
        elif file_name.endswith(supported_file_types):
            main_window.statusBar.showMessage(codeEditor.open_file(global_options["PC_PATH"]+file_name))
        else:
            main_window.statusBar.showMessage("不支持打开的文件类型")
    elif device == "MCU":
        try:
            file_transport("MCU", file_name, "_"+file_name)
            main_window.statusBar.showMessage(codeEditor.open_file(global_options["PC_PATH"]+"_"+file_name))
            file_transport("PC", "_"+file_name, file_name)
            remove_file("PC", "_"+file_name)
        except Exception as e:
            func_for_serial_erro(str(e))

def rename_file(file_name):
    """弹出一个小窗口重命名文件"""
    if os.path.isdir(global_options["PC_PATH"]+file_name):
        main_window.statusBar.showMessage(f"不支持重命名文件夹")
        return None
    fName, fType = split_file_name(file_name)
    redialog = QDialog()    
    shortcut = QShortcut(redialog)
    shortcut.setKey(u'Return')
    shortcut.activated.connect(lambda: redialog.close())
    shortcut2 = QShortcut(redialog)
    shortcut2.setKey(u'Enter')
    shortcut2.activated.connect(lambda: redialog.close())
    gridLayout = QGridLayout(redialog)
    gridLayout.setSpacing(0)
    gridLayout.setObjectName(u"gridLayout")
    gridLayout.setContentsMargins(0, 0, 0, 0)
    redialog.setWindowFlag(Qt.FramelessWindowHint)
    redialog.move(QCursor.pos())
    Lin = QLineEdit(redialog)
    Lin.setText(fName)
    gridLayout.addWidget(Lin, 0, 0, 1, 1)
    redialog.exec()
    after_name = Lin.text()
    if not os.path.exists(global_options["PC_PATH"]+after_name+fType):
        os.rename(global_options["PC_PATH"]+file_name, global_options["PC_PATH"]+after_name+fType)
        main_window.statusBar.showMessage(f"{file_name}->{after_name+fType}")
    else:
        main_window.statusBar.showMessage(f"{global_options['PC_PATH']+after_name+fType} already exists.")
    fresh_PC_files()

def split_file_name(file:str):
    """得到文件名与后缀分离的结果"""
    out = ""
    str_list = file.split(".")
    for i in str_list[:-1]:
        out += i
    return out, "."+str_list[-1]

def go_pre_folder():
    """返回上一级文件夹"""
    global global_options
    if global_options["PC_PATH"] == ".\\":
        return None
    nowPath = ""
    for i in global_options["PC_PATH"].split("\\")[:-2]:
        nowPath += i + "\\"
    global_options["PC_PATH"] = nowPath
    fresh_PC_files()

def open_folder(folder:str):
    """进入文件夹"""
    global global_options
    global_options["PC_PATH"] += folder + "\\"
    fresh_PC_files()

def main():
    bind_methods()
    init_methods()
    w.closeEvent = close_methods
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()