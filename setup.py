from setuptools import setup, find_packages
from pathlib import Path

def parse_requirements(filename):
    with open(filename, encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and not line.endswith("-e")
        ]

setup(
    name="hw_document_portal",
    author="neela natarajan",
    version="0.1",
    description="LLM powered intelligent document analysis and comparison system",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test*", "examples*"]),
    include_package_data=True,
    install_requires=parse_requirements("requirement.txt"),
    extras_require = {
        "dev": ["pytest", "pylint", "ipykernel"]
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "license :: OSI Approved :: MIT License",
    ]
    python_requires=">=3.10",
    
)
