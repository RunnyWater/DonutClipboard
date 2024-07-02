from setuptools import setup, find_packages
import os

def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    requirements = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return requirements

requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')

setup(
    name="DonutClipboard",
    version="0.1.0",
    packages=find_packages(include=['src', 'src.*']),
    install_requires=parse_requirements(requirements_path),
    entry_points={
        'console_scripts': [
            'donut_clipboard=main:main',
        ],
    },
    author="RunnyWater",
    author_email="siriusbrightestone@gmail.com",
    description="Make expirience with clipboard easier",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/RunnyWater/DonutClipboard",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.2',
)
