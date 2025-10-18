import tldextract, sys, uuid, json, os, importlib
import threading

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QDialog, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtWebEngineCore import QWebEnginePage
from browser.api.logger_helper import *

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent);
        self.download_ext = [".iso", ".zip", ".gz", ".png", ".jpg", ".json"];
        self.certificateError.connect( self.certificateError_signal );
        self.urlChanged.connect(self.urlChanged_signal);
        self.loadStarted.connect(self.loadStarted_signal);
        self.logger_javascript = setup_logger( "javascript", os.path.join( os.environ["USER_BROWSER_PATH"], "log", "javascript.log"));
    def loadStarted_signal(self):
        pass;
    def navigationRequested(self, request):
        print("Request", request);
        pass;
    def newWindowRequested(self, request):
        print("Request", request);
        pass;
    def urlChanged_signal(self, url):
        pass;
    def on_navigate_signal(self):
        pass;
    def certificateError_signal(self, qwebenginecertificateerror):
        pass;#<PySide6.QtWebEngineCore.QWebEngineCertificateError object at 0x7f07e0445c80>
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        #print("("+ str(level) +") - " + message + " => " + sourceId + "("+ str(lineNumber) +")");
        self.logger_javascript.info( "("+ str(level) +") - " + message + " => " + sourceId + "("+ str(lineNumber) +")" );
        pass;
    #def javaScriptPrompt(securityOrigin, msg, defaultValue, result):
    #    print(">>>>>>>", securityOrigin, msg, defaultValue, result );
    def download_file(self, url, path):
        try:
            #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'}
            #response = requests.get(url, headers=headers)
            #totalbits = 0
            #if response.status_code == 200:
            #    with open(path, 'wb') as f:
            #        for chunk in response.iter_content(chunk_size=4096):
            #            if chunk:
            #                totalbits += 4096
            #                print("Downloaded",totalbits*4096,"KB...")
            #                f.write(chunk)
            return True;
        except:
            traceback.print_exc();
        if os.path.exists(path):
            os.unlink(path);
        return False;
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        extensao_index = url.toString().rfind( "." );
        extensao = None;
        if extensao_index > 0:
            extensao = url.toString()[extensao_index:];
            arquivo = url.toString()[url.toString().rfind( "/" ) + 1:];
            if extensao in self.download_ext:
                path_file = os.path.join( os.path.expanduser("~/Downloads"), arquivo );
                if not os.path.exists(path_file):
                    t1 = threading.Thread(target=self.download_file, args=(url.toString(), path_file, ));
                    t1.start();
        return super().acceptNavigationRequest(url, _type, isMainFrame)
