import threading
import time
from PySide6.QtCore import Qt, QRect, QSize, QMetaObject, QCoreApplication, Signal
from PySide6.QtWidgets import QWidget, QTextEdit, QPlainTextEdit, QTextEdit, QDialog, QGridLayout, QLineEdit
from PySide6.QtGui import QColor, QPainter, QTextFormat, QShortcut, QIcon, QCursor

from pygments import highlight
from pygments.lexers import Python3Lexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
import rc


class QLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class QCodeEditor(QPlainTextEdit):
    Line_sig = Signal()   
    def __init__(self, parent=None):
        super().__init__(parent)
        self.css = HtmlFormatter(style="colorful").get_style_defs('.highlight')
        self.lex = Python3Lexer()
        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.codeHighlight)      # 
        self.Line_sig.connect(self.codeHighlightLineIter) # 在线程中调用信号来控制文档更新
        self.initCursor = self.textCursor() # 用于跌代刷新高亮格式的文本操作符 
        self.updateLineNumberAreaWidth(0)
        self.runningInit = True           # 线程状态，文件退出前需结束线程
        self.closeLock = threading.Lock() # 线程锁，保证文件退出时的安全

        self.fName = None
        sZoomIn = QShortcut(self)
        sZoomIn.setKey(u'Ctrl+=')
        sZoomIn.activated.connect(self.zoomIn)
        sZoomOut = QShortcut(self)
        sZoomOut.setKey(u'Ctrl+-')
        sZoomOut.activated.connect(self.zoomOut)
        
        sSave = QShortcut(self)
        sSave.setKey(u'Ctrl+s')
        sSave.activated.connect(self.saveFile)
        

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance(f"{digits}", 10) * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(150,150,150).lighter(130)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(120,120,120))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
    
    def saveFile(self):
        """保存文档"""
        if self.fName is not None:
            with open(self.fName, "w", encoding="utf-8") as f:
                f.write(self.toPlainText())
    

    def codeHighlight(self):
        """获取正在编辑的这行, 更新该行的样式"""
        if self.lex is not None:
            curs = self.textCursor()
            now_block = curs.block()
            oldPos = curs.position()
            self.textChanged.disconnect(self.codeHighlight)
            out = highlight(now_block.text(), self.lex, HtmlFormatter())
            curs.select(curs.LineUnderCursor)
            curs.deleteChar()
            curs.insertHtml(f'<style type="text/css">{self.css}</style>{out}'[:-2])
            # print(f'<style type="text/css">{self.css}</style>{out}'[:-1])
            curs.setPosition(oldPos)
            self.setTextCursor(curs)
            self.textChanged.connect(self.codeHighlight)
    
    def codeHighlightLineIter(self):
        """通过迭代刷新整个文档代码高亮的函数"""
        if self.lex is not None:
            self.closeLock.acquire()
            self.textChanged.disconnect(self.codeHighlight)
            nowblock = self.initCursor.block()
            content = nowblock.text()
            if content:
                if not self.initCursor.atStart():
                    self.initCursor.insertText('\n')
                out = highlight(content, self.lex, HtmlFormatter())
                self.initCursor.select(self.initCursor.BlockUnderCursor)
                self.initCursor.deleteChar()
                self.initCursor.insertHtml(f'<style type="text/css">{self.css}</style>{out}'[:-2])
            self.initCursor.movePosition(self.initCursor.NextBlock)
            self.textChanged.connect(self.codeHighlight)
            self.closeLock.release()
    
    def codeHighliteAll(self):        
        """刷新显示界面"""
        time.sleep(0.1)
        self.initCursor = self.textCursor()
        for _ in range(self.blockCount()):
            self.Line_sig.emit()
            time.sleep(0.001)
            if not self.runningInit:
                break
        
    def codeHighliteAllThread(self):
        """启用线程在后台刷新代码高亮效果"""
        import threading
        thr = threading.Thread(target=self.codeHighliteAll)
        thr.start()

    def setCodeHighlite(self, state:bool):
        """是否启用代码高亮"""
        if state:
            self.textChanged.connect(self.codeHighlight)
        else:
            self.textChanged.disconnect(self.codeHighlight)
        
    def close(self, event):
        """安全地退出编辑器"""
        self.runningInit = False
        self.closeLock.acquire()



class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(800, 800)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)        
        self.QCodeEditor = QCodeEditor(Dialog)
        self.QCodeEditor.setObjectName(u"QCodeEditor")
        self.gridLayout.addWidget(self.QCodeEditor, 0, 0, 1, 1)
        self.retranslateUi(Dialog)
        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))


def open_file(fName:str):
    try:
        with open(fName, "r", encoding="utf-8") as f:
            contens = f.read()
    except BaseException as e:
        return str(e)
    
    app = QDialog()
    codeEditor = Ui_Dialog()
    codeEditor.setupUi(app)
    app.setWindowTitle(fName)
    icon = QIcon()
    icon.addFile(u":/ROOT/1.ico", QSize(), QIcon.Normal, QIcon.On)
    app.setWindowIcon(icon)
    if fName.split(".")[-1] != "py":
        try:
            codeEditor.QCodeEditor.lex = guess_lexer_for_filename(fName, "")
        except:
            codeEditor.QCodeEditor.lex = None
    codeEditor.QCodeEditor.fName = fName
    codeEditor.QCodeEditor.zoomIn(5)
    codeEditor.QCodeEditor.setCodeHighlite(False)
    codeEditor.QCodeEditor.setPlainText(contens)
    codeEditor.QCodeEditor.setCodeHighlite(True)
    codeEditor.QCodeEditor.codeHighliteAllThread()
    app.closeEvent = codeEditor.QCodeEditor.close
    app.exec()
    
    codeEditor.QCodeEditor.saveFile()
    return f"File \"{fName}\" saved"


def get_user_rename(default_text:str="")->str:
    """弹出一个小窗口, 让用户输入字符, 并返回这个字符"""
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
    Lin.setText(default_text)
    gridLayout.addWidget(Lin, 0, 0, 1, 1)
    Lin.selectAll()
    redialog.exec()
    return Lin.text()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    codeEditor = QCodeEditor()
    codeEditor.show()
    sys.exit(app.exec())
