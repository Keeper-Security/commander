from setuptools import setup, find_packages
from os import path

import keepercommander

here = path.abspath(path.dirname(__file__))

# Get the long description from the README.md file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'colorama',
    'cryptography',
    'pycryptodomex>=3.7.2',
    'libkeepass',
    'requests',
    'tabulate',
    'prompt_toolkit>=2.0.4,<=2.0.10',
    'asciitree',
    'protobuf>=3.13.0',
    'pyperclip'
]
adpasswd_requires = ['ldap3']
test_requires = ['pytest', 'testfixtures']
pylint_requires = ['pylint', 'pylint-protobuf']

setup(
    name='keepercommander',
    version=keepercommander.__version__,
    description='Keeper Commander for Python 3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Craig Lurey',
    author_email='craig@keepersecurity.com',
    url='https://github.com/Keeper-Security/Commander',
    license='MIT',
    classifiers=["Development Status :: 4 - Beta",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3.5",
                 "Topic :: Security"],
    keywords='security password',

    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "keeper=keepercommander.__main__:main",
        ],
    },
    install_requires=install_requires,
    extras_require={
        'adpasswd': adpasswd_requires,
        'test': test_requires,
        'pylint': pylint_requires,
        'all': adpasswd_requires + test_requires + pylint_requires,
    }
)
