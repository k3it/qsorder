from cx_Freeze import setup, Executable

#must copy the VC runtime DLL by hand
#cp c:\Windows\System32\vcruntime140.dll build\exe.win32-3.6\lib\
#
# see https://github.com/anthony-tuininga/cx_Freeze/issues/278

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [], include_msvcr = True, include_files = ['BUGS.txt', 'CHANGES.txt', 'lame.exe'])

base = 'Console'

executables = [
    Executable('Qsorder\\qsorder.py', base=base, targetName = 'qsorder.exe', icon='qsorder.ico', copyright = "Vasiliy Gokoyev K3IT/GPL 3.0")
]

setup(name='Qsorder',
      version = '2.13',
      description = 'console app for contest audio recording',
      options = dict(build_exe = buildOptions),
      executables = executables)

