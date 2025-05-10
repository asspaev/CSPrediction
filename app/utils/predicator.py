from sklearn.pipeline import Pipeline

from pathlib import Path
from tqdm import tqdm

from curl_cffi import requests as curl_requests
import pandas as pd

from pathlib import Path
from lxml import html

import warnings
from curl_cffi.requests.exceptions import RequestException
warnings.simplefilter(action='ignore', category=FutureWarning)

import utils.preprocess_scrapped_data as utils


class Predicator:
    def __init__(
        self,
        model: Pipeline,
        mean_player: pd.DataFrame,
    ):
        """
        Initialize Predicator.

        Parameters
        ----------
        model : Pipeline
            Model object to be used for prediction.
        """

        # Set model
        self.model = model
        self.mean_player = mean_player

        # Set scrapping settings
        self.response_settings = {
            "headers": None,
            "cookies": None,
            "impersonate": "chrome",
        }

    def set_scrapp_settings(
        self,
        headers: dict = None,
        cookies: Path = None,
    ):
        """
        Set scrapping settings.

        Parameters
        ----------
        headers : dict, optional
            Headers to be used for requests. Defaults to None.
        cookies : Path, optional
            Path to cookies file to be used for requests. Defaults to None.
        """
        
        # Set scrapping settings
        self.response_settings['headers'] = headers
        self.response_settings['cookies'] = cookies

    def _scrapp_full_match(
        self,
        match_link: str,
    ):
        """
        Scrapp full match info.

        Parameters
        ----------
        match_link : str
            Link to the match page.

        Returns
        -------
        df_players : pd.DataFrame
            DataFrame with all players info.
        df_match : pd.DataFrame
            DataFrame with match info.
        """

        # Request page
        response = curl_requests.get(url=match_link, **self.response_settings)

        # Build html tree
        tree = html.fromstring(response.content)  # build html tree

        # Parse players
        players_id, players_name, df_match = utils.parse_players(tree)

        # Get players info
        df_players = utils.create_df_players()
        pbar = tqdm(total=len(players_id), desc="Scrapping players info", unit="player")
        for i in range(1, 11):
            
            # Request page
            player_link = f"https://www.hltv.org/stats/players/{players_id[i-1]}/{players_name[i-1].lower()}"
            response = curl_requests.get(url=player_link, **self.response_settings)
            
            # Build html tree
            tree = html.fromstring(response.content)  # build html tree

            # Parse player info
            player_stats = utils.parse_player_stats(tree)

            # Build DataFrame player
            df_player = pd.DataFrame([{"player_link": players_name[i-1].lower(), **player_stats}])

            # Concat DataFrames
            df_players = pd.concat([df_players, df_player], ignore_index=True)

            # Refresh pbar
            pbar.n += 1
            pbar.refresh()

        return df_players, df_match

    def predict(
        self,
        match_link: str,
        df_match: pd.DataFrame = None,
        df_players: pd.DataFrame = None,
    ):
        """
        Predict the winner of a match based on the match link.

        Parameters
        ----------
        match_link : str
            The link to the match page on hltv.org
        df_match : pd.DataFrame, optional
            The DataFrame containing the match info. If None, the method will
            scrapp the match info from the match link. Defaults to None.
        df_players : pd.DataFrame, optional
            The DataFrame containing the players info. If None, the method will
            scrapp the players info from the match link. Defaults to None.

        Returns
        -------
        y_pred : np.ndarray
            The predicted winner of the match. 0 if team 1 wins, 1 if team 2 wins.
        """

        # Scrapp match info
        if not df_match and not df_players:
            df_players, df_match = self._scrapp_full_match(match_link)

        # Preprocess players
        df_players_preprocessed = utils.preprocess_players(df_players, self.mean_player)

        # Merge data
        df_merged = utils.merge_data(df_match, df_players_preprocessed)

        # Drop string columns
        df_merged = df_merged.drop(columns=df_merged.select_dtypes(include='object').columns)

        # Predict
        y_pred = self.model.predict(df_merged)

        # TODO: Добавить принты и вывод в виде label, а также вывод доп. информации о матче

        return y_pred

