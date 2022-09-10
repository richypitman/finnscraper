import finnscraper.finnscraper as fs
from finnscraper.postcodes import AddPostcode
import pandas as pd

# These are the models I'm interested in
models_dict = {
    "Volkswagen Transporter": "1.817.1444",
    "Toyota HiAce": "1.813.1394",
    "Ford Transit": "1.767.1063",
    "Opel Vivaro": "1.795.7623",
    "Mercedes Vito": "1.785.2897",
    "Mercedes Sprinter": "1.785.1187",
    "Renault Trafic": "1.804.1332",
}

models = models_dict.values()

" Getting the search query URL "
search_url = fs.QueryUrl(
    "https://www.finn.no/car/used/search.html?"
)  # test multiple of these
search_url.add_models(models)
search_url.add_other_query("sales_form", 1)  # used vehicles
# sort newest first - ensures newest are displayed if over 50 pages of ads
search_url.sort_newest_first()
print(f"URL with search query: {search_url.url}")

""" Get ad urls from each page of search results. Only load one page.
The ad_urls instance variable is a list which contains the URLs of all ads """

get_ad_urls = fs.GetAdUrls(search_url.url, maxdepth=1)

""" Parse each ad page and extract key information. A list for holding the
scraped data must be specified. This is a bit ugly and should be improved """
all_ads_list = []
for ad_url in get_ad_urls.ad_urls:
    print(
        f"""Parsing ad {str(get_ad_urls.ad_urls.index(ad_url) + 1)} out of {str(len(get_ad_urls.ad_urls) + 1)}"""
    )
    parse_ad_page = fs.ParseAdPage(ad_url, all_ads_list)
    parse_ad_page.update_all_ads_list(all_ads_list)

""" Create dataframe from data and save to csv. Add fylke, a type of 
geographical region, to allow for easy filtering of ads on location """
csv_outfile = "2022_scrape.csv"
df = pd.DataFrame(all_ads_list)
df.to_csv(csv_outfile, index=False, encoding="UTF-8")
# df = pd.read_csv(csv_outfile)
add_postcode = AddPostcode(csv_outfile, "postcodes.csv")
add_postcode.add_postcode_to_df()
add_postcode.save_csv()
