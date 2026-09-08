Option Explicit

Dim shell, fso, root, desktop, startup, shortcut, target
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(WScript.ScriptFullName)
desktop = shell.SpecialFolders("Desktop")
startup = shell.SpecialFolders("Startup")

target = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\wscript.exe")

Set shortcut = shell.CreateShortcut(desktop & "\JARVIS.lnk")
shortcut.TargetPath = target
shortcut.Arguments = Chr(34) & root & "\launch_jarvis.vbs" & Chr(34)
shortcut.WorkingDirectory = root
shortcut.Description = "Start JARVIS - Umair's Personal Assistant"
shortcut.Save

Set shortcut = shell.CreateShortcut(desktop & "\JARVIS - Stop.lnk")
shortcut.TargetPath = root & "\STOP_JARVIS.bat"
shortcut.WorkingDirectory = root
shortcut.Description = "Stop JARVIS background services"
shortcut.Save

WScript.Echo "JARVIS desktop shortcuts created."
