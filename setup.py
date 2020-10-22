import sys
import os
from setuptools import setup
from torrentool import VERSION


PATH_BASE = os.path.dirname(__file__)
PYTEST_RUNNER = ['pytest-runner'] if 'test' in sys.argv else []

f = open(os.path.join(PATH_BASE, 'README.rst'))
README = f.read()
f.close()

setup(
    name='torrentool',
    version='.'.join(map(str, VERSION)),
    url='https://github.com/idlesign/torrentool',

    description='The tool to work with torrent files.',
    long_description=README,
    license='BSD 3-Clause License',

    author='Igor `idle sign` Starikov',
    author_email='idlesign@yandex.ru',

    packages=['torrentool'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[],
    setup_requires=[] + PYTEST_RUNNER,
    tests_require=[
        'pytest',
        'pytest-datafixtures',
        'pytest-responsemock',
    ],

    entry_points={
        'console_scripts': ['torrentool = torrentool.cli:main'],
    },

    test_suite='tests',

    classifiers=[
        # As in https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License'
    ],
)
