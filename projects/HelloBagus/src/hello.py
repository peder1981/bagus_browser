import os, sys, traceback, json;

from PySide6.QtWidgets import QLayout, QMessageBox, QDialog, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QButtonGroup, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from urllib.parse import urlparse

class Hello():
    def __init__(self):
        self.page = None;
        self.html = None;
        pass;
    
    def after_render(self, page, html):
        javascript = """
            var elementos = document.getElementsByTagName('h1');
            console.log('Resultado:', elementos);
            if (elementos != null && elementos.length > 0)
                elementos[0].innerHTML = elementos[0].innerHTML + ' !!!BagusBagusGo!!!'
            """;
        page.runJavaScript(javascript);

    def before_layout(self, layout_button_group):
        self.bt1 = QPushButton("Bagus?");
        layout_button_group.addWidget(self.bt1);
        self.bt1.clicked.connect(self.bt1_click);
    def bt1_click(self):
        msgBox = QMessageBox();
        msgBox.setText("Done!!!");
        msgBox.exec();
