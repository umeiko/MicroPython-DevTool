from tkinter import EXCEPTION
import pyboard
import serial
import serial.tools.list_ports
from PySide6.QtCore import Signal, QObject



def deal_files(input_bytes:bytes):
    files = input_bytes.split(b"\n")
    out = []
    for i in files:
        if i :
            out.append(i.split()[1])
    return out

class Serial_Manager(QObject):
    pyb = None
    port_erro_signal = Signal(str)
    fresh_signal     = Signal(list)
    def __init__(self) -> None:
        QObject.__init__(self)

    def scan_ports(self)->tuple:
        """查询有哪些串口可用, 返回两个列表"""
        options = serial.tools.list_ports.comports()
        ports = [i.device for i in options]
        names = [i.description for i in options]
        return ports, names
    
    def open_port(self, port:str):
        """打开串口, 并尝试读取内部的文件"""
        files = []
        try:
            if self.pyb is not None:
                self.close_port()
            self.pyb = pyboard.Pyboard(port)
            self.pyb.enter_raw_repl()
            files = deal_files(self.pyb.fs_ls("", False))
        except Exception as e:
            self.port_erro_signal.emit(str(e))
        self.fresh_signal.emit(files)

    def fresh_files(self):
        """刷新串口内容的内部文件"""
        files = []
        try:
            if self.pyb is not None:
                self.pyb.enter_raw_repl()
                files = deal_files(self.pyb.fs_ls("", False))
        except Exception as e:
            self.port_erro_signal.emit(str(e))
        self.fresh_signal.emit(files)
    
    def reboot(self):
        try:
            if self.pyb is not None:
                self.pyb.exit_raw_repl()
                self.pyb.serial.write(b"from machine import reset\r\n")
                self.pyb.serial.write(b"reset()\r\n")
        except Exception as e:
            self.port_erro_signal.emit(str(e))

    def close_port(self):
        """关闭串口"""
        if self.pyb is not None:
            self.pyb.close()
            self.pyb = None
            self.fresh_signal.emit([])
    
    