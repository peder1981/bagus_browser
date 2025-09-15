import tldextract, sys, uuid, json, os, importlib
import threading, requests

BROWSER_PATH = os.environ["BROWSER_PATH"]
sys.path.append( BROWSER_PATH );

from PySide6.QtWidgets import QLayout, QDialog, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtWebEngineCore import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent);
        self.bloqueios = [ "gstatic.com", "doubleclick.net", "googlesyndication.com", "metrike.com.br", "dtrafficquality.google", "metrike.com.br"];
        self.download_ext = [".iso", ".zip", ".gz", ".png", ".jpg", ".json"];
        self.certificateError.connect( self.certificateError_signal );
    
    def certificateError_signal(self, qwebenginecertificateerror):
        pass;#<PySide6.QtWebEngineCore.QWebEngineCertificateError object at 0x7f07e0445c80>
    
    def javaScriptConsoleMessage(self, javaScriptConsoleMessageLevel, message, lineNumber, sourceID):
        pass;
        #print("\033[91mCONSOLE:", javaScriptConsoleMessageLevel, message, lineNumber, sourceID, "\033[0m");
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        pass;
        #print(f"\033[94mJS Console ({level.name}):\033[0m {message} (Line: {lineNumber}, Source: {sourceId})")
    def download_file(self, url, path):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'}
            response = requests.get(url, headers=headers)
            totalbits = 0
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            totalbits += 4096
                            print("Downloaded",totalbits*4096,"KB...")
                            f.write(chunk)
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
                print(path_file, os.path.exists(path_file));
                if not os.path.exists(path_file):
                    t1 = threading.Thread(target=self.download_file, args=(url.toString(), path_file, ));
                    t1.start();
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
