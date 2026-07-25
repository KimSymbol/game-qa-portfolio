import win32gui

hwnd = win32gui.FindWindow(None, "Flare")
left, top, right, bottom = win32gui.GetWindowRect(hwnd)
print(f"전체 창: left={left}, top={top}, right={right}, bottom={bottom}")
print(f"전체 창 크기: width={right-left}, height={bottom-top}")

# 클라이언트 영역 (상단바 제외)
import win32api
rect = win32gui.GetClientRect(hwnd)
print(f"클라이언트 영역: {rect}")