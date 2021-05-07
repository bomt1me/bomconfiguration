"""setup.py """


from pathlib import Path
from setuptools import setup, find_namespace_packages


REQUIREMENTS = []


setup(
    name="bom-configuration",
    version="1.0.4",
    description="config",
    long_description=Path("README.md").read_text(),
    author="Calvin Spring",
    author_email="springcalvind@gmail.com",
    url="https://github.com/bomt1me/bomconfiguration",
    packages=find_namespace_packages("src"),
    namespace_packages=["bom"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    setup_requires=[],
)
