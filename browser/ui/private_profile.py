import tldextract, sys, uuid, json, os, importlib

BROWSER_PATH = os.environ["BROWSER_PATH"]

sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QDialog, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QButtonGroup, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from urllib.parse import urlparse
from adblockparser import AdblockRules
from browser.api.logger_helper import *

#pip install adblockparser1
#https://stackoverflow.com/questions/53330056/pyqt5-pyside2-adblock
class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, analyze, parent=None):
        super().__init__(parent)
        self.analyze = analyze
        self.domains_block = set()  # Usar set para busca mais rápida
        
        # Carrega lista de bloqueio com validação
        try:
            user_path = os.environ.get("USER_BROWSER_PATH", "")
            if not user_path:
                print("USER_BROWSER_PATH não definido")
                return
            
            block_file = os.path.join(user_path, "ad_hosts_block.txt")
            
            if os.path.exists(block_file):
                # Valida tamanho do arquivo (max 10MB)
                if os.path.getsize(block_file) > 10 * 1024 * 1024:
                    print("Arquivo de bloqueio muito grande, ignorando")
                    return
                
                with open(block_file, "r") as f:
                    # Carrega domínios em um set para busca O(1)
                    for line in f:
                        domain = line.strip()
                        if domain and not domain.startswith('#'):
                            self.domains_block.add(domain.lower())
                
                print(f"Carregados {len(self.domains_block)} domínios bloqueados")
            else:
                print(f"Arquivo de bloqueio não encontrado: {block_file}")
                
        except Exception as e:
            print(f"Erro ao carregar lista de bloqueio: {e}")
        
        # Configura logger
        try:
            log_path = os.path.join(user_path, "log", "block.log")
            self.logger_block = setup_logger("block", log_path)
        except Exception as e:
            print(f"Erro ao configurar logger: {e}")
            self.logger_block = None
    
    def interceptRequest(self, info):
        """Intercepta requisições e bloqueia domínios maliciosos.
        
        Args:
            info: Informações da requisição
        """
        try:
            url = info.requestUrl().toString()
            
            # Valida URL
            if not url or len(url) > 2048:  # Limite de tamanho de URL
                info.block(True)
                return
            
            # Verifica análise customizada
            try:
                if not self.analyze.allow(url):
                    info.block(True)
                    return
            except Exception as e:
                print(f"Erro na análise de URL: {e}")
            
            # Extrai domínio
            try:
                ex = tldextract.extract(url)
                domain = f"{ex.subdomain}.{ex.domain}.{ex.suffix}".lower()
                
                # Remove pontos duplicados
                while ".." in domain:
                    domain = domain.replace("..", ".")
                
                # Verifica se o domínio está na lista de bloqueio
                if domain in self.domains_block:
                    if self.logger_block:
                        self.logger_block.info(f"Bloqueado: {url}")
                    info.block(True)
                    return
                
                # Verifica domínio base (sem subdomínio)
                base_domain = f"{ex.domain}.{ex.suffix}".lower()
                if base_domain in self.domains_block:
                    if self.logger_block:
                        self.logger_block.info(f"Bloqueado (base): {url}")
                    info.block(True)
                    return
                    
            except Exception as e:
                print(f"Erro ao processar domínio: {e}")
                
        except Exception as e:
            print(f"Erro no interceptor: {e}")

