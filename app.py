import os, sys, subprocess, traceback, uuid, random;

BROWSER_PATH = os.path.dirname(os.path.realpath(__file__));
os.environ["BROWSER_PATH"] = BROWSER_PATH;
os.environ["BROWSER_SECURE"] = "0";

from PySide6.QtWidgets import QApplication
from browser.browser import Browser;
from browser.form_login import FormLogin;

# def randomico(total):
#     array = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q"];
#     retorno = "";
#     for i in range(total):
#         retorno += array[random.randint(0, len(array) - 1)];
#     return retorno;

# def text_directory_create():
#     try:
#         name_test = randomico(5);
#         password  = randomico(5);
#         cmd = "/bin/bash " + BROWSER_PATH + "/bash/create.sh " + name_test + " 1 " + password;
#         subprocess.run(cmd, shell=True);
#         return True;
#     except:
#         traceback.print_exc();
#         return False;
# def test():
#     if not os.path.exists("/usr/sbin/cryptsetup"):
#         return False;
#     return True;


def main():
    app = QApplication(sys.argv)
    f = FormLogin();
    f.exec();
    if f.diretorio == None:
        f.diretorio = os.path.expanduser("~");
    browser = Browser(f.diretorio)
    browser.show()
    #browser.tabs.currentWidget().url_bar.setFocus() passar isso lá para classe Browser
    sys.exit(app.exec());

if __name__ == "__main__":
    
    #if os.name != 'nt' and test() and text_directory_create():
    #    os.environ["BROWSER_SECURE"] = "1";

    main();


# #!/bin/bash
# # ./create_volume.sh
# # Criar um volume virtual criptografaod, o usuario nao sabe a senha
# # do volume para evitar que ele seja coagido para falar.

# createopen(){
#     dd if=/dev/urandom of=/tmp/$1.img bs=1M count=$(( $2 * 120  ))
#     /usr/sbin/cryptsetup luksFormat /tmp/$1.img <<< 'YES' <<< "$3" <<< "$3"
#     echo -n "$3" | /usr/sbin/cryptsetup open --type luks /tmp/$1.img $1
#     mkfs.ext4 -L $1 /dev/mapper/$1
#     /usr/sbin/cryptsetup close $1
#     echo -n "$3" | /usr/sbin/cryptsetup open --type luks /tmp/$1.img $1
#     mkdir /tmp/$1
#     mount /dev/mapper/$1 /tmp/$1
#     echo "Sucesso" > /tmp/$1/status.txt
#     chown -R $SUDO_USER:$SUDO_USER "/tmp/$1/"
# }
# #1 = nome do arquivo/diretorio
# #2 = tamanho em GB
# #3 = Password do volume
# createopen $1 $2 $3

# # REFERENCIA:
# #https://serverfault.com/questions/513605/how-to-non-interactively-supply-a-passphrase-to-dmcrypt-luksformat
# #https://opensource.com/article/21/4/linux-encryption