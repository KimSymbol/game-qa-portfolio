# debug/test_matching.py
import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from ctypes import windll

def capture_game():
    """게임 창 직접 캡처"""
    hwnd = win32gui.FindWindow(None, "Flare")
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)
    windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)
    bmp_info = bitmap.GetInfo()
    bmp_arr = bitmap.GetBitmapBits(True)
    img = np.frombuffer(bmp_arr, dtype=np.uint8)
    img = img.reshape(bmp_info["bmHeight"], bmp_info["bmWidth"], 4)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    return img

def find_template(screen, template_path, threshold=0.8):
    """템플릿 매칭"""
    arr = np.fromfile(template_path, dtype=np.uint8)
    template = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if template is None:
        print(f"템플릿 로드 실패: {template_path}")
        return False
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    print(f"[{template_path}] 유사도: {max_val:.3f} → {'✅ 발견!' if max_val >= threshold else '❌ 미발견'}")
    return max_val >= threshold

# 메인메뉴 상태에서 실행
screen = capture_game()
find_template(screen, "assets/templates/logo.png")
find_template(screen, "assets/templates/play_game.png")