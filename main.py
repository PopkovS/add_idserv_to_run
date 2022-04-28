# -*- coding: utf-8 -*-
import sys
from time import sleep
from rich.console import Console
from rich import print, spinner

import PySimpleGUI as sg
from console import get_paths
from makeself import raw_makeself
from makeself_header import raw_makeself_header
import os
import threading
import subprocess

tmp_path = '/tmp/run_upd/'
# idserv_path = tmp_path + 'id/'
idserv_path = tmp_path + 'id/opt'
id_inf = 'idserver.info'
ms = 'makeself.sh'
ms_header = 'makeself-header.sh'

blue = '#1f96f3'
strong_gray = '#263238'
but_gray = '#808080'
white = '#FFFFFF'
red = '#FFA07A'
green = '#00FF7F'
return_code = 0

brief = """[MAIN] 
Укажите адрес и порт собственного ID-сервера

[VERIFY] 
При использовании корневого сертификата ОС включите параметр ServerVerify, при использовании собственного сертификата включите оба параметра

[PROXY] 
При использовании прокси-сервера укажите в параметре USE_KIND=3, затем укажите адрес:порт и при необходимости логин с паролем

[HWID] 
Для гарантии уникальности идентификатора включите параметр
"""

id_conf = """
[MAIN]
IDSERVER=
PORT=
FORCE_REPLACE=1

[VERIFY]
ServerVerify=0
ServerVerifyCA=0

[PROXY]
USE_KIND=1
SERVER=
USER=
PASSW=

[HWID]
HwidKeyUsed=
"""


def info_popup(text, header=' ', non_blocking=False, auto_close=False, text_color=None, location=(None, None),
               no_titlebar=True, grab_anywhere=True):
    sg.popup_no_buttons(text,
                        title=header,
                        non_blocking=non_blocking,
                        font=('', 10, ''),
                        auto_close=auto_close,
                        grab_anywhere=grab_anywhere,
                        no_titlebar=no_titlebar,
                        auto_close_duration=2,
                        text_color=text_color,
                        background_color=strong_gray,
                        keep_on_top=True,

                        location=location
                        # relative_location=r_location
                        )


def error_message(text, color=red):
    text_ahead_start.update(text, text_color=color)
    sleep(2)
    if text_ahead_start.get() == text:
        text_ahead_start.update('')


