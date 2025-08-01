from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="expenses",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for managing and visualizing financial expense data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/expenses",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "expenses": ["config/*.yaml"],
    },
    entry_points={
        "console_scripts": [
            "expenses-classify=expenses.classifier:main",
            "expenses-app=app:main",
        ],
    },
)
