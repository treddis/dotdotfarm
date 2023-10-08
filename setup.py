#!/usr/bin/env python3
# ! -*- coding: utf-8 -*-

import os
import shutil
from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

__version__ = '1.6.0'
install_requires = [
    "aiohttp==3.8.4",
    "colorama==0.4.6",
    "setuptools==66.1.1",
    "tqdm==4.64.1",
    "yarl==1.8.2",
    "multidict==6.0.4",
    "attrs==22.2.0",
    "yarl==1.8.2",
    "async-timeout==4.0.2",
    "aiosignal==1.3.1"
]

install_dir = os.path.abspath('.')
try:
    shutil.copy(os.path.join(install_dir, 'dotdotweb.py'), os.path.join(install_dir, 'dotdotfarm', 'dotdotweb.py'))
    setup(
        name='dotdotfarm',
        version=__version__,
        description='Path Traversal exploitation tool',
        license='GPL',
        author='treddis',
        packages=find_packages(),
        install_requires=install_requires,
        entry_points={
            'console_scripts':
                ['dotdotweb = dotdotfarm.dotdotweb:main']
        })
except FileNotFoundError:
    setup(
        name='dotdotfarm',
        version=__version__,
        description='Path Traversal exploitation tool',
        license='GPL',
        author='treddis',
        packages=find_packages(),
        install_requires=install_requires,
        entry_points={
            'console_scripts':
                ['dotdotweb = dotdotfarm.dotdotweb:main']
        })
finally:
    pass
    # os.remove(os.path.join(install_dir, 'dotdotfarm', 'dotdotweb.py'))
