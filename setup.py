import os
from os.path import join, dirname
from setuptools import setup, find_packages

import k1921vkx_flasher

setup(
    name='k1921vkx_flasher',
    version=k1921vkx_flasher.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'pyserial'
    ],
    extras_require={
        'GUI': [
            'pyqt5'
        ]
    },
    entry_points={
        'console_scripts':
            ['k1921vkx_flasher = k1921vkx_flasher.__main__:main']
    }
)
