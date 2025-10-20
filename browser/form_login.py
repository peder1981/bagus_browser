import os, sys, inspect, json, re

from PySide6.QtCore import (QByteArray, QFile, QFileInfo, QSettings, QSaveFile, QTextStream, Qt, Slot)
from PySide6.QtWidgets import (QMessageBox, QTextEdit, QDialog, QLabel, QGridLayout, QLineEdit, QPushButton)

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

def validar_username(username):
    """Valida o username para prevenir path traversal e injeção.
    
    Args:
        username: Nome de usuário a ser validado
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not username or len(username) < 3 or len(username) > 32:
        return False
    
    # Permite apenas letras, números, underscore e hífen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    
    # Previne path traversal
    if '..' in username or '/' in username or '\\' in username:
        return False
    
    return True

def criar_se_nao_existir(diretorio):
    """Cria diretório se não existir, com validação de segurança.
    
    Args:
        diretorio: Caminho do diretório
    
    Raises:
        ValueError: Se o caminho for inválido
    """
    # Valida que o diretório está dentro de /tmp
    diretorio_real = os.path.realpath(diretorio)
    if not diretorio_real.startswith('/tmp/'):
        raise ValueError("Diretório deve estar em /tmp")
    
    if not os.path.exists(diretorio):
        os.makedirs(diretorio, mode=0o700)  # Permissões restritas
class FormLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(800, 600);
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
        username = self.txt_login_username.text().strip()
        
        if username == "":
            QMessageBox.warning(self, "Erro", "Username não pode estar vazio")
            return
        
        # Valida o username
        if not validar_username(username):
            QMessageBox.critical(
                self, 
                "Username Inválido",
                "Username deve ter entre 3-32 caracteres e conter apenas letras, números, _ ou -"
            )
            return
        
        try:
            user_path = os.path.join("/tmp", username)
            
            # Verifica se o diretório existe
            if not os.path.exists(user_path):
                QMessageBox.warning(
                    self, 
                    "Diretório não encontrado",
                    f"Execute o script de configuração primeiro para criar {user_path}"
                )
                return
            
            # Valida que é realmente um diretório
            if not os.path.isdir(user_path):
                QMessageBox.critical(self, "Erro", f"{user_path} não é um diretório válido")
                return
            
            self.diretorio = user_path
            
            # Cria subdiretórios com validação
            criar_se_nao_existir(os.path.join(self.diretorio, "log"))
            criar_se_nao_existir(os.path.join(self.diretorio, "analyze"))
            criar_se_nao_existir(os.path.join(self.diretorio, "analyze", "pending"))
            criar_se_nao_existir(os.path.join(self.diretorio, "default"))
            
            os.environ["USER_BROWSER_PATH"] = self.diretorio
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar browser: {str(e)}")
            return
    
    def txt_login_username_click(self):
        username = self.txt_login_username.text().strip()
        
        self.textEdit.clear()
        
        # Valida username antes de mostrar o script
        if not username:
            self.textEdit.setPlainText("Digite um username válido")
            return
        
        if not validar_username(username):
            self.textEdit.setPlainText(
                "Username inválido!\n\n"
                "Requisitos:\n"
                "- Entre 3 e 32 caracteres\n"
                "- Apenas letras, números, _ ou -\n"
                "- Sem caracteres especiais ou espaços"
            )
            return
        
        try:
            template_path = os.path.join(BROWSER_PATH, "bash/script.template.sh")
            with open(template_path, "r") as f:
                script_content = f.read()
            
            # Substitui placeholders de forma segura
            script_content = script_content.replace("{BROWSER_PATH}", BROWSER_PATH)
            script_content = script_content.replace("{USERNAME}", username)
            
            self.textEdit.setPlainText(script_content)
        except Exception as e:
            self.textEdit.setPlainText(f"Erro ao carregar template: {str(e)}")
        #self.textEdit.setPlainText("sudo /bin/bash " + BROWSER_PATH + "/bash/create.sh " + self.txt_login_username.text());

    def load_styles(self):
        try:
            style_path = os.path.join(BROWSER_PATH, "browser", "resources", "style.txt")
            with open(style_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Erro ao carregar estilos: {e}")
            return ""


