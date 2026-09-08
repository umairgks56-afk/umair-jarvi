Option Explicit

Dim shell, fso, startup, path
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
startup = shell.SpecialFolders("Startup")
path = startup & "\JARVIS.lnk"
If fso.FileExists(path) Then fso.DeleteFile path, True
WScript.Echo "JARVIS Windows startup disabled."
