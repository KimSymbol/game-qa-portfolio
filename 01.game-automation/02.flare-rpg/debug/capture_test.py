import win32gui
import win32ui
import win32con
import cv2
import numpy as np
from ctypes import windll

hwnd = win32gui.FindWindow(None, "Flare")
print(f"hwnd: {hwnd}")

left, top, right, bottom = win32gui.GetWindowRect(hwnd)
width = right - left
height = bottom - top
print(f"창 크기: width={width}, height={height}")

# 캡처
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

_, buf = cv2.imencode(".png", img)
buf.tofile("debug/capture_test.png")
print("저장 완료!")