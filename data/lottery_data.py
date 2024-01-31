"""lottery_data.py"""
import os
import argparse
from datetime import datetime
import logging
import json
import requests

from data.data_frame_operations import DataFrameManager
from data.data_frame_operations_mongodb import DataFrameManagerMongoDB
from configuration.config import VARIABLES


class LotteryDataManager:
    """
    Handles the management of lottery data, including downloading files from an API,
    updating Excel files with lottery results, and handling API requests.

    Attributes:
        None

    Methods:
        is_sunday():
            Checks if the current day is Sunday.
        file_downloaded_today(path, filename):
            Checks if the file has been downloaded today.
        download_lottery_file(api, timeout_seconds):
            Downloads the lottery file from the API.
        update_lottery_data(response, path, filename, args):
            Updates the Excel file with lottery results from the API.
        should_download_file(path, filename):
            Checks if it's appropriate to download the lottery file.
        handle_api_request(path, filename, args):
            Handles the API request and updates the Excel file with the results.
        handle_successful_request(response, path, filename, args):
            Handles a successful API request.
    """

    @staticmethod
    def is_sunday() -> bool:
        """
        Check if the current day is Sunday.

        Returns:
            bool: True if today is Sunday, False otherwise.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return datetime.strptime(today, "%Y-%m-%d").weekday() == 6

    @staticmethod
    def file_downloaded_today(path: str, filename: str) -> bool:
        """
        Check if the file has been downloaded today.

        Args:
            path (str): Path to the file.
            filename (str): Name of the file.

        Returns:
            bool: True if the file has been downloaded today, False otherwise.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(path + filename):
            file_date = datetime.fromtimestamp(
                os.path.getmtime(path + filename)
            ).strftime("%Y-%m-%d")
            return file_date == today
        return False

    @staticmethod
    def download_lottery_file(api: str, timeout_seconds: int = 10) -> requests.Response:
        """
        Downloads the lottery file from the API.

        Args:
            api (str): URL of the API.
            timeout_seconds (int): Timeout for the HTTP request.

        Returns:
            requests.Response: Response object containing the API response.
        """
        try:
            response = requests.get(api, timeout=timeout_seconds)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error("Request failed. Status code: %s", e)
        return response

    @staticmethod
    def update_lottery_data(
        response: requests.Response, path: str, filename: str, args: argparse.Namespace
    ) -> None:
        """
        Updates the Excel file with the lottery results from the API.

        Args:
            response (requests.Response): API response object.
            path (str): Path to the Excel file.
            filename (str): Name of the Excel file.
            args (argparse.Namespace): Parsed command-line arguments.

        Returns:
            None
        """
        if response.status_code == 200:
            LotteryDataManager.handle_successful_request(response, path, filename, args)
        else:
            print(f"Request failed. Status code: {response.status_code}")

    @staticmethod
    def should_download_file(path: str, filename: str) -> bool:
        """
        Checks if it's appropriate to download the lottery file.

        Args:
            path (str): Path to the file.
            filename (str): Name of the file.

        Returns:
            bool: True if the file should be downloaded, False otherwise.
        """
        return (
            not LotteryDataManager.is_sunday()
            and not LotteryDataManager.file_downloaded_today(path, filename)
        )

    @staticmethod
    def handle_api_request(path: str, filename: str, args: argparse.Namespace) -> None:
        """
        Handles the API request and updates the Excel file with the results.

        Args:
            path (str): Path to the Excel file.
            filename (str): Name of the Excel file.
            args (argparse.Namespace): Parsed command-line arguments.

        Returns:
            None
        """
        try:
            if LotteryDataManager.should_download_file(path, filename):
                response = LotteryDataManager.download_lottery_file(VARIABLES["api"])
                LotteryDataManager.update_lottery_data(response, path, filename, args)
            else:
                logging.info(
                    "It's Sunday or file already downloaded today. No need to download the file."
                )
        except requests.exceptions.RequestException as e:
            logging.error("Request failed: %s", e)

    @staticmethod
    def handle_successful_request(
        response: requests.Response, path: str, filename: str, args: argparse.Namespace
    ) -> None:
        """
        Handles a successful API request.

        Args:
            response (requests.Response): API response object.
            path (str): Path to the Excel file.
            filename (str): Name of the Excel file.
            args (argparse.Namespace): Parsed command-line arguments.

        Returns:
            None
        """
        try:
            lottery_data = response.json()
        except json.JSONDecodeError as e:
            logging.error("Error decoding JSON: %s", e)
            return

        if args.storage.lower() == "excel":
            excel = DataFrameManager()
            df_create = excel.read_or_create_dataframe(path, filename)
            df_update = excel.update_dataframe(df_create, lottery_data)
            excel.save_dataframe(df_update, path, filename)
        elif args.storage.lower() == "database":
            mongodb = DataFrameManagerMongoDB()
            df_update = mongodb.update_dataframe_mongodb(lottery_data)
