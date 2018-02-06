# -*- mode: python -*-
import os

a = Analysis(['gl.py'],
             pathex=[os.getcwd()],
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
