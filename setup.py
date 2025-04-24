from setuptools import setup

APP = ['spy_ema_chad.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'numpy', 'ib_insync'],
    'excludes': ['wheel', 'setuptools._vendor.wheel'],
    'site_packages': True,  # Use system site-packages rather than bundling
}

setup(
    app=APP,
    name='MacApp',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)