import os, sys, inspect, json;

from PySide6.QtCore import (QByteArray, QFile, QFileInfo, QSettings, QSaveFile, QTextStream, Qt, Slot)
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QMessageBox, QApplication, QFileDialog, QMainWindow, QComboBox, QMdiArea, QMessageBox, QTextEdit, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QGridLayout, QLineEdit, QPushButton)

BROWSER_PATH = os.environ["BROWSER_PATH"]

sys.path.append( BROWSER_PATH );

class FormLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(600, 320);
        self.diretorio = None;
        layout_login = QGridLayout()
        layout_login.setContentsMargins(20, 20, 20, 20)
        layout_login.setSpacing(10)
        user_login = QLabel("Username:")
        user_login.setProperty("class", "normal")
        layout_login.addWidget(user_login, 1, 0)
        self.txt_login_username = QLineEdit()
        layout_login.addWidget(self.txt_login_username, 1, 1, 1, 2)
        pwd_login = QLabel("Run this script:")
        pwd_login.setProperty("class", "normal")
        layout_login.addWidget(pwd_login, 2, 0)
        self.textEdit = QTextEdit();
        layout_login.addWidget(self.textEdit, 3, 0, 1, 3)
        self.txt_login_username.textChanged.connect(self.txt_login_username_click)
        btn_register_navegar = QPushButton("Start Browser")
        btn_register_navegar.clicked.connect(self.start_browser_click)
        layout_login.addWidget(btn_register_navegar, 4, 1)
        self.setStyleSheet(self.load_styles());
        self.setLayout(layout_login)
    def start_browser_click(self):
        if self.txt_login_username.text().strip() == "":
            print("sem path, é vazio");
            self.close();
        else:
            if os.path.exists(os.path.join("/tmp", self.txt_login_username.text() )):
                self.diretorio = os.path.join("/tmp", self.txt_login_username.text() );
                print(self.diretorio);
                self.close();
    def txt_login_username_click(self):
        self.textEdit.clear()
        self.textEdit.setPlainText("sudo /bin/bash " + BROWSER_PATH + "/bash/create.sh " + self.txt_login_username.text());

    def load_styles(self):
        return """
        * {
            font-family: Consolas;
        }
        QMainWindow {
            background-color: #0f0f0f;
            border: 2px solid #ff0000;
        }
        QTabWidget::pane {
            border: 2px solid #ff0000;
            background-color: #1a1a1a;
        }
        QTabBar::tab {
            background: #2b2b2b;
            color: #ff0000;
            padding: 10px;
            border: 1px solid #ff0000;
        }
        QTabBar::tab:selected {
            background: #ff0000;
            color: #000;
        }
        QToolBar {
            border-bottom: 2px solid black;
            border-top: 2px solid black;
            background: #ff0000;
            color: #ff0000;
        }
        QTextEdit {
            background: #121212;
            color: #ff0000;
            border: 1px solid #ff0000;
            padding: 5px;
        }
        QLineEdit {
            background: #121212;
            color: #ff0000;
            border: 1px solid #ff0000;
            padding: 5px;
        }
        QListWidget {
            background: #121212;
            color: #ff0000;
            border: 1px solid #ff0000;
        }
        """
