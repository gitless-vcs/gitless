# -*- mode: python -*-
a = Analysis(['gl.py'],
             pathex=['/Users/santiago/Documents/MIT/cmodeling/code/gitless'],
             hiddenimports=['pygit2_cffi_4091df83x5470904'],
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
