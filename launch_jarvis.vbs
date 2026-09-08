Option Explicit

Dim shell, fso, root, agentDir, pythonExe, apiCmd, voiceCmd, ollamaCheck, rc
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(WScript.ScriptFullName)
agentDir = root & "\agent"
pythonExe = root & "\.venv\Scripts\python.exe"

If Not fso.FileExists(pythonExe) Then
    MsgBox "JARVIS is not installed yet. Run INSTALL_JARVIS.bat first.", 48, "JARVIS"
    WScript.Quit 1
End If

' Start Ollama only when its local server is not responding.
ollamaCheck = shell.Run("cmd /c ollama list >nul 2>&1", 0, True)
If ollamaCheck <> 0 Then
    shell.Run "cmd /c start ""Ollama"" ollama serve", 0, False
    WScript.Sleep 5000
End If

apiCmd = "cmd /c cd /d """ & agentDir & """ && """ & pythonExe & """ -m uvicorn api:app --host 127.0.0.1 --port 8765"
voiceCmd = "cmd /c cd /d """ & agentDir & """ && """ & pythonExe & """ -m voice.loop"

' Hidden processes: no permanent CMD windows are shown.
shell.Run apiCmd, 0, False
WScript.Sleep 2500
shell.Run voiceCmd, 0, False
WScript.Sleep 1200

' Open the JARVIS dashboard in the default browser.
shell.Run "http://127.0.0.1:8765", 1, False

Set shell = Nothing
Set fso = Nothing
