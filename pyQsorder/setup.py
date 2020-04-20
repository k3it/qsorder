from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=[], excludes=[])

import sys

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('qsorder.py',
               base=base,
               targetName='pyQsorder',
               icon='qsorder.ico',
               shortcutName='Qsorder',
               shortcutDir="DesktopFolder",
               copyright='2020 K3IT',
               )
]

build_exe_options = {
    # 'packages': ['pkg_resources'],
    'includes': [
        'atexit',
        'pkg_resources',
        'pkg_resources.py2_warn',
    ],
    'include_msvcr': True,
    'optimize': 2
}

setup(name='Qsorder',
      version='3.1',
      description='Qsorder is a contest QSO recorder',
      # options = dict(build_exe = buildOptions),
      options={'build_exe': build_exe_options},
      executables=executables)
