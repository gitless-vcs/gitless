# -*- mode: python -*-
import os

a = Analysis(['gl.py'],
             pathex=[os.getcwd()],
             hiddenimports=[
               # https://github.com/pyinstaller/pyinstaller/issues/3198
               # remove this when dropping support for Python < 3.7
               '_sysconfigdata',
               '_cffi_backend'],
             hookspath=None,
             runtime_hooks=None)


pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='gl',
          debug=False,
          strip=None,
          upx=True,
          console=True )
