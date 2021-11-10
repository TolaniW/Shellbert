# -*- mode: python ; coding: utf-8 -*-
import os
path = os.path.abspath(".")
block_cipher = None
datas = []
try:
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			datas.append((f'cogs\\{filename}', 'cogs'))
except:
	datas = []


a = Analysis(
        ['main.py'],
        pathex=[path],
        binaries=[],
        datas=datas,
        hiddenimports=['apscheduler'],
        hookspath=[],
        runtime_hooks=[],
        excludes=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False
    )

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='main',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=['vcruntime140.dll', 'ucrtbase.dll'],
        runtime_tmpdir=None,
        # icon='icon.ico',
        console=True
    )
