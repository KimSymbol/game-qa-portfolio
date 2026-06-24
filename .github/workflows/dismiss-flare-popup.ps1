# Flare 게임 시작 시 뜨는 알림창의 Continue 버튼 자동 클릭

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
}
"@

# 알림창 등장 대기 (최대 5초)
$hwnd = 0
for ($i = 0; $i -lt 10; $i++) {
    $hwnd = [Win32]::FindWindow("#32770", "Flare")
    if ($hwnd -ne 0) {
        break
    }
    Start-Sleep -Milliseconds 500
}

if ($hwnd -ne 0) {
    Write-Host "알림창 발견 (hwnd: $hwnd), 포커스 이동 시도"

    # 강제 최상위 + Alt 키 트릭 (Flappy Bird 때 검증된 방법)
    $HWND_TOPMOST = [IntPtr]::new(-1)
    $HWND_NOTOPMOST = [IntPtr]::new(-2)
    $SWP_NOMOVE = 0x0002
    $SWP_NOSIZE = 0x0001

    # 1. 최상위로 설정
    [Win32]::SetWindowPos($hwnd, $HWND_TOPMOST, 0, 0, 0, 0, $SWP_NOMOVE -bor $SWP_NOSIZE)

    # 2. Alt 키 트릭 (포커스 이동 우회)
    $VK_MENU = 0x12  # Alt 키 가상 코드
    $KEYEVENTF_KEYUP = 0x0002
    [Win32]::keybd_event($VK_MENU, 0, 0, [UIntPtr]::Zero)               # Alt 누름
    [Win32]::SetForegroundWindow($hwnd)                                  # 포커스 이동
    [Win32]::keybd_event($VK_MENU, 0, $KEYEVENTF_KEYUP, [UIntPtr]::Zero) # Alt 뗌

    # 3. 최상위 해제
    [Win32]::SetWindowPos($hwnd, $HWND_NOTOPMOST, 0, 0, 0, 0, $SWP_NOMOVE -bor $SWP_NOSIZE)

    Start-Sleep -Milliseconds 500

    # Tab x3 + Enter 로 Continue 클릭
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "Continue 클릭 완료"
} else {
    Write-Host "알림창 미발견 (정상 실행)"
}