# -*- conding:utf-8 -*-
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

config = {
    'description': 'User management',
    'author': 'Rodrigue ADOUHOUEKONOU',
    'url': 'URL to get it at.',
    'download_url': 'https://github.com/tarlm/usermgmt',
    'author_email': 'radouhou@free.fr',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['usermgmt'],
    'scripts': [],
    'name': 'usermgmt'
}

setup(**config)
