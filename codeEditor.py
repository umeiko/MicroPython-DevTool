from PySide6.QtCore import Qt, QRect, QSize, QMetaObject, QCoreApplication
from PySide6.QtWidgets import QWidget, QTextEdit, QPlainTextEdit, QTextEdit, QDialog, QGridLayout
from PySide6.QtGui import QColor, QPainter, QTextFormat, QShortcut, QIcon
from pygments import highlight
from pygments.lexers import Python3Lexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
import threading
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.css = HtmlFormatter(style="colorful").get_style_defs('.highlight')
        self.lex = Python3Lexer()
        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.codeHighlight)
        self.updateLineNumberAreaWidth(0)
        
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

        # Just to make sure I use the right font
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
            curs.setPosition(oldPos)
            self.setTextCursor(curs)
            self.textChanged.connect(self.codeHighlight)

    def codeHighliteAll(self):
        """为整个文档更新样式"""
        if self.lex is not None:
            code = self.toPlainText()
            curs = self.textCursor()
            curs.movePosition(curs.Start)
            self.textChanged.disconnect(self.codeHighlight)
            for k, i in enumerate(code.split('\n')):
                now_block = curs.block()
                content = now_block.text()
                # print(k, content)
                if content:
                    out = highlight(now_block.text(), self.lex, HtmlFormatter())
                    curs.select(curs.LineUnderCursor)
                    curs.deleteChar()
                    curs.insertHtml(f'<style type="text/css">{self.css}</style>{out}'[:-2])
                else:
                    curs.insertText('')
                curs.movePosition(curs.NextBlock)
            self.textChanged.connect(self.codeHighlight)
    
    def setCodeHighlite(self, state:bool):
        """是否启用代码高亮"""
        if state:
            self.textChanged.connect(self.codeHighlight)
        else:
            self.textChanged.disconnect(self.codeHighlight)



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
    codeEditor.QCodeEditor.setPlainText(contens)
    if len(contens) < 114514:
        codeEditor.QCodeEditor.codeHighliteAll()

    app.exec()
    codeEditor.QCodeEditor.saveFile()
    return f"File \"{fName}\" saved"

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    codeEditor = QCodeEditor()
    codeEditor.show()
    sys.exit(app.exec())
