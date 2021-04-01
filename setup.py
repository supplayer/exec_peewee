import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exec-peewee",
    version="0.0.1",
    author="Supplayer",
    author_email="x254724521@hotmail.com",
    description="Build peewee model class from Mysql.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x254724521/exec_peewee.git",
    packages=setuptools.find_packages(exclude=('tests', '.gitignore', 'requirements.txt')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['peewee', 'pymysql']
)