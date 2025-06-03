from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': False,
    'optimize': 0,
    'packages': [],
    'includes': ['cmath'],
    'site_packages': True,
    'strip': False,  # Keep debug info for complex packages
    'semi_standalone': False,  # Include all dependencies
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        'ib_insync>=0.9.86',
        'pytz>=2022.1',
        'PyYAML>=6.0',
        'jaraco.text'
    ],
)
