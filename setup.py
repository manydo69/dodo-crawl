from setuptools import setup, find_packages

setup(
    name="dodo-crawl",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "selenium",
        "webdriver-manager",
        "tqdm",
        "boto3",
        "python-dotenv",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "dodo-crawl=dodo_crawl.main:main",
        ],
    },
    scripts=["scripts/dodo-crawl"],
    author="Your Name",
    author_email="your.email@example.com",
    description="A comic crawler application",
    keywords="comic, crawler, selenium",
    python_requires=">=3.6",
)
