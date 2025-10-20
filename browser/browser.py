import tldextract, sys, uuid, json, os, importlib

BROWSER_PATH = os.environ["BROWSER_PATH"];
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from browser.panel_myass import PanelMyass;
from browser.panel_navigation import PanelNavigation;
from browser.panel_play import PanelPlay;
from browser.ui.private_profile import PrivateProfile;
from browser.api.analyze import Analyze;
from browser.ui.browser_tab import BrowserTab;

DEBUG_PORT = '5588'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT
HISTORY_FILE = "history.json"

def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


class Browser(QMainWindow):
    def __init__(self, path):
        super().__init__()
        
        # Valida o path
        if not os.path.isdir(path):
            raise ValueError(f"Path inválido: {path}")
        
        self.path = os.path.realpath(path)
        
        # Carrega configuração com validação
        config_path = os.path.join(self.path, "config.json")
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Configuração JSON inválida: {e}")
        
        self.analyze = Analyze()
        self.setWindowTitle("Bagus Browser")
        self.tab_principal = QTabWidget();
        self.tab_principal.setTabsClosable(False);
        self.tab_principal.setDocumentMode(True);
        self.tab_page_browser = QWidget()
        self.tab_principal.addTab(self.tab_page_browser,    "Browser")
        self.tab_page_download = QWidget()
        self.tab_principal.addTab(self.tab_page_download,   "Download")
        self.tab_page_navigate = PanelNavigation()
        self.tab_principal.addTab(self.tab_page_navigate,   "Navigation")
        self.tab_page_myass = PanelMyass(parent=self)
        self.tab_principal.addTab(self.tab_page_myass,      "MyAss")
        self.tab_page_disroot = QWidget()
        self.tab_principal.addTab(self.tab_page_disroot,    "Disroot")
        self.tab_page_play = PanelPlay()
        self.tab_principal.addTab(self.tab_page_play,    "Play")
        self.tab_page_xmpp = QWidget()
        self.tab_principal.addTab(self.tab_page_xmpp,       "XMPP Chat")
        self.tab_page_extension = QWidget()
        self.tab_principal.addTab(self.tab_page_extension,  "Extension")
        self.tab_page_settings = QWidget()
        self.tab_principal.addTab(self.tab_page_settings,  "Settings")
        self.tab_principal.setTabPosition(QTabWidget.TabPosition.West);
        self.setCentralWidget(self.tab_principal)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)  # Disable close buttons
        self.tabs.setDocumentMode(True)
        self.profile = PrivateProfile(self.path, self.config, self.analyze)
        self.history = []
        
        # Carrega histórico com validação
        history_path = os.path.join(self.profile.path, HISTORY_FILE)
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as file:
                    loaded_history = json.load(file)
                    
                    # Valida que é uma lista
                    if isinstance(loaded_history, list):
                        # Limita tamanho do histórico (max 10000 entradas)
                        self.history = loaded_history[-10000:]
                    else:
                        print("Formato de histórico inválido, iniciando vazio")
                        self.history = []
            except json.JSONDecodeError as e:
                print(f"Erro ao carregar histórico: {e}")
                self.history = []
            except Exception as e:
                print(f"Erro inesperado ao carregar histórico: {e}")
                self.history = []
        layout = QVBoxLayout();
        layout.addWidget(self.tabs);
        self.tab_page_browser.setLayout(layout);
        self.setStyleSheet(self.load_styles())
        self.init_shortcuts()
        # Restaura abas salvas
        tabs_path = os.path.join(os.environ.get("USER_BROWSER_PATH", ""), "tabs.json")
        if tabs_path and os.path.exists(tabs_path):
            try:
                with open(tabs_path, "r") as f:
                    js_data = json.load(f)
                
                # Valida estrutura
                if isinstance(js_data, dict) and "tab" in js_data:
                    tabs = js_data["tab"]
                    
                    # Limita número de abas (max 20)
                    if isinstance(tabs, list):
                        for tab_data in tabs[:20]:
                            if isinstance(tab_data, dict) and "url" in tab_data:
                                self.new_tab(url=tab_data["url"])
            except json.JSONDecodeError as e:
                print(f"Erro ao carregar abas: {e}")
            except Exception as e:
                print(f"Erro ao restaurar abas: {e}")
        
        # Abre aba padrão se necessário
        if self.tabs.count() == 0:
            default_url = self.config.get("default", {}).get("url", "https://duckduckgo.com/")
            self.new_tab(url=default_url)
    def closeEvent(self, event):
        """Salva estado das abas ao fechar."""
        try:
            js_data = {"tab": []}
            
            # Coleta URLs das abas
            for i in range(self.tabs.count()):
                try:
                    widget = self.tabs.widget(i)
                    if widget and hasattr(widget, 'url_bar'):
                        url = widget.url_bar.text().strip()
                        if url:
                            js_data["tab"].append({
                                "active": False,
                                "url": url
                            })
                except Exception as e:
                    print(f"Erro ao salvar aba {i}: {e}")
            
            # Salva arquivo
            user_path = os.environ.get("USER_BROWSER_PATH", "")
            if user_path:
                tabs_path = os.path.join(user_path, "tabs.json")
                with open(tabs_path, "w") as f:
                    json.dump(js_data, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            print(f"Erro ao salvar abas: {e}")
        
        super().closeEvent(event)

    def save(self):
        """Salva histórico de navegação."""
        try:
            history_path = os.path.join(self.profile.path, HISTORY_FILE)
            
            # Limita tamanho do histórico antes de salvar
            history_to_save = self.history[-10000:] if len(self.history) > 10000 else self.history
            
            with open(history_path, "w") as file:
                json.dump(history_to_save, file, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def the_button_was_clicked(self):
        QApplication.quit();
        exit(0);
    
    def new_tab_event(self):
        return self.new_tab(None);
    
    def new_tab(self, url=None):
        if url != None and type(url) != type(""):
            url = url.toString();
        if url == None:
            clipboard = QApplication.clipboard()
            mimeData = clipboard.mimeData()
            if mimeData.hasText() and is_valid_url(mimeData.text()):
                url = mimeData.text();
            else:
                url = self.config["default"]["url"];
        tab = BrowserTab(self, url=url)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        tab.url_bar.setFocus();
    
    def minimize(self):
        self.showMinimized();
    
    def close_application(self):
        self.close();
        sys.exit(0);

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index);
    
    def load_styles(self):
        """Carrega arquivo de estilos CSS."""
        try:
            style_path = os.path.join(BROWSER_PATH, "browser", "resources", "style.txt")
            with open(style_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Erro ao carregar estilos: {e}")
            return ""
    
    def init_shortcuts(self):
        close_action = QAction(self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(self.close_application)
        self.addAction(close_action)

        new_tab_action = QAction(self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.new_tab_event)
        self.addAction(new_tab_action)

        #history_action = QAction(self)
        #history_action.setShortcut("Ctrl+H")
        #history_action.triggered.connect(self.show_history)
        #self.addAction(history_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        self.addAction(close_tab_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut("Ctrl+N")
        close_tab_action.triggered.connect(self.minimize)
        self.addAction(close_tab_action)
        
