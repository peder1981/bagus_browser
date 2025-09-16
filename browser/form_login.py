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
                if not os.path.exists( os.path.join( self.diretorio, "default" ) ):
                    os.makedirs( os.path.join( self.diretorio, "default" ) );
                self.close();
    
    def txt_login_username_click(self):
        self.textEdit.clear()
        self.textEdit.setPlainText("sudo /bin/bash " + BROWSER_PATH + "/bash/create.sh " + self.txt_login_username.text());

    def load_styles(self):
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();
