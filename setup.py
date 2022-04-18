import setuptools
from os import path


def read(fname):
    return open(path.join(path.dirname(__file__), fname), encoding="utf-8").read()


setuptools.setup(
    name='FTA',
    version='1.0.0',
    author="Alexander Popov",
    author_email="popovalex1100@gmail.com",
    url="https://github.com/linkliti/File-Transfer-App",
    description='File Transfer App on Python',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=['FTA'],
    entry_points={
        'console_scripts': [
            'FTA = FTA.__main__:main'
        ]
    },
    install_requires=[
        'pyside6',
        'docopt'
    ],
    python_requires='>=3.6, <4'
)