def create_temp_file(path, file_name, text):
    # os.system(f'[[ -d {path} ]] || mkdir -p {path}  > /dev/null')
    subprocess.run(f'[[ -d {path} ]] || mkdir -p {path}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    file = open(path + file_name, 'w', encoding='utf-8')
    file.write(text)
    # os.system(f'chmod 755 {path}{file_name}  > /dev/null')
    subprocess.run(f'chmod 755 {path}{file_name}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    file.close()


def check_path(path, end_name='.run', name_file=''):
    err_report = list()
    if path:
        if os.path.isfile(path):
            None if path.endswith(end_name) else err_report.append(
                f'{name_file}Требуется файл с расширением "{end_name}"')
        else:
            if len(path) > 44:
                path = '...' + path[-44:]
            err_report.append(f'{name_file}"{path}" - указанный путь не существует')
    else:
        err_report.append(f'{name_file}Необходимо указать путь к файлу')
    return err_report


def add_ids_into_arch(result_path, idsrv):
    create_temp_file(tmp_path, ms, raw_makeself)
    create_temp_file(tmp_path, ms_header, raw_makeself_header)
    create_temp_file(idserv_path, id_inf, idsrv)
    result = os.system(f'{tmp_path}{ms} --append {idserv_path} {result_path} > /dev/null')
    os.system(f'chmod 755 {result_path}  > /dev/null')
    os.system(f'rm -rf {tmp_path} > /dev/null')
    return result


def gui_add_idserv(result_path, idsrv):
    return_code = add_ids_into_arch(result_path, idsrv)
    start_butt.update(disabled=False)
    id_field.update(disabled=False)
    text_ahead_start('')
    window.refresh()
    return return_code


def copy_rcm(element):
    try:
        text = element.Widget.selection_get()
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(text)
    except:
        print('Nothing selected')


right_click_menu_id = ['', [' ', 'Очистить', 'Копировать::ID_COPY', 'Вставить::ID_PASTE']]
right_click_menu_run_path = [' ', ['Копировать::PATH_RUN_COPY', 'Вставить::PATH_RUN_PASTE']]
sg.theme('DarkGrey4')

rcm_dict = {'ID_COPY': 'idservinfo', 'ID_PASTE': 'idservinfo',
            'PATH_RUN_COPY': 'path_to_run', 'PATH_RUN_PASTE': 'path_to_run'}

start_butt = sg.Button('подготовить', key='start', size=(16, 1), font=('', 9, 'bold'), button_color=('', blue))
text_ahead_start = sg.Text('', key='wait',
                           background_color=strong_gray,
                           expand_x=True, justification='center',
                           auto_size_text=True
                           )
id_field = sg.Multiline(id_conf, key='idservinfo', size=(12, 19), expand_x=True, font=('', 12, ''),
                        border_width=1,
                        no_scrollbar=True,
                        right_click_menu=right_click_menu_id,
                        focus=True,
                        background_color=white)

layout = [

    [sg.Text('Файл assistant.run:', background_color=strong_gray, font=('', 10, '')),
     sg.Text('', expand_x=True, background_color=strong_gray),
     ],
    [sg.InputText(key="path_to_run",
                  size=(45, 3),
                  font=('', 12, ''),
                  expand_x=True,
                  border_width=1,
                  right_click_menu=right_click_menu_run_path,
                  background_color=white),
     sg.FileBrowse(key="open_explorer", target="path_to_run",
                   button_text='...', button_color=('', but_gray), size=(4, 1),
                   file_types=(('installer', '*.run'),))],
    [id_field],
    [text_ahead_start],
    [start_butt,
     sg.Text(text='', size=(13, 1), background_color=strong_gray, expand_x=True),
     sg.Button('справка', key='info', size=(16, 1), button_color=('', but_gray), font=('', 9, 'bold'))]]

window = sg.Window('', layout, icon='./helper.ico',
                   titlebar_icon='./helper.ico',
                   background_color=strong_gray,
                   keep_on_top=False
                   )


def gui_app():
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'close'):
            break

        x, y = window.current_location(more_accurate=True)
        size_x, size_y = window.current_size_accurate()

        if event == 'start':
            result_path = values['path_to_run']
            errors = check_path(result_path)
            if not errors:
                text_idserv = values['idservinfo']
                start_butt.update(disabled=True)
                id_field.update(disabled=True)
                text_ahead_start('Ожидайте...', text_color=white)
                window.perform_long_operation(lambda: gui_add_idserv(result_path, text_idserv), "FUNC_COMPLETE")
            else:
                threading.Thread(target=error_message, args=('\n\n'.join(errors),), daemon=True).start()
                continue

        if event == "FUNC_COMPLETE":
            if values["FUNC_COMPLETE"]:
                info_popup("   "+"Произошла непредвиденная ошибка!", location=(x, y + int(size_y) / 2),
                           text_color=red, auto_close=True, grab_anywhere=False)
            else:

                info_popup("   "+"Изменения успешно внесены", location=(x, y + int(size_y) / 2),
                           text_color=green, auto_close=True, grab_anywhere=False)

        if event == 'info':
            info_popup(brief, 'Справка', location=(x + size_x, y), no_titlebar=False, non_blocking=True)

        if event.startswith('Копировать'):
            el = rcm_dict[event.split('::')[1]]
            copy_rcm(window[el])
        if event.startswith('Вставить'):
            el = rcm_dict[event.split('::')[1]]
            try:
                window[el].Widget.insert(sg.tk.INSERT, window.TKroot.clipboard_get())
            except:
                pass
        if event == 'Очистить':
            window['idservinfo'].update(id_conf)
    window.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        console = Console()
        idsrv_path, result_path = get_paths()
        errors = check_path(idsrv_path, end_name='', name_file='idserver.info: [bold red]') + \
                 check_path(result_path, name_file='assistant.run: [bold red]')
        with console.status('Выполнение...', spinner='dots'):
            console.print('Поиск ошибок')
            if errors:
                for er in errors:
                    console.print(er + '[/]')
                console.print('\n', 'Для справки используйте опцию "--help"', sep='')
            else:
                try:
                    id_text = open(idsrv_path, 'r', encoding='utf8').read()
                except UnicodeDecodeError as err:
                    console.print(f'Ошибка чтения {idsrv_path}')
                    console.print(err)
                    sys.exit(1)

                console.print('Пересборка приложения')
                res = add_ids_into_arch(result_path, id_text)
                if res:
                    console.print('[bold red]Произошла непредвиденная ошибка[/]')
                    sys.exit(1)
                else:
                    console.print('[bold green]Изменения успешно внесены[/]')
                    sys.exit(0)
    else:
        gui_app()
