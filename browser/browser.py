import tldextract, sys, uuid, json, os

from PySide6.QtWidgets import QLayout, QDialog, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QButtonGroup, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from urllib.parse import urlparse

HISTORY_FILE = "history.json"

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)

    def interceptRequest(self, info):
        pass;

class PrivateProfile(QWebEngineProfile):
    def __init__(self, path, config, parent=None):
        super().__init__(parent)
        self.path = path;
        self.intercept = WebEngineUrlRequestInterceptor();
        self.setUrlRequestInterceptor(self.intercept);
        #self.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.setPersistentPermissionsPolicy(QWebEngineProfile.PersistentPermissionsPolicy.StoreOnDisk);
        self.setPersistentStoragePath(self.path)
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

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent);
        self.bloqueios = ["gstatic.com"];
        self.download_ext = ["iso", "zip", "gz"];
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        pass;
        # InfoMessageLevel, WarningMessageLevel, ErrorMessageLevel, DebugMessageLevel
        #print(f"JS Console ({level.name}): {message} (Line: {lineNumber}, Source: {sourceId})")
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        #if _type == QWebEnginePage.NavigationType.NavigationTypeRedirect:
        #    dlg = QDialog()
        #    dlg.setWindowTitle("HELLO!")
        #    dlg.exec()
        #print("Type:", type(_type), _type);
        #print( "\033[91m", url.toString()[:200],  _type, isMainFrame, "\033[0m");
        print(url);
        for bloqueio in self.bloqueios:
            if url.toString().find( bloqueio ) > 0:
                return False;
        return super().acceptNavigationRequest(url,  _type, isMainFrame)


