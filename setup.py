from codecs import open
import glob
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="spire",
    version="0.2",
    
    description="Run software pipelines using YAML files",
    long_description=long_description,
    
    url="https://ipb-dev.u-strasbg.fr/gitlab/lamy/spire",
    
    author="Julien Lamy",
    author_email="lamy@unistra.fr",
    
    license="MIT", # TODO
    
    classifiers=[
        "Development Status :: 4 - Beta",
        
        "Environment :: Console",
        
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        
        "License :: OSI Approved :: MIT License", # TODO
        
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    
    keywords="pipeline workflow", # TODO

    packages=find_packages(exclude=["doc", "modules", "tests"]),
    install_requires=["jinja2", "pyyaml"],
    
    # package_data={ "spire": ["modules/*"] },
    data_files=[("modules", glob.glob("modules/*yml.j2"))],
    
    entry_points={ "console_scripts": [ "spire=spire:main"] },
)
