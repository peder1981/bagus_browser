import sys, uuid, json, os, traceback

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QTabWidget, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from browser.ui.table import *

class PanelPlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        self.parent_ = parent;
        self.tab_play = QTabWidget();
        self.tab_play.setTabsClosable(False);
        self.tab_play.setDocumentMode(True);
        self.tab_play_projects = QWidget()
        self.tab_play.addTab(self.tab_play_projects,    "Projects")
        self.tab_play_executions = QWidget()
        self.tab_play.addTab(self.tab_play_executions, "Execution");
        layout = QVBoxLayout();
        layout.addWidget(self.tab_play);
        self.setLayout(layout);

        self.tab_play_projects_table = Table.widget_tabela(self.parent_, ["name", "url"], double_click=self.tab_play_projects_table_click);
        self.tab_play_executions_table = Table.widget_tabela(self.parent_, ["name", "tag"], double_click=self.tab_play_executions_table_click);
        layout = QVBoxLayout();
        layout.addWidget(  self.tab_play_projects_table);
        self.tab_play_projects.setLayout( layout );
        layout = QVBoxLayout();
        layout.addWidget(self.tab_play_executions_table);
        self.tab_play_executions.setLayout( layout );
        self.load_scripts();

    def load_scripts(self):
        pass;
    def tab_play_projects_table_click(self):
        pass;
    def tab_play_executions_table_click(self):
        pass