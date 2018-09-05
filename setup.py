import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="functional_funds_transfer",
    version="v0.2",
    author="Monty Dimkpa",
    author_email="cmdimkpa@gmail.com",
    description="Teaching functional programming with a funds transfer example",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmdimkpa/functional-funds-transfer/archive/v0.2.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
