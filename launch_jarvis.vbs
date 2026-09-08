Option Explicit

Dim shell, fso, root, agentDir, pythonExe, apiCmd, voiceCmd, ollamaCheck, apiReady, proc, dataDir, voiceLog
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(WScript.ScriptFullName)
agentDir = root & "\agent"
dataDir = agentDir & "\data"
voiceLog = dataDir & "\voice.log"
pythonExe = root & "\.venv\Scripts\python.exe"

If Not fso.FileExists(pythonExe) Then
    MsgBox "JARVIS is not installed yet. Run INSTALL_JARVIS.bat first.", 48, "JARVIS"
    WScript.Quit 1
End If

If Not fso.FolderExists(dataDir) Then fso.CreateFolder dataDir

' Start Ollama only when its CLI cannot reach the local service.
ollamaCheck = shell.Run("cmd /c ollama list >nul 2>&1", 0, True)
If ollamaCheck <> 0 Then
    shell.Run "cmd /c start ""Ollama"" ollama serve", 0, False
    WScript.Sleep 5000
End If

' Avoid duplicate API process.
apiReady = shell.Run("powershell -NoProfile -Command ""try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health -TimeoutSec 1 | Out-Null; exit 0 } catch { exit 1 }""", 0, True)
If apiReady <> 0 Then
    apiCmd = "cmd /c cd /d """ & agentDir & """ && """ & pythonExe & """ -m uvicorn api:app --host 127.0.0.1 --port 8765"
    shell.Run apiCmd, 0, False
    WScript.Sleep 2500
End If

' Start voice only if no existing voice.loop process is present.
Set proc = shell.Exec("powershell -NoProfile -Command ""if (Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'voice\.loop' }) { exit 0 } else { exit 1 }""")
Do While proc.Status = 0
    WScript.Sleep 50
Loop
If proc.ExitCode <> 0 Then
    ' Keep the process hidden, but persist stdout/stderr so a voice startup failure is diagnosable.
    voiceCmd = "cmd /c cd /d """ & agentDir & """ && """ & pythonExe & """ -m voice.loop >> """ & voiceLog & """ 2>&1"
    shell.Run voiceCmd, 0, False
End If

WScript.Sleep 1200
shell.Run "http://127.0.0.1:8765", 1, False

Set proc = Nothing
Set shell = Nothing
Set fso = Nothing
