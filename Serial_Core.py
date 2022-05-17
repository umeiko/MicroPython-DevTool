import threading
import pyboard
import serial
import serial.tools.list_ports
from PySide6.QtCore import Signal, QObject


def deal_files(input_bytes:bytes)->list:
    files = input_bytes.split(b"\n")
    out = []
    for i in files:
        if i :
            out.append(i.split()[1])
    return out

class Serial_Thread(threading.Thread, QObject):
    """串口调试助手的收信线程"""
    jump_sig = Signal()
    text_sig = Signal(str)
    err_sig  = Signal(str)
    def __init__(self, port):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.isRunning = False
        self.serial = serial.Serial(port)
        self.serial.timeout=0
        self.serial.baudrate=115200
        self.jump_last = True
    
    def run(self):
        temp = b""
        text = b""
        self.isRunning = True
        while self.isRunning:
            try:
                text = self.serial.read()
            except BaseException as e:
                self.err_sig.emit("From Thread:"+str(e))
            if text:
                temp += text
                text = b""
                try:  # 解决汉字等二进制转换的问题
                    decode_str = temp.decode(encoding="utf-8")
                    for k, i in enumerate(decode_str):
                        if i in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f":
                            decode_str = decode_str[:k] + "\\x" + temp[k:k+1].hex() + decode_str[k+1:]
                    self.text_sig.emit(decode_str)
                    temp = b""
                except BaseException as e:
                    msg = str(e).split(":")[-1]
                    if msg == " unexpected end of data":
                        if len(temp) >3:
                            decode_str = ""
                            for k, _ in enumerate(temp):
                                decode_str += "\\x" + temp[k:k+1].hex()
                            self.text_sig.emit(decode_str)
                            temp = b""
                    else:
                        decode_str = ""
                        for k, _ in enumerate(temp):
                            decode_str += "\\x" + temp[k:k+1].hex()
                        self.text_sig.emit(decode_str)
                        temp = b""
                if self.jump_last:
                    self.jump_sig.emit() 
        print("串口打印线程被终止")

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
            self.pyb.exit_raw_repl()
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
                self.pyb.exit_raw_repl()
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
    
    def write_ser(self, content):
        """写内容到串口"""
        if isinstance(content, bytes):
            content = content
        elif isinstance(content, str):
            content = content.encode()
        
        if self.pyb is not None:
            if self.pyb.in_raw_repl:
                self.pyb.exit_raw_repl()
            try:
                self.pyb.serial.write(content+b"\r\n")
            except BaseException as e:
                self.port_erro_signal.emit(str(e))
    
    