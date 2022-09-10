"""
本模块提供了一个代码编辑器, 刷新代码高亮格式的线程, 以及简易的用户单行文本交互窗口。
"""
import threading
import time
from PySide6.QtCore import Qt, QRect, QSize, QMetaObject, QCoreApplication, Signal
from PySide6.QtWidgets import QWidget, QTextEdit, QPlainTextEdit, QTextEdit, QDialog, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QColor, QPainter, QTextFormat, QShortcut, QIcon, QCursor, QKeyEvent
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
    def __init__(self, parent=None, lex=Python3Lexer()):
        super().__init__(parent)
        self.css = HtmlFormatter(style="colorful").get_style_defs('.highlight')
        self.lex = lex
        self.now_editing_line = 0
        self.setUndoRedoEnabled(False)
        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.codeHighlight)      # 
        self.Line_sig.connect(self.codeHighlightLineIter) # 在线程中调用信号来控制文档更新
        self.initCursor = self.textCursor() # 用于迭代刷新高亮格式的文本操作符 
        self.updateLineNumberAreaWidth(0)
        self.setTabStopDistance(40)
        self.runningInit = True             # 线程状态，文件退出前需结束线程
        self.closeLock = threading.Lock()   # 线程锁，保证文件退出时的安全

        self.fName = None
        sZoomIn = QShortcut(self)
        sZoomIn.setKey(u'Ctrl+=')
        sZoomIn.activated.connect(self.zoomIn)
        sZoomOut = QShortcut(self)
        sZoomOut.setKey(u'Ctrl+-')
        sZoomOut.activated.connect(self.zoomOut)
        
        sDelTab = QShortcut(self)
        sDelTab.setKey(u'Shift+Tab')
        sDelTab.activated.connect(self.deTabMultiLine)

        sComment = QShortcut(self)
        sComment.setKey(u'Ctrl+/')
        sComment.activated.connect(self.commentMultiLine)
        
        sSave = QShortcut(self)
        sSave.setKey(u'Ctrl+s')
        sSave.activated.connect(self.saveFile)

        # 重载键盘事件
        self.oldKeyEvent = self.keyPressEvent
        self.keyPressEvent = self.newKeyEvents
    
    def newKeyEvents(self, k:QKeyEvent):
        """重载键盘事件, 改写某些输入按键的功能"""
        # print(k.keyCombination().key())
        if k.keyCombination().key() == Qt.Key.Key_Tab:
            self.tabMultiLine()
        else:
            self.oldKeyEvent(k)

    def tabMultiLine(self):
        """一次性给多行添加缩进"""
        curs = self.textCursor()
        start_index = curs.selectionStart()
        end_index = curs.selectionEnd()
        if start_index != end_index:
            original_texts = curs.selection().toPlainText()
            curs.setPosition(end_index)
            curs.movePosition(curs.EndOfBlock)
            end_index = curs.position()
            curs.setPosition(start_index)
            curs.movePosition(curs.StartOfBlock)
            select_start = curs.position()
            curs.insertText("\t")
            self.codeHighlight(curs)
            temp = 1
            for k, i in enumerate(original_texts):
                if i == "\n":
                    curs.setPosition(start_index+temp+k+1)
                    temp += 1
                    curs.insertText("\t")
                    self.codeHighlight(curs)
            # 选中多行
            curs.setPosition(select_start, curs.MoveAnchor)
            curs.setPosition(end_index+temp, curs.KeepAnchor)
            self.setTextCursor(curs)
        else:
            curs.insertText("\t")

    def deTabMultiLine(self):
        """一次性取消多行的缩进"""
        curs = self.textCursor()
        start_index = curs.selectionStart()
        end_index = curs.selectionEnd()
        curs.setPosition(end_index)
        curs.movePosition(curs.EndOfBlock)
        end_index = curs.position()
        curs.setPosition(start_index)
        curs.movePosition(curs.StartOfLine)
        start_index = curs.position()
        curs.setPosition(start_index, curs.MoveAnchor)
        curs.setPosition(end_index, curs.KeepAnchor)
        original_texts = curs.selection().toPlainText()
        atLineStart = True
        temp = 0
        for k, i in enumerate(original_texts):
            if atLineStart and i == "\t":
                curs.setPosition(start_index+temp+k, curs.MoveAnchor)
                curs.deleteChar()
                temp -= 1
                self.codeHighlight(curs)
            if i == "\n":
                atLineStart = True
            else:
                atLineStart = False
        # 选中多行
        curs.setPosition(start_index, curs.MoveAnchor)
        curs.setPosition(end_index+temp, curs.KeepAnchor)
        self.setTextCursor(curs)

    def commentMultiLine(self):
        """一次性注释多行"""
        curs = self.textCursor()
        start_index = curs.selectionStart()
        end_index = curs.selectionEnd()
        curs.setPosition(end_index)
        curs.movePosition(curs.EndOfBlock)
        end_index = curs.position()
        curs.setPosition(start_index)
        curs.movePosition(curs.StartOfLine)
        start_index = curs.position()
        curs.setPosition(start_index, curs.MoveAnchor)
        curs.setPosition(end_index, curs.KeepAnchor)
        original_texts = curs.selection().toPlainText()
        curs.setPosition(start_index, curs.MoveAnchor)
        # 判断是加注释还是消除注释        
        add_comment = False
        for i in original_texts.splitlines():
            if not i.startswith("#"):
                add_comment = True
                break
        if add_comment:
            curs.movePosition(curs.StartOfBlock)
            curs.insertText("#")
            self.codeHighlight(curs)
            temp = start_index + 1
            for k, i in enumerate(original_texts):
                if i == "\n":
                    curs.setPosition(start_index+temp+k+1)
                    temp += 1
                    curs.insertText("#")
                    self.codeHighlight(curs)
        else:
            curs.movePosition(curs.StartOfBlock)
            curs.deleteChar()
            self.codeHighlight(curs)
            temp = start_index - 1
            for k, i in enumerate(original_texts):
                if i == "\n":
                    curs.setPosition(start_index+temp+k+1)
                    curs.deleteChar()
                    temp -= 1
                    self.codeHighlight(curs)
        # 选中多行
        curs.setPosition(start_index, curs.MoveAnchor)
        curs.setPosition(end_index+temp, curs.KeepAnchor)
        self.setTextCursor(curs)
        

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

    def codeHighlight(self, curser=None):
        """获取正在编辑的这行, 更新该行的样式"""
        if self.lex is not None:
            if curser is None:
                curs = self.textCursor()
            else:
                curs = curser
            now_block = curs.block()
            oldPos = curs.position()
            self.textChanged.disconnect(self.codeHighlight)
            out = highlight(now_block.text(), self.lex, HtmlFormatter())
            curs.select(curs.LineUnderCursor)
            # print(f"-{now_block.text()}-{curs.selectedText()}-{out}\\")
            if now_block.text() and (curs.selectedText() == now_block.text()):
                curs.deleteChar()
                curs.insertHtml(f'<style type="text/css">{self.css}</style>{out}'[:-2])
            elif self.now_editing_line != now_block.blockNumber():
                pre_block = now_block.previous()
                k = 0
                for i in pre_block.text():
                    if i not in (" ", "\t"):
                        break
                    k += 1
                indented_blocks = pre_block.text()[:k]
                if pre_block.text().endswith(":"):
                    indented_blocks += "\t"
                out = indented_blocks
                oldPos += len(indented_blocks)
                curs.insertText(out)
            curs.setPosition(oldPos)
            self.setTextCursor(curs)
            self.textChanged.connect(self.codeHighlight)
            self.now_editing_line = now_block.blockNumber()
    
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


def get_user_rename(default_text:str="",hint_text:str="")->str:
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
    gridLayout.setContentsMargins(1, 1, 1, 1)
    redialog.setWindowFlag(Qt.FramelessWindowHint)
    redialog.move(QCursor.pos())
    Lin = QLineEdit(redialog)
    Lin.setText(default_text)
    if hint_text: 
        Label = QLabel(redialog)
        Label.setText(hint_text)
        gridLayout.addWidget(Label, 0, 0, 1, 1)
        gridLayout.addWidget(Lin, 1, 0, 1, 1)
    else:
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
