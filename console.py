import subprocess
import argparse

example_id = """
Файл "idserver.info" необходимо подготовить заранее. 
Для заполнения "idserver.info" используйте следующий шаблон:

# Укажите адрес и порт собственного ID-сервера:
[MAIN]
IDSERVER=
PORT=
FORCE_REPLACE=1

# При использовании корневого сертификата ОС включите параметр ServerVerify=1, при использовании собственного сертификата включите оба параметра:
[VERIFY]
ServerVerify=0
ServerVerifyCA=0

# При использовании прокси-сервера укажите в параметре USE_KIND=3, затем укажите адрес:порт и при необходимости логин с паролем:
[PROXY]
USE_KIND=1
SERVER=
USER=
PASSW=

# Для гарантии уникальности идентификатора включите параметр:
[HWID]
HwidKeyUsed=
"""


def get_paths():
    parser = argparse.ArgumentParser(description='Для работы в графическом режиме запустите приложение без аргументов.',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=example_id)
    parser.add_argument('idserver_info_path', type=str, help='- Location of "idserver.info" file')
    parser.add_argument('assistant_run_path', type=str, help='- Location of "assistant.run" file')

    args = parser.parse_args()
    return args.idserver_info_path, args.assistant_run_path
