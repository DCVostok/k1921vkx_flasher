from setuptools import setup, find_packages
from os.path import join, dirname
from setuptools import Command
import os
import k1921vkx_flasher


class build_app(Command):
    description = "build executable file"
    user_options = [
        ('distpath=', None, 'path to out executable file'),
    ]

    def run(self):
        import PyInstaller.__main__
        import shutil
        if os.path.isdir('build'):
            shutil.rmtree('build')
        if os.path.isdir(self.distpath):
            shutil.rmtree(self.distpath)
            print("del "+self.distpath)

        PyInstaller.__main__.run([
            'k1921vkx_flasher\__main__.py',
            '--onefile',
            '--distpath='+self.distpath,
            '--name=k1921vkx_flasher',
            '--icon=k1921vkx_flasher/ui/flasher.ico'
        ])

    def initialize_options(self):
        self.distpath = 'dist'

    def finalize_options(self):
        pass


setup(
    name='k1921vkx_flasher',
    version=k1921vkx_flasher.__version__,
    cmdclass={
        'build_app': build_app,
    },
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'pyinstaller',
        'pyqt5',
        'pyserial'
    ],
    entry_points={
        'console_scripts':
            ['k1921vkx_flasher = k1921vkx_flasher.__main__:main']
    }
)
