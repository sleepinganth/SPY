from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'optimize': 0,
    'packages': [],
    'excludes': ['pkg_resources', 'setuptools', 'jaraco.text'],
    'site_packages': True,
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
