; 定义安装程序的基本信息
[Setup]
AppName=SVINA
AppVersion=0.0.1
; 安装在用户目录
DefaultDirName={userappdata}\SVINA  


DefaultGroupName=SVINA
OutputBaseFilename=SVINA_0.0.1_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=none
SetupIconFile={app}\svina.ico 
;PrivilegesRequired=admin
[Files]
; 项目文件
; 项目文件，递归复制整个文件夹内容到目标目录
Source: "D:\notebookWD\SVINA\bin\*"; DestDir: "{app}\bin"; Flags: recursesubdirs createallsubdirs
Source: "D:\notebookWD\SVINA\env.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\notebookWD\SVINA\README.txt"; DestDir: "{app}"; Flags: isreadme
Source: "D:\notebookWD\SVINA\Miniconda3-latest-Windows-x86_64.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\notebookWD\SVINA\svina.ico"; DestDir: "{app}"; Flags: ignoreversion  
[Icons]
; 创建快捷方式
Name: "{group}\SVINA"; Filename: "{app}\bin\run_script.bat"; IconFilename: "{app}\svina.ico"
Name: "{commondesktop}\SVINA"; Filename: "{app}\bin\run_script.bat"; IconFilename: "{app}\svina.ico"




[Run]
; 安装 Miniconda（无界面模式）
Filename: "{app}\Miniconda3-latest-Windows-x86_64.exe"; Parameters: "/InstallationType=JustMe /AddToPath=1 /S /D={app}\miniconda"; Flags: shellexec waituntilterminated

; 激活 Miniconda 并创建 Conda 环境
Filename: "{cmd}"; Parameters: "/K {app}\miniconda\Scripts\activate.bat {app}\miniconda && {app}\miniconda\Scripts\conda.exe env create -f {app}\env.yml -p {app}\env"; Flags: waituntilterminated


; 创建运行脚本的批处理文件
Filename: "{cmd}"; Parameters: "/C echo @echo off > {app}\bin\run_script.bat && echo call {app}\miniconda\Scripts\activate.bat {app}\env >> {app}\bin\run_script.bat && echo ""{app}\\env\\python.exe"" ""{app}\\bin\\SVINA_GUI.py"" >> {app}\bin\run_script.bat && echo pause >> {app}\bin\run_script.bat"; Flags: runhidden waituntilterminated

;%WINDIR%\System32\cmd.exe "/K" C:\Users\74489\AppData\Roaming\SVINA\miniconda\Scripts\activate.bat C:\Users\74489\AppData\Roaming\SVINA\miniconda
;%WINDIR%\System32\cmd.exe "/K" C:\Users\Lenovo\AppData\Roaming\SVINA\miniconda\Scripts\activate.bat C:\Users\Lenovo\AppData\Roaming\SVINA\miniconda