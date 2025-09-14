import tldextract, sys, uuid, json, os, importlib

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QDialog, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtWebEngineCore import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent);
        self.bloqueios = [ "gstatic.com", "doubleclick.net", "googlesyndication.com", "metrike.com.br", "dtrafficquality.google", "metrike.com.br"];
        self.download_ext = ["iso", "zip", "gz"];
        self.certificateError.connect( self.certificateError_signal );
    
    def certificateError_signal(self, qwebenginecertificateerror):
        pass;#<PySide6.QtWebEngineCore.QWebEngineCertificateError object at 0x7f07e0445c80>
    
    def javaScriptConsoleMessage(self, javaScriptConsoleMessageLevel, message, lineNumber, sourceID):
        pass;
        #print("\033[91mCONSOLE:", javaScriptConsoleMessageLevel, message, lineNumber, sourceID, "\033[0m");
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        pass;
        #print(f"\033[94mJS Console ({level.name}):\033[0m {message} (Line: {lineNumber}, Source: {sourceId})")
    
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        for bloqueio in self.bloqueios:
            if url.toString().find( bloqueio ) > 0:
                if _type == QWebEnginePage.NavigationType.NavigationTypeTyped or _type == QWebEnginePage.NavigationType.NavigationTypeRedirect:
                    dlg = QDialog()
                    dlg.setWindowTitle(bloqueio)
                    dlg.exec()
                    break;
                else:
                    print("\033[91mBLOQUEIO:", _type, bloqueio, "\033[0m");
                    return False;
        return super().acceptNavigationRequest(url, _type, isMainFrame)
