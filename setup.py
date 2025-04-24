from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'numpy', 'ib_insync'],  # Add required packages
    'includes': ['numpy.core.multiarray'],  # Explicitly include numpy components
    'excludes': ['wheel', 'setuptools._vendor.wheel', 'PyQt5', 'PySide2', 'tkinter'],
    'frameworks': [],
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
