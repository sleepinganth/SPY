from setuptools import setup

APP = ['spy_ema_chad.py']
DATA_FILES = [('', ['custom_bootstrap.py'])]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'numpy', 'ib_insync', 'eventkit', 'nest_asyncio', 'dateutil', 'pytz'],
    'includes': ['numpy.core.multiarray'],
    'excludes': ['wheel', 'setuptools._vendor.wheel'],
    'site_packages': True,  # Include site-packages
    'bootstrap': 'custom_bootstrap',  # Use custom bootstrap
    'optimize': 0,  # Don't optimize - helps with debugging
}

setup(
    app=APP,
    name='MacApp',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)