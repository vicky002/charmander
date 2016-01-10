__author__ = 'vikesh'

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


PYTHON3 = sys.version_info[0] > 2

required = ['requests>=2.5', 'websocket-client==0.32.0',
            'beautifulsoup4==4.4.1', 'html5lib==0.9999999', 'pyfiglet==0.7.4',
            'slackrtm==0.2.1']

if not PYTHON3:
    required += ['importlib>=1.0.3']

packages = []

try:
    longdesc = open("README.rs").read()
except:
    longdesc = ''

# Thanks to Kenneth Reitz, I stole the template for this : https://github.com/kennethreitz
setup(
    name='charmander',
    version='1.0.0',
    description='An Intelligent bot for slack',
    long_description=longdesc,
    author='Vikesh Tiwari',
    author_email='vicky002@eulercoder.me',
    url='https://github.com/vicky002/Charmander',
    packages=packages,
    scripts= [''],
    package_data = {'': ['LICENCE',], '':['charmander/extensions/*.py']},
    include_package_data=True,
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ),

)