from setuptools import setup

# Read requirements from requirements.txt
def read_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-16') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except UnicodeDecodeError:
        # Fallback to latin-1 encoding if utf-8 fails
        with open('requirements.txt', 'r', encoding='latin-1') as f:
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
