from setuptools import setup
import os

setup(
    name="pyFRTB",
    version="0.1",
    author="Mark Teper",
    author_email="",
    description=("Python package for computing FRTB SBA Approach"),
    license="MIT",
    keywords="FRTB Finance Basel",
    install_requires=["numpy"],
    url="https://github.com/tarkmeper/pyFRTB",
    packages=['pyFRTB'],
    include_package_data=True,
    package_data={'pyFRTB': ['*.yaml']},
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4"
    ]
)