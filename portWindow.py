# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'portWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTextBrowser, QVBoxLayout, QWidget)
import rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(559, 405)
        icon = QIcon()
        icon.addFile(u":/ROOT/1.ico", QSize(), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sendingTextEdit = QLineEdit(Dialog)
        self.sendingTextEdit.setObjectName(u"sendingTextEdit")
        self.sendingTextEdit.setMinimumSize(QSize(300, 30))

        self.horizontalLayout.addWidget(self.sendingTextEdit)

        self.Sending = QPushButton(Dialog)
        self.Sending.setObjectName(u"Sending")
        self.Sending.setMinimumSize(QSize(80, 30))

        self.horizontalLayout.addWidget(self.Sending)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.recv_Text = QTextBrowser(Dialog)
        self.recv_Text.setObjectName(u"recv_Text")

        self.verticalLayout.addWidget(self.recv_Text)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")

        self.horizontalLayout_2.addLayout(self.horizontalLayout_4)

        self.stopRun = QPushButton(Dialog)
        self.stopRun.setObjectName(u"stopRun")

        self.horizontalLayout_2.addWidget(self.stopRun)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        self.AutoLast = QRadioButton(Dialog)
        self.AutoLast.setObjectName(u"AutoLast")
        self.AutoLast.setMinimumSize(QSize(120, 0))
        self.AutoLast.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_3.addWidget(self.AutoLast)

        self.Clear = QPushButton(Dialog)
        self.Clear.setObjectName(u"Clear")
        self.Clear.setMinimumSize(QSize(80, 30))
        self.Clear.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.Clear)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u901a\u4fe1\u8c03\u8bd5", None))
        self.Sending.setText(QCoreApplication.translate("Dialog", u"\u53d1\u9001", None))
#if QT_CONFIG(shortcut)
        self.Sending.setShortcut(QCoreApplication.translate("Dialog", u"Enter", None))
#endif // QT_CONFIG(shortcut)
        self.stopRun.setText(QCoreApplication.translate("Dialog", u"\u505c\u6b62\u8fd0\u884c", None))
        self.AutoLast.setText(QCoreApplication.translate("Dialog", u"\u81ea\u52a8\u8f6c\u5230\u884c\u5c3e", None))
#if QT_CONFIG(shortcut)
        self.AutoLast.setShortcut(QCoreApplication.translate("Dialog", u"Ctrl+A", None))
#endif // QT_CONFIG(shortcut)
        self.Clear.setText(QCoreApplication.translate("Dialog", u"\u6e05\u7a7a", None))
#if QT_CONFIG(shortcut)
        self.Clear.setShortcut(QCoreApplication.translate("Dialog", u"Del", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

