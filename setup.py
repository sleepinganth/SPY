from setuptools import setup

APP = ['spy_ema_chad.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'numpy', 'cmath'],
    'includes': ['cmath','pandas._libs.tslibs', 'pandas._libs.tslibs.timestamps', 'pandas._libs.testing'],
    'excludes': ['numpy.__config__', 'numpy.distutils', 'numpy.f2py', 'numpy.testing'],
    'plist': {
        'CFBundleName': 'MacApp',
    },
    'optimize': 1,
    'resources': [],  # Add any files needed
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
