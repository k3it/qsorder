from cx_Freeze import setup, Executable

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
