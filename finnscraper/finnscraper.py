from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from typing import Union


def soupify_page(url: str) -> BeautifulSoup:
    """
    Take a URL and return a Beautiful Soup object (parsed HTML document)

    Args:
        url (str): URL of document to parse

    Returns:
        BeautifulSoup: parsed HTML document
    """

    req = urlopen(url)
    soup = BeautifulSoup(req.read(), "html.parser")

    return soup


class QueryUrl:
    """
    URL string with query string sent in the search GET request. Composed of the
    URL, defining the Finn ads to be searched, e.g.
    https://www.finn.no/car/used/search.html?, and the query string, which
    filters to search results. Query names and values can be found by filtering
    on Finn.no and examining the GET query string generated in the URL.

    This class is instantiated with a URL which may or may not initially contain
    a GET query string.
    """

    def __init__(self, url: str) -> None:
        """
        Instantiate the class with a URL with or wihout a GET query string

        Args:
            url (str): Finn URL search page, e.g. https://www.finn.no/car/used/search.html?

        """

        self.url = url
        self._check_clean_input_url()

    def _check_clean_input_url(self) -> None:
        """
        Check that the format of the URL string is suitable.

        Must contain:
            1. "finn.no"
            2. "search.html?"

        Must not contain:
            1. A page query
        """

        if "finn.no" not in self.url:
            raise ValueError(f"You have not entered a Finn.no addresss")

        if "search.html?" not in self.url:
            raise ValueError(
                f"URL query string should contain 'search.html?'. URL input: {self.url}"
            )

        # Don't want a page query in the query string as this is added when searching for ads
        query_remove_list = [r"&page=\{\d{1,2}\}"]
        for pattern in query_remove_list:
            match = re.search(pattern, self.url)
            if match:
                print(f"Removing {match[0]} from input URL")
                self.url = re.sub(pattern, "", self.url)

    def sort_newest_first(self) -> None:
        """
        Sort by newest first to guarantee most recent results are loaded. Finn
        loads a maximum of 50 pages of ad results for a given search query.
        """
        self.url += "&sort=PUBLISHED_DESC"

    def add_other_query(self, query_name: str, query_value: Union[int, str]) -> None:
        """
        Add custom search query & value.
        Some examples:
        add_other_query("registration_class", 2) - vehicle type van
        add_other_query("sales_form", 1) - used vehicle for sale

        Args:
            query_name (str): query name
            query_value (Union[int, str]): query value
        """

        if type(query_value) != str:
            query_value = str(query_value)

        self.url += f"&{query_name}={query_value}"

    def add_models(self, models: list) -> None:
        """
        Add a list of vehicle models to the query string

        Args:
            models (list): list of vehicle model values
        """
        for model in models:
            self.url += f"&model={model}"


class GetAdUrls:
    """
    Get each ad for a given search defined by a search query.
    """

    def __init__(self, search_url: str, maxdepth: int = 50) -> None:
        """
        On instantiating, ad URLs wills be searched for and collected starting
        on page 1 of the search query given in the search_url. Up to 50 pages
        are searched as Finn loads a maximum of 50 pages of ad results for a
        given search query. Fewer pages will be searched if no more ads are
        found. The maxdepth argument can be used to limit number of search pages
        to be scraped.

        Args:
            search_url (str): URL containing search query maxdepth (int,
            optional): Maximum number of search pages to scrape ads from.
            Defaults to 50.
        """
        self.search_url = search_url
        self.maxdepth = maxdepth
        self.ad_urls = []

        assert self.maxdepth >= 1, "maxdepth must be greater than 1"

        if self.maxdepth > 50:
            self.maxdepth = 50
            print("Setting maxdepth to 50")

        self._get_ad_page_urls()

    def _get_ad_page_urls(self):
        """
        Loop through search pages and add ad page URLs to ad_urls list
        """
        self.endloop = False  # end loop flag
        self.page = 1  # page number

        # Loop through adds in search pages until no more ads are found
        while self.endloop == False:
            if self.page == self.maxdepth + 1:
                self.endloop = True
                self._print_ads_found()
                print("Reached end of search pages.")
            else:
                print(f"Searching for ads on page {self.page}")

                url_page_num = self.search_url + f"&page={self.page}"
                soup = soupify_page(url_page_num)
                self._get_ad_urls(soup)

                self.page += 1

        # If finn.no not in string, remove from list
        self.ad_urls = [url for url in self.ad_urls if "finn.no" in url]

    def _get_ad_urls(self, soup: BeautifulSoup) -> None:

        ad_urls = [a["href"] for a in soup.find_all("a", {"class": "ads__unit__link"})]

        # If only one ad is returned, the page is empty except for a random paid advert
        # stop the loop
        if len(ad_urls) <= 1:
            self.endloop = True
            self._print_ads_found()
            print("Reached end of ads for current search query. Stopping search.")
        else:
            self.ad_urls.extend(ad_urls)

    def _print_ads_found(self):
        print(f"{len(self.ad_urls)} ads found.")


