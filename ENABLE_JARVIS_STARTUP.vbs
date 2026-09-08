Option Explicit

Dim shell, fso, root, startup, shortcut, target
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(WScript.ScriptFullName)
startup = shell.SpecialFolders("Startup")
target = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\wscript.exe")

Set shortcut = shell.CreateShortcut(startup & "\JARVIS.lnk")
shortcut.TargetPath = target
shortcut.Arguments = Chr(34) & root & "\launch_jarvis.vbs" & Chr(34)
shortcut.WorkingDirectory = root
shortcut.Description = "Start JARVIS automatically at Windows sign-in"
shortcut.Save

WScript.Echo "JARVIS Windows startup enabled."
