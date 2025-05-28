from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': False,
    'optimize': 0,
    'packages': [],
    'includes': ['cmath'],
    'site_packages': True,
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
