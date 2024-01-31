"""Main"""
import os
import argparse
import logging
from typing import List
import numpy as np
import pandas as pd

from data.lottery_data import LotteryDataManager
from data.data_frame_operations import DataFrameManager
from data.data_frame_operations_mongodb import DataFrameManagerMongoDB
from data.mlp_model_operations import MLPModelOperations
from configuration.config import VARIABLES


class LotteryHandler:
    """
    Handles the lottery data processing and prediction generation.

    This class encapsulates functionality for handling command-line arguments,
    reading data from different storage sources, generating predictions using
    MLP models, and printing final combinations and number occurrences.

    Attributes:
        storage_options (list): A list of available storage options.
        log_file_path (str): The path to the log file directory.
        log_file_name (str): The name of the log file.
        excel_file_path (str): The path to the Excel file directory.
        excel_file_name (str): The name of the Excel file.

    Methods:
        configure_logging():
            Configures the logging settings.
        parse_command_line_arguments():
            Parses command-line arguments.
        get_sorted_combined_numbers(df):
            Generates and sorts combined numbers from MLP predictions.
        print_final_combinations(final_combinations, df_dezenas):
            Prints final combinations and checks for occurrences.
        handle_predictions(df):
            Handles the generation of predictions and prints final combinations.
        count_and_print_occurrences(df):
            Counts and prints number occurrences in lottery results.
        handle_occurrences(df):
            Handles the printing of number occurrences in lottery results.
        handle_command_line_arguments():
            Handles command-line arguments and orchestrates data processing.
    """

    def __init__(self):
        self.storage_options = VARIABLES["storage_options"]
        self.log_file_path = VARIABLES["log_file_path"]
        self.log_file_name = VARIABLES["log_file_name"]
        self.excel_file_path = VARIABLES["excel_file_path"]
        self.excel_file_name = VARIABLES["excel_file_name"]
        self.configure_logging()

    def configure_logging(self) -> None:
        """
        Configure logging settings.

        Returns:
            None
        """
        log_file_path = os.path.join(self.log_file_path, self.log_file_name)
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def parse_command_line_arguments(self) -> argparse.Namespace:
        """
        Parses command-line arguments.

        Returns:
            argparse.Namespace: Parsed command-line arguments.
        """
        parser = argparse.ArgumentParser(description="Process some integers.")
        parser.add_argument(
            "--predictions", type=str, default="Não", help="Generate predictions"
        )
        parser.add_argument(
            "--get_games", type=str, default="Não", help="Get for games in the API"
        )
        parser.add_argument(
            "--storage",
            type=str,
            default="Excel",
            choices=self.storage_options,
            help="Defines how data is stored",
        )
        return parser.parse_args()

    def get_sorted_combined_numbers(self, df: pd.DataFrame) -> List[int]:
        """
        Generate and sort combined numbers from MLP predictions.

        Args:
            df (pd.DataFrame): DataFrame containing existing data.

        Returns:
            List[int]: Sorted list of combined numbers.
        """
        mpl = MLPModelOperations()
        predicted_numbers = mpl.generate_numbers_mlp(df).values.flatten()
        return sorted(list(predicted_numbers))

    def print_final_combinations(
        self, final_combinations: List[List[int]], df_dezenas: List[np.array]
    ) -> None:
        """
        Print final combinations and indicate if they have occurred before.

        Args:
            final_combinations (List[List[int]]): List of final combinations.
            df_dezenas (List[np.array]): List of existing combinations.

        Returns:
            None
        """
        mongodb = DataFrameManagerMongoDB()
        for j, final_combination in enumerate(final_combinations, start=1):
            final_combination_array = np.array(final_combination)
            combination = final_combination_array.tolist()

            if any(np.array_equal(final_combination_array, x) for x in df_dezenas):
                mongodb.save_predictions_to_mongodb(combination, True)
                print(f"Final Combination {j}: {final_combination} (Already occurred)")
            else:
                mongodb.save_predictions_to_mongodb(combination, False)
                print(f"Final Combination {j}: {final_combination}")

    def handle_predictions(self, df: pd.DataFrame) -> None:
        """
        Handles the generation of predictions and prints the final combinations.

        Args:
            df (pd.DataFrame): DataFrame containing existing data.

        Returns:
            None
        """
        mpl = MLPModelOperations()
        df_dezenas = [
            np.array([int(num) for num in dezenas]) for dezenas in df["dezenas"]
        ]
        combined_numbers = self.get_sorted_combined_numbers(df)
        final_combinations = mpl.generate_final_combinations(combined_numbers)
        self.print_final_combinations(final_combinations, df_dezenas)

    def count_and_print_occurrences(self, df: pd.DataFrame) -> None:
        """
        Count and print number occurrences in lottery results.

        Args:
            df (pd.DataFrame): DataFrame containing lottery results.

        Returns:
            None
        """
        all_numbers = [num for sublist in df["dezenas"] for num in sublist]
        number_counts = pd.Series(all_numbers, dtype="float64").value_counts()
        total_occurrences = number_counts.sum()
        for number, count in number_counts.items():
            percentage = (count / total_occurrences) * 100
            print(
                f"Number: {number}, "
                f"Occurrences: {count}-{total_occurrences}, "
                f"Percentage: {percentage:.2f}%"
            )

    def handle_occurrences(self, df: pd.DataFrame) -> None:
        """
        Handles the printing of number occurrences in the lottery results.

        Args:
            df (pd.DataFrame): DataFrame containing lottery results.

        Returns:
            None
        """
        self.count_and_print_occurrences(df)

    def handle_command_line_arguments(self) -> None:
        """
        Handles command-line arguments.

        Returns:
            None
        """
        args = self.parse_command_line_arguments()

        if args.get_games.lower() == "sim":
            lottery = LotteryDataManager()
            lottery.handle_api_request(self.excel_file_path, self.excel_file_name, args)

        if args.storage.lower() in self.storage_options:
            if args.storage.lower() == "excel":
                excel = DataFrameManager()
                df = excel.read_or_create_dataframe(
                    self.excel_file_path, self.excel_file_name
                )
            elif args.storage.lower() == "database":
                mongodb = DataFrameManagerMongoDB()
                df = mongodb.read_or_create_data_from_mongodb(True)
        else:
            logging.error(
                "Invalid storage option: %s. Please use %s. Aborting.",
                args.storage,
                self.storage_options,
            )
            return

        if args.predictions.lower() == "sim":
            self.handle_predictions(df)
        else:
            self.handle_occurrences(df)


if __name__ == "__main__":
    lottery_handler = LotteryHandler()
    lottery_handler.handle_command_line_arguments()
