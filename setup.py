from pathlib import Path
from setuptools import setup, find_namespace_packages


REQUIREMENTS = []
VERSION = "1.0.5"


setup(
    name="bom-configuration",
    version=VERSION,
    description="Config fun.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/bomt1me/bomconfiguration",
    packages=find_namespace_packages("src"),
    namespace_packages=["bom"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    classifiers=[],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    setup_requires=[],
)
