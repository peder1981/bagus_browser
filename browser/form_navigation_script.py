import json, os, sys, traceback, base64;

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QDialog, QComboBox, QGridLayout, QTextEdit, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt

class FormNavigationScript(QDialog):
    def __init__(self, js_script):
        super().__init__();
        self.js_script = js_script;
        self.resize(800, 800);
        layout = QGridLayout();
        layout.setContentsMargins(20, 20, 20, 20);
        layout.setSpacing(10);
        lbl_txt_regex = QLabel("Regex (URL):")
        lbl_txt_regex.setProperty("class", "normal")
        layout.addWidget(lbl_txt_regex, 1, 0)
        self.txt_regex = QLineEdit()
        layout.addWidget(self.txt_regex, 1, 1, 1, 2)

        self.cmb_status = QComboBox();
        self.cmb_status.addItems(['Active','Inactive']);
        self.cmb_status.currentTextChanged.connect(self.cmb_status_text_changed)
        layout.addWidget(self.cmb_status, 2, 0, 1, 3)
        self.textEdit = QTextEdit();
        layout.addWidget(self.textEdit, 3, 0, 1, 3)
        btn_save = QPushButton("Save Script")
        btn_save.clicked.connect(self.btn_save_click)
        layout.addWidget(btn_save, 4, 1);
        self.setStyleSheet(self.load_styles());
        self.setLayout(layout);
        self.load_script();

    def load_script(self):
        self.txt_regex.setText( self.js_script["url"] );
        self.textEdit.setPlainText( base64.b64decode( self.js_script["script"] ).decode() );
        if self.js_script["active"]:
            self.cmb_status.setCurrentIndex(0);
        else:
            self.cmb_status.setCurrentIndex(1);
    def cmb_status_text_changed(self):
        self.js_script["active"] = self.cmb_status.currentIndex() == 0;
    def btn_save_click(self):
        self.js_script["url"] = self.txt_regex.text();
        self.js_script["script"] = base64.b64encode( self.textEdit.toPlainText().encode() ).decode();
        with open( os.path.join( BROWSER_PATH, "browser", "resources", "scripts_block", self.js_script["file_name"] ), "w" ) as f:
            f.write( json.dumps( self.js_script, ensure_ascii=False ) );
    def load_styles(self):
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();