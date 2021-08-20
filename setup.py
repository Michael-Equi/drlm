import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="drlm",
    version="0.0.1",
    author="Michael Equi",
    author_email="michaelequi@berkeley.edu",
    description="Dorm room lights and magic high level code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    packages=setuptools.find_packages(),
    package_data={'': ['adata.json', 'adata_input.json']},
    python_requires=">=3.9",
)
