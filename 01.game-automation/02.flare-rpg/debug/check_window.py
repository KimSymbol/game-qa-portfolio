# check_window.py 로 저장 후 실행
import pygetwindow as gw

windows = gw.getAllTitles()
for w in windows:
    if w:
        print(w)