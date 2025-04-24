from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': [],
    'excludes': ['wheel', 'setuptools._vendor.wheel'],  # Exclude the problematic packages
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
