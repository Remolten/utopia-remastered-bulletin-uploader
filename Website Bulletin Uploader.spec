# -*- mode: python -*-

a = Analysis(['pgup.py'],
             datas=[('pgu\\data\\themes\\clean', 'pgu\\data\\themes\\clean')])

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.datas,
          onefile=True,
          console=False,
          name='Website Bulletin Uploader',
          icon='leaf.ico')
