from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'optimize': 1,
    'includes': ['numpy', 'pandas'],
    'packages': [],
    'plist': {'CFBundleName': 'MacApp'},
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
