from setuptools import setup

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

APP = ['main.py']
OPTIONS = {
    'argv_emulation': False,
    'optimize': 0,
    'packages': [],
    'includes': ['cmath'],
    'site_packages': True,
}

setup(
    app=APP,
    name='MacApp',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=read_requirements(),
)