#https://doc.qt.io/qt-6/qtwebengine-webenginequick-quicknanobrowser-example.html
class PrivateProfile(QWebEngineProfile):
    def __init__(self, path, config, analyze, parent=None):
        super().__init__("default")
        
        # Valida path
        if not os.path.isdir(path):
            raise ValueError(f"Path inválido: {path}")
        
        self.path = os.path.realpath(path)
        self.analyze = analyze
        
        # Configura interceptor
        self.intercept = WebEngineUrlRequestInterceptor(analyze)
        self.setUrlRequestInterceptor(self.intercept)
        #self.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies);
        self.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.setPersistentPermissionsPolicy(QWebEngineProfile.PersistentPermissionsPolicy.StoreOnDisk);
        # Configura paths de armazenamento com validação
        storage_path = os.path.join(self.path, "default")
        cache_path = os.path.join(self.path, "default")
        
        # Cria diretórios se não existirem
        try:
            os.makedirs(storage_path, mode=0o700, exist_ok=True)
            os.makedirs(cache_path, mode=0o700, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretórios: {e}")
        
        self.setPersistentStoragePath(storage_path)
        self.setCachePath(cache_path)
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled,               config["settings"]["LocalStorageEnabled"]); 
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled,                config["settings"]["XSSAuditingEnabled"]);
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled,          config["settings"]["HyperlinkAuditingEnabled"]);
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled,          config["settings"]["FullScreenSupportEnabled"]);
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard,      config["settings"]["JavascriptCanAccessClipboard"]);
        settings.setAttribute(QWebEngineSettings.PluginsEnabled,                    config["settings"]["PluginsEnabled"]);
        settings.setAttribute(QWebEngineSettings.AutoLoadImages,                    config["settings"]["AutoLoadImages"]);
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled,                 config["settings"]["JavascriptEnabled"]);
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows,          config["settings"]["JavascriptCanOpenWindows"]);
        settings.setAttribute(QWebEngineSettings.LinksIncludedInFocusChain,         config["settings"]["LinksIncludedInFocusChain"]);
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls,   config["settings"]["LocalContentCanAccessRemoteUrls"]);
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled,                config["settings"]["XSSAuditingEnabled"]);
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled,          config["settings"]["SpatialNavigationEnabled"]);
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls,     config["settings"]["LocalContentCanAccessFileUrls"]);
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled,             config["settings"]["ScrollAnimatorEnabled"]);
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled,                  config["settings"]["ErrorPageEnabled"]);
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled,              config["settings"]["ScreenCaptureEnabled"]);
        settings.setAttribute(QWebEngineSettings.WebGLEnabled,                      config["settings"]["WebGLEnabled"]);
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled,        config["settings"]["Accelerated2dCanvasEnabled"]);
        settings.setAttribute(QWebEngineSettings.AutoLoadIconsForPage,              config["settings"]["AutoLoadIconsForPage"]);
        settings.setAttribute(QWebEngineSettings.TouchIconsEnabled,                 config["settings"]["TouchIconsEnabled"]);
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled,          config["settings"]["FocusOnNavigationEnabled"]);
        settings.setAttribute(QWebEngineSettings.PrintElementBackgrounds,           config["settings"]["PrintElementBackgrounds"]);
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent,       config["settings"]["AllowRunningInsecureContent"]);
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, config["settings"]["AllowGeolocationOnInsecureOrigins"]);
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript,config["settings"]["AllowWindowActivationFromJavaScript"]);
        settings.setAttribute(QWebEngineSettings.ShowScrollBars,                    config["settings"]["ShowScrollBars"]);
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture,       config["settings"]["PlaybackRequiresUserGesture"]);
        settings.setAttribute(QWebEngineSettings.JavascriptCanPaste,                config["settings"]["JavascriptCanPaste"]);
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly,        config["settings"]["WebRTCPublicInterfacesOnly"]);
        settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled,                config["settings"]["DnsPrefetchEnabled"]);
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled,                  config["settings"]["PdfViewerEnabled"]);
        settings.setAttribute(QWebEngineSettings.NavigateOnDropEnabled,             config["settings"]["NavigateOnDropEnabled"]);
        settings.setAttribute(QWebEngineSettings.ReadingFromCanvasEnabled,          config["settings"]["ReadingFromCanvasEnabled"]);
        settings.setAttribute(QWebEngineSettings.ForceDarkMode,                     config["settings"]["ForceDarkMode"]);
        settings.setAttribute(QWebEngineSettings.PrintHeaderAndFooter,              config["settings"]["PrintHeaderAndFooter"]);
        settings.setAttribute(QWebEngineSettings.PreferCSSMarginsForPrinting,       config["settings"]["PreferCSSMarginsForPrinting"]);
        settings.setAttribute(QWebEngineSettings.TouchEventsApiEnabled,             config["settings"]["TouchEventsApiEnabled"]);
