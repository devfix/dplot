from setuptools import find_packages, setup

setup(
    name='dplot',
    packages=find_packages(),
    version='0.0.1',
    description='devfix plot',
    author='devfix',
    install_requires=['numpy', 'matplotlib'],
    test_suite='tests',
)
