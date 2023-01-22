#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
        name='dotdotfarm',
        version='1.0',
        description='Path Traversal exploitation tool',
        license='GPL',
        author='treddis',
        author_email='test@mail.com',
        # packages=['dotdotfarm'],
        packages=find_packages(),
        install_requires=[
                'aiohttp==3.8.3',
                'tqdm',
                'colorama',
                'multidict==6.0.4'],
        entry_points={
                'console_scripts':
                ['dotdotweb = dotdotfarm.dotdotweb:main']
        })