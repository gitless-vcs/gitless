# -*- mode: python -*-
import os

a = Analysis(['gl.py'],
             pathex=[os.getcwd()],
             hiddenimports=['pygit2_cffi_3adedda7x2a59b7ee'],
             hookspath=None,
             runtime_hooks=None)

# this is a file pygit2 requires
a.datas += [('decl.h', '../pygit2/pygit2/decl.h', 'DATA')]

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
