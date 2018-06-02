; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Qsorder"
#define MyAppVersion "2.13"
#define MyAppPublisher "K3IT"
#define MyAppURL "https://github.com/k3it/qsorder"
#define MyAppExeName "qsorder.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{24C5C544-3D6D-41B5-B7DD-6C74EFBCC5AF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={sd}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=C:\Users\uncle_ziba\qsorder\dist
OutputBaseFilename={#MyAppName}-{#MyAppVersion}-win32
SetupIconFile=C:\Users\uncle_ziba\qsorder\qsorder.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\uncle_ziba\qsorder\build\exe.win32-3.6\qsorder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\uncle_ziba\qsorder\build\exe.win32-3.6\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\uncle_ziba\qsorder\build\exe.win32-3.6\BUGS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\uncle_ziba\qsorder\build\exe.win32-3.6\CHANGES.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\uncle_ziba\qsorder\build\exe.win32-3.6\python36.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\uncle_ziba\qsorder\build\exe.win32-3.6\lame.exe"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

