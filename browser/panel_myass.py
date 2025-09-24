import tldextract, sys, uuid, json, os, importlib, requests, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QTextEdit, QHBoxLayout, QWidget, QTabWidget, QListWidget, QPushButton, QButtonGroup, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize,  QByteArray, QUrl
from PySide6.QtWebEngineCore import QWebEngineHttpRequest, QWebEnginePage

from browser.ui.table import *
from browser.api.rest_helper import *

class PanelMyass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        #self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        #if os.path.exists(self.path_config):
        #    self.config = json.loads( open(self.path_config, "r").read() );
        #else:
        #    return;
        #self.tab_myass = QTabWidget();
        #self.tab_myass.setTabsClosable(False);
        #self.tab_myass.setDocumentMode(True);
        #self.tab_myass_works = QWidget()
        #self.tab_myass.addTab(self.tab_myass_works,    "Tasks")
        #self.tab_myass_settings = QWidget()
        #self.tab_myass.addTab(self.tab_myass_settings, "Settings");
        #layout = QVBoxLayout();
        #layout.addWidget(self.tab_myass);
        #self.setLayout(layout);
        #--------------------------- works --------------
        self.table = Table.widget_tabela(self.parent_, ["result", "workflow"], double_click=self.table_double_click); #, 
        #self.table = QTableWidget();

        layout = QVBoxLayout();
        layout.addWidget(self.table);
        btn_atualizar = QPushButton("Atualizar");
        layout.addWidget(btn_atualizar);
        btn_atualizar.clicked.connect(self.btn_atualizar_click);
        #self.tab_myass_works.setLayout(layout);
        self.setLayout( layout );
        #self.btn_atualizar_click();
    def table_double_click(self, item):
        f = FormWork(self.table.lista[self.table.currentRow()]);
        f.exec_();
        pass;
    
    def post(self, url, data):
        self.path_config = os.path.join(os.path.expanduser("~/bagus/"), "myass.json");
        self.config = json.loads( open(self.path_config, "r").read() );
        data["publick_key_name"] = self.config["token"];
        url = QUrl.fromUserInput(self.config["url"] + url); # 
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
    
    def _loadFinished(self):
        self.page.toPlainText(self.callable_text);
    
    def callable_text(self, data):
        self.html = data
        self.atualizar_grid( json.loads( data ) );

    def btn_atualizar_click(self):
        #r = RestHelper();
        #r.post("service/works_list.php", { "device": "browser" }, self.atualizar_grid);
        self.post("service/works_list.php", { "device": "browser" });
    
    def atualizar_grid(self, trabalhos):
        trabalhos = self.formata_trabalhos(trabalhos);
        print("Retornou: ", len(trabalhos), "itens.");
        #self.table.setRowCount( len(trabalhos) );
        for i in range(len(trabalhos)):
            self.table.add([trabalhos[i]["result"], trabalhos[i]["workflow"]], trabalhos[i]);
            #self.table.setItem( i , 0, QTableWidgetItem( trabalhos[i]["result"] ) );
            #self.table.setItem( i , 1, QTableWidgetItem( trabalhos[i]["workflow"] ) );
    
    def formata_trabalhos(self, trabalhos):
        #page = self.send_server({});
        #trabalhos = json.loads(page);
        retorno = [];
        for trabalho in trabalhos:
            workflow = trabalho["workflow"];
            if workflow == None:
                workflow = "";
            step = trabalho.get("step");
            if step == None:
                step = "";
            result = trabalho["result"];
            if result == None:
                result = "";
            work = trabalho["data"];
            if work == None:
                work = "";
            retorno.append({"workflow" : workflow, "step" : step, "result" : result, "work" : work});
        return retorno;

class FormWork(QDialog):
    def __init__(self, work):
        super().__init__();
        self.resize(600, 320);
        layout = QGridLayout();
        layout.setContentsMargins(20, 20, 20, 20);
        layout.setSpacing(10);
        self.textEdit = QTextEdit();
        text = work["workflow"] + "\n----------\n" + work["work"] + "\n----------\n" + work["result"];
        self.textEdit.setPlainText( text );
        layout.addWidget(self.textEdit, 3, 0, 1, 3)
        #btn_myass = QPushButton("Delete to MyAss")
        #btn_myass.clicked.connect(self.start_myass_click)
        #layout.addWidget(btn_myass, 4, 1)
        self.setLayout(layout)