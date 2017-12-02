import os
import sys
from setuptools import setup, find_packages
from setuptools.extension import Library

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
except ImportError:
    bdist_wheel = None


setup(
    name = "lxman",
    version = "0.1.0",
    author = "stuxcrystal",
    author_email = "stuxcrystal@encode.moe",
    description = ("Making WSL a better system"),
    license = "MIT",
    keywords = "windows wsl linux docker",
    url = "http://lxman.encode.moe/",
    packages=find_packages(),
    long_description=read('README.rst'),

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "Topic :: System :: Operating System",
        "Topic :: System :: Operating System Kernels",

        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",

        "Intended Audience :: Developers",

        "Environment :: Win32 (MS Windows)",
        "Environment :: Console",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],

    ext_modules = [Library(
        'lxman.vendor.ntfsea',
        sources=['lxman/vendor/ntfsea.c'],
        libraries=["NtDll"],
        extra_link_args=["/DLL"]
    )],
    cmdclass={'bdist_wheel': bdist_wheel},

    entry_points = {
        'console_scripts': ['lxman=lxman.cli:main']
    },
    install_requires = [
        'colorama',
        'click',
        'requests'
    ],
)
