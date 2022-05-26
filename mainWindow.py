# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)
import rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(555, 414)
        icon = QIcon()
        icon.addFile(u":/ROOT/1.ico", QSize(), QIcon.Normal, QIcon.On)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.PC_files = QListWidget(self.groupBox)
        icon1 = QIcon()
        icon1.addFile(u":/ROOT/icons/txt.ico", QSize(), QIcon.Normal, QIcon.Off)
        __qlistwidgetitem = QListWidgetItem(self.PC_files)
        __qlistwidgetitem.setIcon(icon1);
        self.PC_files.setObjectName(u"PC_files")
        self.PC_files.setContextMenuPolicy(Qt.CustomContextMenu)

        self.gridLayout.addWidget(self.PC_files, 0, 0, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.MCU_files = QListWidget(self.groupBox_2)
        QListWidgetItem(self.MCU_files)
        self.MCU_files.setObjectName(u"MCU_files")
        self.MCU_files.setContextMenuPolicy(Qt.CustomContextMenu)

        self.gridLayout_2.addWidget(self.MCU_files, 0, 0, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.port_select = QComboBox(self.centralwidget)
        self.port_select.addItem("")
        self.port_select.setObjectName(u"port_select")
        self.port_select.setMinimumSize(QSize(150, 0))

        self.horizontalLayout_2.addWidget(self.port_select)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.port_exec = QPushButton(self.centralwidget)
        self.port_exec.setObjectName(u"port_exec")
        self.port_exec.setMinimumSize(QSize(90, 0))

        self.horizontalLayout_2.addWidget(self.port_exec)

        self.restart_MCU = QPushButton(self.centralwidget)
        self.restart_MCU.setObjectName(u"restart_MCU")
        self.restart_MCU.setEnabled(True)
        self.restart_MCU.setMinimumSize(QSize(90, 0))
        self.restart_MCU.setCheckable(False)
        self.restart_MCU.setFlat(False)

        self.horizontalLayout_2.addWidget(self.restart_MCU)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        self.restart_MCU.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MicroPython\u6587\u4ef6\u52a9\u624b", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"PC\u6587\u4ef6", None))

        __sortingEnabled = self.PC_files.isSortingEnabled()
        self.PC_files.setSortingEnabled(False)
        ___qlistwidgetitem = self.PC_files.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u9879\u76ee", None));
        self.PC_files.setSortingEnabled(__sortingEnabled)

        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u5355\u7247\u673a\u5185\u6587\u4ef6", None))

        __sortingEnabled1 = self.MCU_files.isSortingEnabled()
        self.MCU_files.setSortingEnabled(False)
        ___qlistwidgetitem1 = self.MCU_files.item(0)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u9879\u76ee", None));
        self.MCU_files.setSortingEnabled(__sortingEnabled1)

        self.port_select.setItemText(0, QCoreApplication.translate("MainWindow", u"\u65ad\u5f00\u8fde\u63a5", None))

        self.port_exec.setText(QCoreApplication.translate("MainWindow", u"\u547d\u4ee4\u884c\u8c03\u8bd5", None))
        self.restart_MCU.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u542f\u5355\u7247\u673a", None))
    # retranslateUi

