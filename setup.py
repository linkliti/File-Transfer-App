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
    include_package_data=True,
    packages=['FTA'],
    package_data={
        'FTA': ['style/*'],
    },
    entry_points={
        'console_scripts': [
            'FTA = FTA.__main__:main'
        ]
    },
    install_requires=[
        'pyqt5',
        'docopt',
        'pyftpdlib'
    ],
    extras_require={
        'dev': [
            'pytest'
        ]
    },
    python_requires='>=3.6, <4'
)
