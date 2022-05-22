import re
from os import path

import setuptools


def read(fname):
    return open(path.join(path.dirname(__file__), fname),
                encoding="utf-8").read()


metadata = dict(
    re.findall(
        r"""__([a-z]+)__ = '([^']+)""", read("FTA/__init__.py")
    )
)


setuptools.setup(
    name='FTA',
    version=metadata["version"],
    author="Alexander Popov",
    author_email="popovalex1100@gmail.com",
    url="https://github.com/linkliti/File-Transfer-App",
    description='File Transfer App on Python',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=['FTA'],
    package_data={
        'FTA': ['cert/*', 'style/*']
    },
    entry_points={
        'console_scripts': [
            'FTA = FTA.__main__:main'
        ]
    },
    install_requires=[
        'pyqt5',
        'docopt',
        'pyftpdlib',
        'tabulate',
        'psutil',
        'pyOpenSSL',
        'netifaces',
    ],
    extras_require={
        'dev': [
            'setuptools',
            'pytest',
            'autopep8',
            'sphinx',
            'sphinx_rtd_theme'
        ]
    },
    python_requires='>=3.7, <4'
)
