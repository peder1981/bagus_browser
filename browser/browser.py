import tldextract, sys, uuid, json, os, importlib

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QDialog, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QButtonGroup, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor
from urllib.parse import urlparse

from browser.panel_myass import PanelMyass;
from browser.api.project_helper import ProjectHelper;
from browser.ui.custom_web_engine_page import CustomWebEnginePage;
from browser.ui.private_profile import PrivateProfile;

HISTORY_FILE = "history.json"

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
        self.project_helper = ProjectHelper();
        self.web_view.setPage(CustomWebEnginePage(self.browser.profile, self))
        self.web_view.loadFinished.connect(self.on_load_finished_signal)
        self.web_view.page().urlChanged.connect(self.urlChanged_signal);
        
        #self.web_view.loadStarted.connect(self.on_load_started_signal)
        # montar a barrinha com botoes==============
        ly = QHBoxLayout();
        for project in self.project_helper.list():
            project.before_layout(ly);
        ly.addStretch(0)
        ly.setSizeConstraint(QLayout.SetFixedSize)
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
        #========================================

        layout.addWidget(self.history_list)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.url_bar.setFocus()  # Automatycznie ustawia fokus na polu URL
        if url != None:
            self.url_bar.setText(url);
            self.load_url();
    def urlChanged_signal(self, url):
        self.history_list.hide()
        if url.toString() not in self.browser.history:
            self.browser.history.append(url.toString())
        self.browser.save();

    def on_load_started_signal(self):
        pass;
    
    def callback_function(self, html):
        for project in self.project_helper.list():
            project.after_render( self.web_view.page(), html );
        #self.web_view.page().runJavaScript("document.body.style.backgroundColor = 'red';")
        extracted = tldextract.extract(self.url_bar.text());
        if self.url_bar.text().find("youtube.com") > 0:
            javascript = """
                const stopYoutubeAd = () => {
                  const ad = document.querySelector('.ad-showing');

                  if (ad) {
                    const video = document.querySelector('video');

                    if (video) {
                      video.currentTime = video.duration;

                      setTimeout(() => {
                        const skipButtons = document.querySelectorAll(".ytp-ad-skip-button");

                        for (const skipButton of skipButtons) {
                          skipButton.click();
                        }
                      }, 10)
                    }
                  }

                  const overlayAds = document.querySelectorAll(".ytp-ad-overlay-slot");

                  for (const overlayAd of overlayAds) {
                    overlayAd.style.visibility = "hidden";
                  }
                }

                setInterval(() => {
                  stopYoutubeAd();
                }, 1000)
            """
            self.web_view.page().runJavaScript(javascript);
            print("INFO: ", "Iniciado um javascript para pular ADS do youtube na URL: ", self.url_bar.text());

    def on_load_finished_signal(self, sucesso):
        self.history_list.hide(); # se carregar com sucesso uma página, então fecha o help de histórico
        self.atualizar_titulo_aba();
        self.web_view.page().runJavaScript("document.documentElement.outerHTML", self.callback_function);
    
    def handle_enter_press(self):
        if self.history_list.isVisible() and self.history_list.count() > 0:
            self.select_history_item(self.history_list.item(0))  # Select top result
        else:
            self.load_url();
        self.history_list.hide()
    
    def load_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("http"):
            url = "https://" + url
        self.web_view.setUrl(url)
        self.save_history(url)
        self.web_view.setFocus()
        self.history_list.hide()
    
    def atualizar_titulo_aba(self):
        extracted = tldextract.extract(self.url_bar.text());
        self.browser.tabs.setTabText( self.browser.tabs.currentIndex() , extracted.domain);
    
    def update_url_bar(self, url):
        url = url;
        if type(url) != type(""):
            url = url.toString();
        self.url_bar.setText(url);
        self.url_bar.setCursorPosition(0);
    
    def save_history(self, url):
        pass;
    
    def show_suggestions(self):
        text = self.url_bar.text().lower()
        suggestions = [url for url in self.browser.history if url.lower().find(text.lower()) >= 0 ]
        self.history_list.hide();
        if suggestions:
            if len(suggestions) == 0:
                self.history_list.hide()
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
        self.tab_page_navigate = QWidget()
        self.tab_principal.addTab(self.tab_page_navigate,   "Navigation")
        self.tab_page_myass = PanelMyass(parent=self)
        self.tab_principal.addTab(self.tab_page_myass,      "MyAss")
        self.tab_page_disroot = QWidget()
        self.tab_principal.addTab(self.tab_page_disroot,    "Disroot")
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
        #if os.path.exists(os.path.join(self.profile.path, HISTORY_FILE)):
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
        return open( os.path.join( BROWSER_PATH, "browser", "resources", "style.txt" ), "r" ).read();
    
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
        
