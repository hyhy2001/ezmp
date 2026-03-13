from setuptools import setup, find_packages

setup(
    name="ezmp",
    version="0.1.0",
    description="An incredibly easy to use Python multiprocessing and threading package for beginners.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "data": ["pandas>=2.0.0", "openpyxl>=3.1.2"],
        "net": ["requests>=2.31.0"],
        "all": ["pandas>=2.0.0", "openpyxl>=3.1.2", "requests>=2.31.0"],
    },
    python_requires=">=3.8",
)
