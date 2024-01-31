"""data_frame_operations.py"""
import os
import ast
import logging
from typing import List
import pandas as pd


class DataFrameManager:
    """
    A utility class for managing operations on pandas DataFrames.

    This class provides static methods to perform common operations
    such as reading or creating DataFrames from Excel files, updating
    DataFrames with new data, and saving DataFrames to Excel files.

    Attributes:
        None

    Methods:
        read_or_create_dataframe(path: str, filename: str) -> pd.DataFrame:
            Reads existing data from the specified Excel file or creates a new DataFrame.

        create_new_dataframe() -> pd.DataFrame:
            Creates a new DataFrame with specified columns.

        convert_string_to_list(df: pd.DataFrame, column: str) -> None:
            Converts string representations to a list in the specified DataFrame column.

        update_dataframe(df: pd.DataFrame, lottery_data: List[dict]) -> pd.DataFrame:
            Updates the DataFrame with new lottery results.

        save_dataframe(df: pd.DataFrame, path: str, filename: str) -> None:
            Saves the DataFrame to an Excel file.
    """

    @staticmethod
    def read_or_create_dataframe(path: str, filename: str) -> pd.DataFrame:
        """
        Reads existing data from the specified Excel file or creates a new DataFrame.

        Args:
            path (str): Path to the Excel file.

        Returns:
            pd.DataFrame: DataFrame containing existing data or a new DataFrame.
        """
        try:
            if os.path.exists(os.path.join(path, filename)):
                existing_data = pd.read_excel(os.path.join(path, filename))
                DataFrameManager.convert_string_to_list(existing_data, "dezenas")
                return existing_data

            logging.info("File not found. Creating a new DataFrame.")
            return DataFrameManager.create_new_dataframe()
        except pd.errors.EmptyDataError as e:
            logging.error("Error loading DataFrame: %s", e)
            return DataFrameManager.create_new_dataframe()

    @staticmethod
    def create_new_dataframe() -> pd.DataFrame:
        """
        Creates a new DataFrame with specified columns.

        Returns:
            pd.DataFrame: New DataFrame.
        """
        columns = ["concurso", "data", "dezenas"]
        return pd.DataFrame(columns=columns)

    @staticmethod
    def convert_string_to_list(df: pd.DataFrame, column: str) -> None:
        """
        Converts string representations to a list in the specified DataFrame column.

        Args:
            df (pd.DataFrame): DataFrame to be modified.
            column (str): Name of the column containing string representations to convert.

        Returns:
            None
        """
        df[column] = df[column].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

    @staticmethod
    def update_dataframe(df: pd.DataFrame, lottery_data: List[dict]) -> pd.DataFrame:
        """
        Updates the DataFrame with new lottery results.

        Args:
            df (pd.DataFrame): DataFrame containing existing data.
            lottery_data (List[dict]): List of lottery results.

        Returns:
            pd.DataFrame: DataFrame with the selected numbers
        """
        # Iterate over the new lottery results
        for result in lottery_data:
            concurso = result["concurso"]
            data = result["data"]
            dezenas = result["dezenas"]

            # Convert the list of numbers to a string
            dezenas_str = ", ".join(map(str, [int(x) for x in dezenas]))

            # Check if the lottery draw is already in the DataFrame
            if concurso in df["concurso"].values:
                # Update the corresponding values
                df.loc[df["concurso"] == concurso, ["data", "dezenas"]] = [
                    data,
                    dezenas_str,
                ]
            else:
                # Add a new row to the DataFrame
                new_row = pd.DataFrame(
                    {"concurso": [concurso], "data": [data], "dezenas": [dezenas_str]}
                )
                df = pd.concat([df, new_row], ignore_index=True)

        return df

    @staticmethod
    def save_dataframe(df: pd.DataFrame, path: str, filename: str) -> None:
        """
        Saves the DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): DataFrame to be saved.
            path (str): Path to the Excel file.

        Returns:
            None
        """
        # Sort the DataFrame by the 'Concurso' column
        df = df.sort_values(by="concurso", ascending=False)

        # Save the updated DataFrame to the Excel file
        df.to_excel(os.path.join(path, filename), index=False)
        logging.info("Excel file updated at: %s", os.path.join(path, filename))
