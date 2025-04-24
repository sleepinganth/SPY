from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'numpy', 'cmath'],
    'includes': ['cmath'],
    'excludes': [],
    'plist': {
        'CFBundleName': 'MacApp',
    },
    'optimize': 1,
    'resources': [],  # Add any files needed
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
