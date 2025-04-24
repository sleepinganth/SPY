# setup.py
from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'includes': ['pkg_resources', 'cmath'],
    'packages': ['jaraco', 'jaraco.text', 'pandas'],
}

setup(
    name='MacApp',
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
