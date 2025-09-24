import os, sys, traceback, json;

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtWebEngineCore import  QWebEngineHttpRequest, QWebEnginePage

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QHBoxLayout, QWidget, QTabWidget, QListWidget, QPushButton, QButtonGroup, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize,  QByteArray, QUrl
from PySide6.QtWebEngineCore import QWebEngineHttpRequest, QWebEnginePage

class RestHelper:
    def __init__(self):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        if os.path.exists(self.path_config):
            self.config = json.loads( open(self.path_config, "r").read() );
        else:
            self.config = None;
        self.page = None;
        self.callback = None;
    
    def post(self, url, data, callback):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        self.config = json.loads( open(self.path_config, "r").read() );
        self.callback = callback;
        data["publick_key_name"] = self.config["token"];
        url = QUrl.fromUserInput(self.config["url"] + url); # 
        #url = QUrl.fromUserInput("https://www.aied.com.br");
        print(url.toString());
        request = QWebEngineHttpRequest();
        request.setUrl( url );
        request.setMethod(QWebEngineHttpRequest.Post);
        request.setHeader(QByteArray(b'User-Agent'), QByteArray(b'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'));
        request.setHeader(QByteArray(b'Content-Type'),QByteArray(b'application/json'))
        request.setPostData(json.dumps(data).encode("utf-8")); #
        retorno = request.postData();
        self.page = QWebEnginePage();
        self.page.loadFinished.connect(self._loadFinished);
        self.page.load(request)
        print("só aguardar....");
    
    def _loadFinished(self):
        print("load finish");
        self.page.toPlainText(self.callable_text);
    
    def callable_text(self, data):
        print(data);
        self.html = data
        print("Retornou", data[:100]);
        self.callback( json.loads( data ) );
        #self.page = None;
        #self.callback = None;