class ParseAdPage:
    """For each ad, instantiate this class"""

    def __init__(self, ad_url: str, all_ads_list: list = None) -> None:
        self.ad_url = ad_url
        self.value_pattern = "^.*\>(.*)\<.*$"  # captures between > <
        self.soup = soupify_page(self.ad_url)

        self.price = self.get_price(self.soup)
        self.address = self.get_address(self.soup)
        self.brand, self.model = self.get_brand_model(self.soup)
        self.key_info = self.get_key_info(self.soup)

        self.d = self._create_dictionary()

    def get_price(self, ad_soup: BeautifulSoup) -> int:
        price = ad_soup.find("span", {"class": "u-t3"}).text

        # Clean up price data
        price = price.replace("\xa0", "")  # replace non-breaking space
        price = price.replace(" kr", "")  # remove kr from price
        price = int(price)

        return price

    def get_address(self, ad_soup: BeautifulSoup) -> str:
        # Address found in both "p" and "span" tags
        if ad_soup.find("span", {"class": "u-mh16"}) is not None:
            address = ad_soup.find("span", {"class": "u-mh16"}).text
        elif ad_soup.find("p", {"class": "u-mh16"}) is not None:
            address = ad_soup.find("p", {"class": "u-mh16"}).text
        else:
            address = "Not found"

        return address

    def get_brand_model(self, ad_soup: BeautifulSoup) -> tuple:
        try:
            brand = ad_soup.find(
                "a", attrs={"data-controller": "trackCrumbTrailAttribute1"}
            ).text
        except:
            brand = "Not found"
        try:
            model = ad_soup.find(
                "a", attrs={"data-controller": "trackCrumbTrailAttribute2"}
            ).text
        except:
            model = "Not found"

        return brand, model

    def get_key_info(self, ad_soup: BeautifulSoup) -> dict:
        key_info_keys = ["Year", "Mileage", "Gearbox", "Fuel"]

        key_info_div_tags = ad_soup.select(".media__body .u-strong")
        # str(x) to convert from bs4 ResultSet to list of strings
        key_info_values = [
            re.search(self.value_pattern, str(x)).groups()[0] for x in key_info_div_tags
        ]

        # Tidy up values - aimed at the mileage entry
        key_info_values = [x.replace("\xa0", "") for x in key_info_values]
        key_info_values = [x.replace(" km", "") for x in key_info_values]

        return dict(zip(key_info_keys, key_info_values))

    def _create_dictionary(self):
        d = {
            "URL": self.ad_url,
            "Price": self.price,
            "Address": self.address,
            "Brand": self.brand,
            "Model": self.model,
        }

        d.update(self.key_info)

        return d

    def update_all_ads_list(self, all_ads_list: list) -> None:
        all_ads_list.append(self.d)
