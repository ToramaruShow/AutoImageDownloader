import os
import PySimpleGUI as sg
import time
import requests

result = []
header = ['  Name  ', '   Time  ', '  Size  ', ' Result ']
estimated = 0
SizeLst = {
    'BTN': (20, 1),
    'RUN': (10, 1),
    'URL': (6, 1),
    'URLINP': (44, 1),
    'AMO': (6, 1),
    'AMOINP': (16, 1),
    'OPT': (6, 1),
    'OPTINP': (16, 1),
    'CB': (7, 1),
    'TBL': (1, 10),
    'RI': (19, 1)
}

keyName = {
    'JPG': '-JPG-',
    'JPEG': '-JPE-',
    'PNG': '-PNG-',
    'GIF': '-GIF-'}

ModeCB = [[sg.Checkbox('jpg', key=keyName['JPG'], default=True, size=SizeLst['CB'], ),
           sg.Checkbox('jpeg', key=keyName['JPEG'], default=False, size=SizeLst['CB'], ),
           sg.Checkbox('png', key=keyName['PNG'], default=False, size=SizeLst['CB'], ),
           sg.Checkbox('gif', key=keyName['GIF'], default=False, size=SizeLst['CB'], )]]

PrcBtn = [[sg.Button('Save', size=SizeLst['RUN'], key='-SAVE-'),
           sg.Button('Calc   Time & Size', size=SizeLst['BTN'], key='-TIME-'),
           sg.Button('Quit', size=SizeLst['RUN'], key='-QUIT-')]]

layout = [[sg.Text('URL', size=SizeLst['URL']), sg.InputText(size=SizeLst['URLINP'], key='-URL-')],
          [sg.Text('Amount', size=SizeLst['AMO']), sg.InputText(size=SizeLst['AMOINP'], key='-AMO-'),
           sg.Text('Start', size=SizeLst['AMO']), sg.InputText(size=SizeLst['AMOINP'], key='-STR-')],
          [sg.Text('Prefix ', size=SizeLst['OPT']), sg.InputText(size=SizeLst['OPTINP'], key='-PRE-'),
           sg.Text('Suffix ', size=SizeLst['OPT']), sg.InputText(size=SizeLst['OPTINP'], key='-SUF-')],
          [sg.Frame('Select Extension', ModeCB)],
          [[sg.Table(result, headings=header, size=SizeLst['TBL'], key='-TBL-')],
           sg.Frame('Process', PrcBtn),
           [[sg.Text('Estimated Processing Time'), sg.Text('00H 00M 00S', key='-EPT-')],
            [sg.Text('Total         Processing Time'), sg.Text('00H 00M 00S', key='-TPT-')]],
           [sg.Text('Request Interval (1 = 0.1s)', size=SizeLst['RI']), sg.InputText(size=SizeLst['AMO'], key='-RI-')],
           [sg.Text('Estimated Size', size=SizeLst['RI']), sg.Text('00000MB', size=SizeLst['RI'], key='-ES-')],
           [sg.Text('Total         Size', size=SizeLst['RI']), sg.Text('00000MB', size=SizeLst['RI'], key='-TS-')]]]

window = sg.Window('AutoDownloader', layout)

