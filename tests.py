import unittest


"""

1. QueryUrl
    1. Check that a Finn.no address has been entered
    2. Check that ValueError is raised if "search.html?" not in URL
    3. Check that "&page={p}" and "page={p}" are removed if in URL

2. GetAdUrls
    1. Check that maxdepth keywords limit search pages

"""

from finnscraper.finnscraper import QueryUrl, GetAdUrls


class TestQueryUrl(unittest.TestCase):
    def test_finn_url(self):
        """Check that a Finn.no address has been entered"""
        url = "https://www.otherurl.no/car/used/"
        with self.assertRaises(ValueError):
            result = QueryUrl(url)._check_clean_input_url()

    def test_search_query_present(self):
        """Check that ValueError is raised if "search.html?" not in URL"""
        url = "https://www.finn.no/car/used/"
        with self.assertRaises(ValueError):
            result = QueryUrl(url)._check_clean_input_url()

    def test_page_not_in_search_query(self):
        """Check that "&page={p}" is removed if in URL"""
        url = "https://www.finn.no/car/used/search.html?page={p}"
        query = QueryUrl(url)
        result = query._check_clean_input_url()
        self.assertFalse(r"&page=\{\d{1,2}\}" in query.url)


class TestGetAdUrl(unittest.TestCase):
    """Check that the maxdepth keyword works in GetAdUrls"""

    def test_maxdepth(self):
        url = "https://www.finn.no/car/used/search.html?"
        query = QueryUrl(url)
        adsUrl = GetAdUrls(query.url, maxdepth=3)
        # maxdepth = 3 returns page = 4 and stops loading, hence assertEqual to 4
        self.assertEqual(adsUrl.page, 4)


if __name__ == "__main__":
    unittest.main()
