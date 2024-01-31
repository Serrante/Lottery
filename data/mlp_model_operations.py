"""mlp_model_operations.py"""
import random
from typing import List, Tuple
import logging
import numpy as np
import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler
from configuration.config import VARIABLES


class MLPModelOperations:
    """
    Class containing methods for Multi-Layer Perceptron (MLP) model operations.
    """

    @staticmethod
    def generate_final_combinations(fixed_numbers: List[int]) -> List[Tuple[int]]:
        """
        Generates final combinations of numbers.

        Args:
            fixed_numbers (List[int]): List of fixed numbers.

        Returns:
            List[Tuple[int]]: List of final combinations.
        """
        combinations_set = set()

        while len(combinations_set) < VARIABLES["prediction_count"]:
            random_number = random.randint(1, VARIABLES["max_number"])
            while random_number in fixed_numbers:
                random_number = random.randint(1, VARIABLES["max_number"])
            combination = tuple(fixed_numbers + [random_number])

            if combination not in combinations_set:
                combinations_set.add(combination)

        return list(combinations_set)

    @staticmethod
    def train_mlp_model(
        training_data: np.ndarray, training_targets: np.ndarray, max_iter: int = 15000
    ) -> MLPClassifier:
        """
        Train an MLP (Multi-Layer Perceptron) model.

        Args:
            training_data (np.ndarray): Input data for training.
            training_targets (np.ndarray): Target labels for training.
            max_iter (int): Maximum number of iterations for training.

        Returns:
            MLPClassifier: Trained MLP model.
        """
        scaler = MinMaxScaler()
        training_data_scaled = scaler.fit_transform(training_data.reshape(-1, 1))

        model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation="logistic",
            learning_rate="adaptive",
            max_iter=max_iter,
            random_state=100,
        )

        try:
            model.fit(training_data_scaled, training_targets)
        except ImportError as e:
            logging.error("Error during MLP model training: %s", e)

        return model

    @staticmethod
    def generate_random_numbers(model: MLPClassifier, num_draws: int = 15) -> List[int]:
        """
        Generate random numbers using an MLP model.

        Args:
            model (MLPClassifier): Trained MLP model.
            num_draws (int): Number of draws to generate.

        Returns:
            List[int]: List of generated numbers.
        """
        new_draws = np.random.uniform(1, 26, size=num_draws).reshape(-1, 1)
        probabilities = model.predict_proba(new_draws)

        sorted_probabilities = np.clip(
            np.argsort(-probabilities.mean(axis=0))[:14] + 1, 1, 25
        )

        unique_numbers = list(set(sorted_probabilities))

        while len(unique_numbers) < 14:
            random_number = random.randint(1, 25)
            if random_number not in unique_numbers:
                unique_numbers.append(random_number)

        return unique_numbers

    @staticmethod
    def generate_numbers_mlp(
        df: pd.DataFrame, training_data_size: int = 100
    ) -> pd.DataFrame:
        """
        Generate numbers using MLP (Multi-Layer Perceptron) model.

        Args:
            df (pd.DataFrame): DataFrame containing existing data.

        Returns:
            pd.DataFrame: DataFrame with the selected numbers.
        """
        numbers = df["dezenas"].to_numpy()

        numbers_integer = np.array([[int(num) for num in row] for row in numbers])

        flattened_numbers = np.concatenate(numbers_integer).ravel()

        binary_targets = np.column_stack(
            [np.isin(np.arange(1, 26), row).astype(int) for row in numbers_integer]
        )

        num_samples = min(len(flattened_numbers), len(binary_targets))

        flattened_numbers = flattened_numbers[:num_samples]

        binary_targets = binary_targets[:num_samples]

        indices = np.random.choice(
            num_samples, size=min(training_data_size, num_samples), replace=False
        )

        training_data = flattened_numbers[indices]

        training_targets = binary_targets[indices]

        model = MLPModelOperations.train_mlp_model(training_data, training_targets)

        selected_numbers = MLPModelOperations.generate_random_numbers(
            model, training_data_size
        )

        predictions_df = pd.DataFrame(
            [selected_numbers],
            columns=[f"Number_{i}" for i in range(1, len(selected_numbers) + 1)],
        )

        return predictions_df
