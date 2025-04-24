# setup.py
from setuptools import setup

APP = ['spy_ema_chad.py']
DATA_FILES = [('', ['spy_ema_chad.py', '__boot__.py'])]  # <- rename custom_bootstrap.py to __boot__.py
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'numpy', 'ib_insync', 'eventkit', 'nest_asyncio', 'dateutil', 'pytz'],
    'includes': ['numpy.core.multiarray'],
    'excludes': ['wheel', 'setuptools._vendor.wheel'],
    'site_packages': True,
    'optimize': 0,
}

setup(
    app=APP,
    name='MacApp',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
