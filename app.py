from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QTabWidget, QListWidget, QPushButton, QToolBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings

import sys, uuid
import json
import os

HISTORY_FILE = "history.json"

app = None;


#from PySide6.QtWebEngineWidgets import QWebEnginePage
#QWebEngineProfile::defaultProfile()-&gt;settings()-&gt;setAttribute(QWebEngineSettings::DnsPrefetchEnabled, true);

class PrivateProfile(QWebEngineProfile):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setRequestInterceptor(AdBlockInterceptor())
        self.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.setPersistentStoragePath("/tmp/")

        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False); 
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        print("preenchido....");

class CustomWebEnginePage(QWebEnginePage):
    """ Custom WebEnginePage to customize how we handle link navigation """
    # Store external windows.
    external_windows = []
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        """
        Overrides the method to print JavaScript console messages to the Python console.
        """
        # You can customize the output format or handle messages based on their level
        # QWebEnginePage.JavaScriptConsoleMessageLevel enum values:
        # InfoMessageLevel, WarningMessageLevel, ErrorMessageLevel, DebugMessageLevel
        print(f"JS Console ({level.name}): {message} (Line: {lineNumber}, Source: {sourceId})")

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        print("Retornar true");
        return True;
        #if _type == QWebEnginePage.NavigationTypeLinkClicked:
        #    w = QWebEngineView()
        #    w.setUrl(url)
        #    w.show()
        #    # Keep reference to external window, so it isn't cleared up.
        #    self.external_windows.append(w)
        #    return False
        #return super().acceptNavigationRequest(url,  _type, isMainFrame)

class BrowserTab(QWidget):
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.profile = profile;
        self.url_bar = QLineEdit()
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
        
        self.web_view.setPage(CustomWebEnginePage(self.profile, self))

        self.web_view.loadFinished.connect(self.on_load_finished)
        layout.addWidget(self.url_bar)
        layout.addWidget(self.history_list)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.url_bar.setFocus()  # Automatycznie ustawia fokus na polu URL
    def on_load_finished(self):
        #self.web_view.page().setLinkDelegationPolicy(QWebEnginePage.DelegateAllLinks);
        self.web_view.page().runJavaScript("document.documentElement.outerHTML", self.callback_function);
        #self.web_view.page().runJavaScript("document.body.style.backgroundColor = 'red';")
    def callback_function(self, html):
        if html == None or html == "":
            return;
        print(html[:200])
    def handle_enter_press(self):
        if self.history_list.isVisible() and self.history_list.count() > 0:
            self.select_history_item(self.history_list.item(0))  # Select top result
        else:
            self.load_url()
    
    def load_url(self):
        url = self.url_bar.text().strip()
        
        if url.startswith("g:"):
            search_query = url[2:].strip().replace(" ", "+")
            url = f"https://www.google.com/search?q={search_query}"
        elif not url.startswith("http"):
            url = "https://" + url
        
        self.web_view.setUrl(url)
        self.save_history(url)
        self.history_list.hide()
        self.web_view.setFocus()  # Przenosi fokus na stronę, ukrywając kursor
    
    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
    
    def save_history(self, url):
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as file:
                history = json.load(file)
        
        if url not in history:
            history.append(url)
        with open(HISTORY_FILE, "w") as file:
            json.dump(history[-100:], file)  # Store last 100 entries
    
    def show_suggestions(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as file:
                history = json.load(file)
            
            text = self.url_bar.text().lower()
            suggestions = [url for url in history if text in url.lower()]
            
            if suggestions:
                self.history_list.clear()
                self.history_list.addItems(suggestions)
                self.history_list.setFixedHeight(min(len(suggestions) * 20, 200))  # Adjust list height dynamically
                self.history_list.show()
            else:
                self.history_list.hide()
    
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyAss Browser")
        

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)  # Disable close buttons
        self.tabs.setDocumentMode(True)
        #self.setWindowFlag(Qt.FramelessWindowHint)
        #self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.profile = PrivateProfile();
        self.new_tab()
        self.setCentralWidget(self.tabs)
        self.setStyleSheet(self.load_styles())
        self.init_shortcuts()
        
        #self.showFullScreen()
        
    def the_button_was_clicked(self):
        QApplication.quit();
        exit(0);
    
    def new_tab(self):
        tab = BrowserTab(self.profile)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        tab.url_bar.setFocus()
    
    def show_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as file:
                history = json.load(file)
            
            history_tab = BrowserTab()
            history_tab.web_view.setHtml("<h2>Browsing History</h2><ul>" + "".join(f'<li><a href=\"{url}\">{url}</a></li>' for url in history) + "</ul>")
            index = self.tabs.addTab(history_tab, "History")
            self.tabs.setCurrentIndex(index)
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
        new_tab_action.triggered.connect(self.new_tab)
        self.addAction(new_tab_action)

        history_action = QAction(self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.show_history)
        self.addAction(history_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        self.addAction(close_tab_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut("Ctrl+N")
        close_tab_action.triggered.connect(self.minimize)
        self.addAction(close_tab_action)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    browser.tabs.currentWidget().url_bar.setFocus()  # Automatycznie ustawia fokus na polu URL
    sys.exit(app.exec())