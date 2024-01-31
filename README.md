# Lottery Prediction System

## Description
The Lottery Prediction System is a Python-based application designed to predict lottery numbers using Machine Learning algorithms. It employs Multi-Layer Perceptron (MLP) models to generate likely combinations for lottery draws.

The system allows users to fetch lottery data from an API, store it locally or in a MongoDB database, generate predictions based on historical data, and analyze the occurrence of numbers in previous draws.

## Creator
- **Luis Serrante**

## Technologies Used
- Python
- NumPy
- Pandas
- Scikit-learn
- Requests
- Pymongo

## Features
- Fetches lottery data from a designated API.
- Stores lottery data locally in Excel files or in a MongoDB database.
- Trains MLP models to predict future lottery numbers.
- Generates likely combinations for upcoming draws.
- Analyzes the occurrence of numbers in previous lottery draws.
- Provides command-line interface for easy interaction.

## Installation
To run this system locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Serrante/Lottery.git
    ```

2. Navigate to the project directory:
    ```bash
    cd Lottery
    ```

3. Install dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To use this system, follow these steps:

1. Ensure you have Python installed.

2. Clone the repository or download the source code.

3. Install the required dependencies as mentioned in the Installation section.

4. Run the main script:
    ```bash
    python main.py
    ```

5. Follow the command-line prompts to fetch data, generate predictions, and analyze results.

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.

2. Create a new branch (`git checkout -b feature/improvement`).

3. Make your changes.

4. Commit your changes (`git commit -am 'Add new feature'`).

5. Push to the branch (`git push origin feature/improvement`).

6. Create a new Pull Request.

## License
This project is licensed under the [MIT License](LICENSE).
