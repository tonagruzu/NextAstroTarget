Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the script's directory
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Set working directory
objShell.CurrentDirectory = strScriptDir

' Use system pythonw.exe (same Python that works in terminal)
strPythonw = "C:\Users\tomas\AppData\Local\Programs\Python\Python39\pythonw.exe"

' Path to the main script
strMainScript = strScriptDir & "\main_pyside6.py"

' Launch without showing console (1 = normal window, shown and activated)
objShell.Run """" & strPythonw & """ """ & strMainScript & """", 1, False
