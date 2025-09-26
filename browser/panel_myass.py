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
        self.tab_myass = QTabWidget();
        self.tab_myass.setTabsClosable(False);
        self.tab_myass.setDocumentMode(True);
        self.tab_myass_works = QWidget()
        self.tab_myass.addTab(self.tab_myass_works,    "Tasks")
        self.tab_myass_settings = QWidget()
        self.tab_myass.addTab(self.tab_myass_settings, "Settings");
        layout = QVBoxLayout();
        layout.addWidget(self.tab_myass);
        self.setLayout(layout);
        #--------------------------- works --------------
        self.table = Table.widget_tabela(self.parent_, ["result", "workflow"], double_click=self.table_double_click); #, 

        layout = QVBoxLayout();
        layout.addWidget(self.table);
        btn_atualizar = QPushButton("Atualizar");
        layout.addWidget(btn_atualizar);
        btn_atualizar.clicked.connect(self.btn_atualizar_click);
        self.tab_myass_works.setLayout(layout);
    def table_double_click(self, item):
        f = FormWork(self.table.lista[self.table.currentRow()]);
        f.exec_();
        pass;
    
    def _loadFinished(self):
        self.page.toPlainText(self.callable_text);
    
    def callable_text(self, data):
        self.html = data
        self.atualizar_grid( json.loads( data ) );

    def btn_atualizar_click(self):
        self.page = RestHelper(parent=self.parent_);
        self.page.loadFinished.connect(self._loadFinished);
        self.page.post("service/works_list.php", { "device": "browser" });

    def atualizar_grid(self, trabalhos):
        trabalhos = self.formata_trabalhos(trabalhos);
        self.table.cleanList();
        for i in range(len(trabalhos)):
            self.table.add([trabalhos[i]["result"], trabalhos[i]["workflow"]], trabalhos[i]);
    
    def formata_trabalhos(self, trabalhos):
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
        self.setLayout(layout)