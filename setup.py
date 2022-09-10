from setuptools import setup

setup(
    name="finnscraper",
    version="0.1",
    description="Package for scraping car advert data from Finn",
    url="http://github.com/richypitman/finnscraper",
    author="Richy Pitman",
    author_email="richy.pitman@googlemail.com",
    license="MIT",
    packages=["finnscraper"],
    dependencies=["bs4", "pandas"],
    zip_safe=False,
)
