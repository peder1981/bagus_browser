
import tldextract, sys, uuid, json, os, importlib
#import logging

BROWSER_PATH = os.environ["BROWSER_PATH"];
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QListWidget, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl;

from browser.api.project_helper import ProjectHelper;
from browser.ui.custom_web_engine_page import CustomWebEnginePage;

DEBUG_PORT = '5588'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT
HISTORY_FILE = "history.json"

class BrowserTab(QWidget):
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
        #self.web_view.contextMenuEvent.connect(self.contextMenuEvent_);
        
        #self.web_view.loadStarted.connect(self.on_load_started_signal)
        # montar a barrinha com botoes==============
        ly = QHBoxLayout();
        
        bt1 = QPushButton("Inspector");
        ly.addWidget(bt1);
        bt1.clicked.connect(self.bt1_click);

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
    #def contextMenuEvent_(self, event):
    #    self.menu = self.web_view.page().createStandardContextMenu()
    #    self.menu.addAction('My action')
    #    self.menu.popup(event.globalPos())

    def bt1_click(self):
        self.inspector = QWebEngineView()
        self.inspector.setWindowTitle('Web Inspector')
        self.inspector.load(QUrl(DEBUG_URL))

        self.web_view.page().setDevToolsPage(self.inspector.page())
        self.inspector.show()

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
                }, 1000);

                setInterval(function() { 
            var $cross = document.getElementsByClassName("ytp-ad-overlay-close-container")[0]; 
            var $skip = document.getElementsByClassName("ytp-ad-skip-button")[0]; 
            if ($cross != undefined) $cross.click(); 
            if ($skip != undefined) $skip.click() 
            }, 2000);

            
            (function() {
                'use strict';

                const CHECK_INTERVAL = 500; // ms between checks

                function skipAd() {
                    const skipButtons = [
                        '.ytp-ad-skip-button-modern',
                        '.ytp-skip-ad-button',
                        'button[aria-label^="Skip ad"]'
                    ];

                    for (const selector of skipButtons) {
                        const button = document.querySelector(selector);
                        if (button && button.offsetParent !== null) {
                            button.click();
                            return;
                        }
                    }

                    // Seek through unskippable ads
                    const video = document.querySelector('video');
                    if (video && document.querySelector('.ad-showing, .ad-interrupting')) {
                        video.currentTime = video.duration - 0.1;
                    }
                }

                setInterval(skipAd, CHECK_INTERVAL);
                document.addEventListener('yt-navigate-finish', skipAd);
            })();

            """
            print("INFO: ", "Iniciado um javascript para pular ADS do youtube na URL: ", self.url_bar.text());
            self.web_view.page().runJavaScript(javascript);
        else:
            javascript = """
                function getElementByXPath(path) {
                  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                }

                var elemento1 = getElementByXPath("//*[contains(@class, 'van_vid_carousel')]");
                var elemento2 = getElementByXPath("//*[contains(@class, 'newsletter-form__wrapper')]") ;
                var elemento3 = getElementByXPath("//*[contains(@class, 'dfp-leaderboard-container')]") ;

                console.log(elemento1, elemento2, elemento3);
                elemento1.remove();
                elemento2.remove();
                elemento3.remove();
            """
            self.web_view.page().runJavaScript(javascript);
            print("INFO: ", "Iniciado o remover carretel: ", self.url_bar.text());

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
        index = -1;
        for i in range(self.browser.tabs.count()):
            if self.browser.tabs.widget(i) == self:
                index = i;
                break;
        if index >= 0:
            self.browser.tabs.setTabText( index , extracted.domain);
    
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
