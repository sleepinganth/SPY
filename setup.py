# setup.py
from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': [],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)