while True:
    event, values = window.read()
    if event == "-QUIT-" or event == sg.WIN_CLOSED:
        break
    if event == "-SAVE-" or event == "-TIME-":
        Integer, Caution = False, False
        if values['-URL-'] == "":
            sg.popup("Item [URL] is blank")
        if values['-STR-'] == "":
            sg.popup("Item [Start] is blank")
        if values['-AMO-'] == "":
            sg.popup("Item [Amount] is blank")
        if values['-RI-'] == "":
            sg.popup("Item [Request Interval] is blank")
        elif values['-RI-'].isdecimal():
            Integer = True
            if int(values['-RI-']) < 0.1:
                Caution = True  # DOS攻撃になりそうなリクエスト送信間隔に対する警告
        else:
            sg.popup("Item [Request Interval] is not a number")
        if values['-JPG-'] is False and values['-JPE-'] is False \
                and values['-PNG-'] is False and values['-GIF-'] is False:
            sg.popup("No Extension Selected")
        if Caution:
            ans = sg.popup_yes_no(
                "Request sending interval is short\n"
                + "This will put a load on the destination server.Are you sure?\n"
                + "It is your own responsibility even if you get IPBAN etc.")
            if ans == "Yes":
                Caution = False
        if Caution is False and values['-URL-'] != "" and values['-STR-'] != "" \
                and values['-AMO-'] != "" and values['-RI-'] != "":
            # sg.popup("Start saving the image\nPlease Wait...")
            time1 = time.time()
            url = values['-URL-'] + "/"
            file_name = "."  # 保存ファイル名　「.jpg」だけなのは左側には番号　右側には拡張子(jpg png gifを指定せずに保存可能)
            prefix = values['-PRE-']  # 数字の前に付いてる文字
            suffix = values['-SUF-']  # 数字の後に付いてる文字
            folder_path = "DownloadFolder/" + url.replace("https://", "") + "/"  # 保存場所　URLにしたがって保存される
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/58.0.3029.110 Safari/537.36'}  # Error403対策
            start = int(values['-STR-']) + estimated  # 保存番号のスタート地点設定
            length = int(values['-AMO-'])  # 保存数
            memo_length = int(values['-AMO-'])  # 計算用
            if event == "-TIME-":
                length = 10
                estimated += 10
            request_time = int(values['-RI-']) / 10  # 保存間隔 0.秒(リクエスト送信間隔)

            jpg, jpeg, png, gif = True, True, True, True
            if str(values['-JPG-']) == "False":
                jpg = False
            if str(values['-JPE-']) == "False":
                jpeg = False
            if str(values['-PNG-']) == "False":
                png = False
            if str(values['-GIF-']) == "False":
                gif = False
            # フォルダが存在しない場合は作成する
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            error = False  # 4種の拡張子でやってなかった場合
            not_found_img = True  # そもそも画像がないor拡張子未選択
            response = ""

            extension = []  # サーチする拡張子
            if jpg:
                extension.append("jpg")
            if jpeg:
                extension.append("jpeg")
            if png:
                extension.append("png")
            if gif:
                extension.append("gif")

            try:
                check = len(extension)
                for ext in extension:
                    response = requests.get(url + values['-STR-'] + "." + ext, headers=headers)  # まずは画像があるか確認
                    content_type = response.headers["content-type"]
                    file_path = os.path.join(folder_path, file_name)
                    check -= 1
                    if "image" in content_type:
                        not_found_img = False
                        break
                    elif not_found_img and check == 0:
                        sg.popup(Exception("Error! [URL] may be wrong: " + str(content_type)))
                    time.sleep(0.25)
            except:
                sg.popup("There is something wrong with [URL]\n[URL] may be wrong")
                not_found_img = True

            savenum = start  # 0からカウント

            if not_found_img is False:
                memo = file_name
                data_size = 0
                while length + start > savenum:
                    time3 = time.time()
                    file_name = prefix + str(savenum) + suffix + file_name
                    error = True
                    for ext in extension:
                        file_name = file_name.replace("jpg", "")
                        file_name = file_name.replace("jpeg", "")
                        file_name = file_name.replace("png", "")
                        file_name = file_name.replace("gif", "")
                        file_name = file_name + ext
                        file_path = os.path.join(folder_path, file_name)
                        response = requests.get(url + file_name, headers=headers)
                        if response.status_code == 200:
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                                print("Success Save Image! \n  FileName: " + file_name)
                                error = False
                                break
                    if error:
                        err = Exception("Error: " + str(response.status_code) + "\n   FileName: " + file_name)
                        print(err)
                    savenum += 1
                    time.sleep(request_time)
                    time4 = time.time()
                    time_result = int(((time4 - time3) % 3600) % 60)
                    if error:
                        result.insert(0, [file_name, str(time_result) + " S", "N/A",
                                          "Failed " + str(response.status_code)])
                    else:
                        size = int((os.path.getsize("./" + folder_path + "/" + file_name)) / 1000)
                        data_size += size
                        result.insert(0, [file_name, str(time_result) + " S", str(size) + "KB", "Success"])
                    file_name = memo
                time2 = time.time()
                if event == "-TIME-":
                    time_change = int((time2 - time1) * ((memo_length - estimated) / 10))
                else:
                    time_change = int(time2 - time1)
                H = int(time_change / 3600)
                HH, MM, SS = "", "", ""
                if H < 10:
                    HH = "0"
                time_change = time_change % 3600
                M = int(time_change / 60)
                if M < 10:
                    MM = "0"
                time_change = time_change % 60
                S = int(time_change)
                if S < 10:
                    SS = "0"
                if event == "-TIME-":
                    window['-EPT-'].update(HH + str(H) + "H " + MM + str(M) + "M " + SS + str(S) + "S")
                    window['-ES-'].update(str(int((data_size / 1000) * (memo_length / 10))) + "MB")
                else:
                    window['-TPT-'].update(HH + str(H) + "H " + MM + str(M) + "M " + SS + str(S) + "S")
                    window['-TS-'].update(str(int(data_size / 1000)) + "MB")
                window['-TBL-'].update(result)
                sg.popup("Finish SaveImages!\nFileLink: " + folder_path[:-1])
