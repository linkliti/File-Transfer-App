import setuptools
from os import path

def read(fname):
    return open(path.join(path.dirname(__file__), fname), encoding="utf-8").read()

setuptools.setup(
    name='FTA',
    version='1.0.0',
    author="Alexander Popov",
    packages=setuptools.find_packages(),
    description='File Transfer App on Python',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    entry_points={
            'console_scripts': [
                'FTA=FTA.main:main'
            ]
    }
    # install_requires=[],
)
