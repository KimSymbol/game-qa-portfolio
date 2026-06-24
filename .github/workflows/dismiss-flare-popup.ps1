# Flare 게임 시작 시 뜨는 알림창의 Continue 버튼 자동 클릭
# 알림창이 없으면 정상 진행

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

# 알림창 등장 대기 (최대 5초)
$hwnd = 0
for ($i = 0; $i -lt 10; $i++) {
    # 알림창은 Windows 표준 Dialog (클래스명 #32770)
    $hwnd = [Win32]::FindWindow("#32770", "Flare")
    if ($hwnd -ne 0) {
        break
    }
    Start-Sleep -Milliseconds 500
}

if ($hwnd -ne 0) {
    Write-Host "알림창 발견 (hwnd: $hwnd), Continue 클릭"
    [Win32]::SetForegroundWindow($hwnd)
    Start-Sleep -Milliseconds 500

    # Tab x3 으로 Continue 버튼 이동 후 Enter
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