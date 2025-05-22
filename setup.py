from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="hockey_stats",
    version="0.1",
    packages=["hockey_stats"],
    install_requires=required,
    include_package_data=True
)
