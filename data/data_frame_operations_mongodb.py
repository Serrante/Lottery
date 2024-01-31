"""data_frame_operations_mongodb.py"""
import logging
from datetime import datetime
from typing import List
import pymongo
import pandas as pd

from configuration.config import VARIABLES


class DataFrameManagerMongoDB:
    """
    A class for managing operations on MongoDB collections containing lottery data.

    This class provides methods to read existing data from MongoDB, update the database
    with new lottery results, convert string representations to lists, and save data to MongoDB.

    Attributes:
        None

    Methods:
        read_or_create_data_from_mongodb(dataframe: bool = False) -> list:
            Reads existing data from MongoDB and returns it as a list.

        update_data_to_mongodb(lottery_data: list) -> None:
            Updates the MongoDB collection with new lottery results.

        convert_string_to_list(dezenas_str: str) -> list:
            Converts a string representation to a list.

        update_dataframe_mongodb(lottery_data: list) -> list:
            Updates the existing MongoDB data with new lottery results and returns it.

        save_dataframe_mongodb(lottery_data: list) -> None:
            Saves the provided lottery data to MongoDB.
    """

    def __init__(self):
        # Connecting to MongoDB (adjust settings as needed)
        self.db_client = pymongo.MongoClient(VARIABLES["mongodb"]["host"])
        self.db_name = self.db_client[VARIABLES["mongodb"]["database"]]
        self.collection_lotofacil_results = self.db_name[
            VARIABLES["mongodb"]["results_collection"]
        ]
        self.collection_predictions = self.db_name[
            VARIABLES["mongodb"]["predictions_collection"]
        ]

    def read_or_create_data_from_mongodb(self, dataframe: bool = False) -> list:
        """
        Reads existing data from the specified MongoDB collection.

        Args:
            dataframe (bool): Flag indicating whether to return data as a DataFrame.

        Returns:
            list: List of lottery data documents from the MongoDB collection.
        """
        try:
            result = self.collection_lotofacil_results.find()
            if result:
                if dataframe:
                    documents_list = [document for document in result]
                    existing_data = pd.DataFrame(documents_list)
                else:
                    existing_data = []
            else:
                existing_data = []

            logging.info("Creating a new list....")
        except pymongo.errors.PyMongoError as mongo_error:
            logging.error("Error reading data from MongoDB: %s", mongo_error)
            existing_data = []

        return existing_data

    def update_data_to_mongodb(self, lottery_data: list) -> None:
        """
        Updates the MongoDB collection with new lottery results.

        Args:
            lottery_data (list): List of lottery results documents.

        Returns:
            None
        """
        try:
            for document in lottery_data:
                filtro = {"concurso": document["concurso"]}
                existing_document = self.collection_lotofacil_results.find_one(filtro)
                if existing_document is None:
                    new_document = document
                    self.collection_lotofacil_results.insert_one(new_document)

            logging.info("MongoDB data updated.")
        except pymongo.errors.PyMongoError as mongo_error:
            logging.error("Error reading data from MongoDB: %s", mongo_error)

    def convert_string_to_list(self, dezenas_str: str) -> list:
        """
        Converts a string representation of numbers to a list.

        Args:
            dezenas_str (str): String representation of numbers.

        Returns:
            list: List of numbers.
        """
        if isinstance(dezenas_str, str):
            return [int(x) for x in dezenas_str.split(", ")]

        if isinstance(dezenas_str, list):
            return dezenas_str

        logging.error("Invalid input type. Expected str or list.")
        return []

    def update_dataframe_mongodb(self, lottery_data: list) -> list:
        """
        Updates the existing MongoDB data with new lottery results.

        Args:
            lottery_data (list): List of new lottery results.

        Returns:
            list: Updated list of lottery data documents.
        """
        existing_data = self.read_or_create_data_from_mongodb(False)
        for result in lottery_data:
            concurso = result["concurso"]
            data = result["data"]
            dezenas = self.convert_string_to_list(result["dezenas"])
            existing_data.append(
                {"concurso": concurso, "data": data, "dezenas": dezenas}
            )
        self.update_data_to_mongodb(existing_data)
        return existing_data

    def save_dataframe_mongodb(self, lottery_data: list) -> None:
        """
        Saves the provided lottery data to MongoDB.

        Args:
            lottery_data (list): List of lottery results documents.

        Returns:
            None
        """
        try:
            desired_keys = ["concurso", "data", "dezenas"]
            processed_lottery_data = [
                {key: document[key] for key in desired_keys}
                for document in lottery_data
            ]
            self.collection_lotofacil_results.insert_many(processed_lottery_data)
            logging.info("MongoDB data saved.")
        except pymongo.errors.PyMongoError as mongo_error:
            logging.error("Error reading data from MongoDB: %s", mongo_error)

    def save_predictions_to_mongodb(
        self, final_combinations: list, occurred: bool = False
    ) -> None:
        """
        Saves the predicted combinations to the MongoDB collection.

        Args:
            final_combinations (list):
                List of predicted combinations to be saved.
            occurred (bool):
                Indicates if the combination has occurred before.

        Returns:
            None
        """
        try:
            if self.combination_exists(final_combinations):
                logging.info(
                    "Combination %s already exists in predictions.", final_combinations
                )
            else:
                document = {
                    "combination": final_combinations,
                    "occurred_before": occurred,
                    "prediction_date": datetime.now(),
                }
                self.collection_predictions.insert_one(document)

            logging.info("Final combinations saved to MongoDB.")
        except pymongo.errors.PyMongoError as mongo_error:
            logging.error("Error saving predictions to MongoDB: %s", mongo_error)

    def combination_exists(self, combination: List[List[int]]) -> bool:
        """
        Check if a combination already exists in the predictions collection.

        Args:
            combination (List[int]): Combination to check.

        Returns:
            bool: True if the combination exists, False otherwise.
        """
        try:
            existing_combination = self.collection_predictions.find_one(
                {"combination": combination}
            )
            return existing_combination is not None
        except pymongo.errors.PyMongoError as mongo_error:
            logging.error("Error checking combination existence: %s", mongo_error)
            return False