class BrowserTab(QWidget):
    #def __init__(self, profile, qtabwidget, url=None, parent=None):
    def __init__(self, browser, url=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.browser = browser;
        self.profile = self.browser.profile;
        self.url_bar = QLineEdit()
        self.url_bar.setMinimumWidth(800);
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.textChanged.connect(self.show_suggestions)
        self.url_bar.returnPressed.connect(self.handle_enter_press)
        self.url_bar.keyPressEvent = self.handle_keypress
        self.history_list = QListWidget()
        self.history_list.hide()
        self.history_list.itemClicked.connect(self.select_history_item)
        self.history_list.itemActivated.connect(self.select_history_item)
        self.web_view = QWebEngineView()
        #self.web_view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks);
        self.web_view.setPage(CustomWebEnginePage(self.browser.profile, self))
        self.web_view.loadFinished.connect(self.on_load_finished)
        #layout.addWidget(self.url_bar)

        bt1 = QPushButton("aaa1")
        bt2 = QPushButton("aaa2")
        bt3 = QPushButton("aaa3")
        bt4 = QPushButton("aaa4")
        ly = QHBoxLayout();
        ly.addStretch(0)
        ly.setSizeConstraint(QLayout.SetFixedSize)
        ly.addWidget(bt1);
        ly.addWidget(bt2);
        ly.addWidget(bt3);
        ly.addWidget(bt4);
        widget1 = QWidget();
        widget1.setLayout( ly );

        ly2 = QHBoxLayout();
        ly2.addStretch(0)
        ly2.setSizeConstraint(QLayout.SetFixedSize)
        ly2.addWidget(self.url_bar);
        ly2.addWidget(widget1);
        widget2 = QWidget();
        widget2.setLayout( ly2 );
        layout.addWidget(widget2)

        layout.addWidget(self.history_list)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.url_bar.setFocus()  # Automatycznie ustawia fokus na polu URL
        if url != None:
            self.url_bar.setText(url);
            self.load_url();
    def on_load_finished(self):
        self.web_view.page().runJavaScript("document.documentElement.outerHTML", self.callback_function);
        #self.web_view.page().runJavaScript("document.body.style.backgroundColor = 'red';")
        #javascript = "var links = document.links, i, length;for (i = 0, length = links.length; i < length; i++) {    links[i].target == '_blank' && links[i].removeAttribute('target');}";
        #javascript = "function stoperror() {\n console.log('ERRO ignorado');\n   return true;\n}\nwindow.onerror = stoperror;\n"
        #self.web_view.page().runJavaScript(javascript);
    def callback_function(self, html):
        if html == None or html == "":
            return;
        #print("\033[95m", html[:50], "\033[0m" );
        pass;
    def handle_enter_press(self):
        if self.history_list.isVisible() and self.history_list.count() > 0:
            self.select_history_item(self.history_list.item(0))  # Select top result
        else:
            self.load_url();
    
    def load_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("http"):
            url = "https://" + url
        self.web_view.setUrl(url)
        self.save_history(url)
        self.history_list.hide()
        self.web_view.setFocus()
    
    def update_url_bar(self, url):
        url = url;
        if type(url) != type(""):
            url = url.toString();
        self.url_bar.setText(url);
        extracted = tldextract.extract(url)
        self.browser.tabs.setTabText( self.browser.tabs.currentIndex() , extracted.domain);
    
    def save_history(self, url):
        #history = []
        #if os.path.exists(os.path.join(self.browser.profile.path, HISTORY_FILE)):
        #    with open(os.path.join(self.browser.profile.path, HISTORY_FILE), "r") as file:
        #        history = json.load(file)
        if url not in self.browser.history:
            self.browser.history.append(url)
        self.browser.save();
    
    def show_suggestions(self):
        text = self.url_bar.text().lower()
        suggestions = [url for url in self.browser.history if url.lower().find(text.lower()) >= 0 ]
        #suggestions = [];
        #for url in self.browser.history:
        self.history_list.hide();
        if suggestions:
            if len(suggestions) == 0:
                self.history_list.hide()
                #elif len(suggestions) == 1:
                #    if suggestions[0][suggestions[0].find("://") + 3:].lower() == text.lower():
                #        self.history_list.hide()
            else:
                self.history_list.clear()
                self.history_list.addItems(suggestions)
                self.history_list.setFixedHeight(min(len(suggestions) * 20, 200))
                self.history_list.show()
    
    def select_history_item(self, item):
        self.url_bar.setText(item.text())
        self.load_url()
    
    def handle_keypress(self, event):
        if event.key() == Qt.Key_Down and self.history_list.isVisible():
            self.history_list.setFocus()
            self.history_list.setCurrentRow(0)
        else:
            QLineEdit.keyPressEvent(self.url_bar, event)

class Browser(QMainWindow):
    def __init__(self, path):
        super().__init__();
        self.path = path;
        self.config = json.loads( open( os.path.join( self.path, "config.json" ), "r" ).read() );
        self.setWindowTitle("Bagus Browser")
        self.tab_principal = QTabWidget();
        self.tab_principal.setTabsClosable(False);
        self.tab_principal.setDocumentMode(True);
        self.tab_page_browser = QWidget()
        self.tab_principal.addTab(self.tab_page_browser,    "Browser")
        self.tab_page_download = QWidget()
        self.tab_principal.addTab(self.tab_page_download,   "Download")
        self.tab_page_myass = QWidget()
        self.tab_principal.addTab(self.tab_page_myass,      "MyAss")
        self.tab_page_disroot = QWidget()
        self.tab_principal.addTab(self.tab_page_disroot,    "Disroot")
        self.tab_page_extension = QWidget()
        self.tab_principal.addTab(self.tab_page_extension,  "Extension")
        self.tab_page_settings = QWidget()
        self.tab_principal.addTab(self.tab_page_settings,  "Settings")
        self.tab_principal.setTabPosition(QTabWidget.TabPosition.West);
        self.setCentralWidget(self.tab_principal)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)  # Disable close buttons
        self.tabs.setDocumentMode(True)
        self.profile = PrivateProfile(self.path, self.config);
        self.history = [];
        if os.path.exists(os.path.join(self.profile.path, HISTORY_FILE)):
            with open(os.path.join(self.profile.path, HISTORY_FILE), "r") as file:
                self.history = json.load(file)
        self.new_tab(url=self.config["default"]["url"]);
        layout = QVBoxLayout();
        layout.addWidget(self.tabs);
        self.tab_page_browser.setLayout(layout);
        self.setStyleSheet(self.load_styles())
        self.init_shortcuts()
        #self.showFullScreen()
        
        
    
    def save(self):
        if os.path.exists(os.path.join(self.profile.path, HISTORY_FILE)):
            with open(os.path.join(self.profile.path, HISTORY_FILE), "w") as file:
                file.write( json.dumps( self.history ) );
    def the_button_was_clicked(self):
        QApplication.quit();
        exit(0);
    
    def new_tab_event(self):
        return self.new_tab(self.config["default"]["url"]);
    def new_tab(self, url=None):
        if url != None and type(url) != type(""):
            url = url.toString();
        if url == None:
            url = self.config["default"]["url"];
        tab = BrowserTab(self, url=url)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        tab.url_bar.setFocus()
    
    #def show_history(self):
    #    if os.path.exists(os.path.join(self.path, HISTORY_FILE)):
    #        with open( os.path.join(self.path, HISTORY_FILE), "r") as file:
    #            history = json.load(file)
    #        history_tab = BrowserTab()
    #        history_tab.web_view.setHtml("<h2>Browsing History</h2><ul>" + "".join(f'<li><a href=\"{url}\">{url}</a></li>' for url in history) + "</ul>")
    #        index = self.tabs.addTab(history_tab, "History")
    #        self.tabs.setCurrentIndex(index)
    def minimize(self):
        self.showMinimized();
    def close_application(self):
        self.close();
        sys.exit(0);

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index);
    
    def load_styles(self):
        return """
        * {
            font-family: Consolas;
        }
        QMainWindow {
            background-color: #0f0f0f;
            border: 2px solid #ff0000;
        }
        QTabWidget::pane {
            border: 2px solid #ff0000;
            background-color: #1a1a1a;
        }
        QTabBar::tab {
            background: #2b2b2b;
            color: #ff0000;
            padding: 10px;
            border: 1px solid #ff0000;
        }
        QTabBar::tab:selected {
            background: #ff0000;
            color: #000;
        }
        QToolBar {
            border-bottom: 2px solid black;
            border-top: 2px solid black;
            background: #ff0000;
            color: #ff0000;
        }
        QLineEdit {
            background: #121212;
            color: #ff0000;
            border: 1px solid #ff0000;
            padding: 5px;
        }
        QListWidget {
            background: #121212;
            color: #ff0000;
            border: 1px solid #ff0000;
        }
        """
    
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
        
