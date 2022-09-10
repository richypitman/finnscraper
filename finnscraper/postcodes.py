import re
import pandas as pd


class AddPostcode:
    def __init__(self, finn_csv_file: str, postcode_file: str) -> None:
        self.finn_csv_file = finn_csv_file
        self.postcode_file = postcode_file

    def add_postcode_to_df(self) -> None:
        self.postcode_lines = self._csv_reader(self.postcode_file)
        self.postcode_fylke_dict = self._get_postcode_fylke_dict(self.postcode_lines)
        self.df = self._add_postcode_to_df(self.finn_csv_file, self.postcode_fylke_dict)

    def _csv_reader(self, file):
        f = open(file)
        lines = f.read().split("\n")
        return lines

    def _get_postcode_fylke_dict(self, lines: list) -> dict:
        # First entry is postcode region, second is fylke
        rows = lines[1:]
        postcode_regions = [row.split(",")[0] for row in rows]
        fylker = [row.split(",")[1] for row in rows]
        d = dict(zip(postcode_regions, fylker))

        return d

    def _add_postcode_to_df(self, finn_csv: str, postcode_fylke: dict) -> pd.DataFrame:
        """
        Get postcode from address and use dictionary of postcode regions:fylker
        to assign a fylke to each ad.

        Args:
            finn_csv (str): filepath to csv of ads scraped from Finn
            postcodes_fylker (dict): dictionary of postcode regions:fylker to
            assign a fylke to each ad.

        Returns:
            pd.DataFrame: ad data with postcodes & fylker added
        """

        df = pd.read_csv(finn_csv)

        pattern_postcode = r"[0-9]{4}"  # match four digits
        df["Postcode"] = df["Address"].apply(
            lambda x: re.search(pattern_postcode, x).group(0)
        )
        df["Fylke"] = df["Postcode"].apply(lambda x: postcode_fylke.get(x[:2]))

        return df

    def save_csv(self, outfile: str = None) -> None:
        """
        Save dataframe to csv file. If no outfile name is provided, the
        dataframe will overwrite the input csv file.

        Args:
            df (pd.DataFrame): dataframe of scraped data
            outfile (str, optional): name of saved csv file. Defaults to None,
            overwriting the input csv file.
        """
        if not outfile:
            outfile = self.finn_csv_file
        if not outfile.endswith(".csv"):
            outfile += ".csv"

        print(f"Saving dataframe to {outfile}")
        self.df.to_csv(outfile, index=False, encoding="UTF-8")
