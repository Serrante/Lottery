"""Configurations"""
import os

VARIABLES = {
    "mongodb": {
        "host": "localhost",
        "port": 27017,
        "database": "serrante",
        "results_collection": "lotofacil_results",
        "predictions_collection": "lotofacil_predictions",
    },
    "excel_file_path": os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "excel"
    ),
    "excel_file_name": "resultados_lotofacil.xlsx",
    "log_file_path": os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
    ),
    "log_file_name": "lottery.log",
    "api": "https://loteriascaixa-api.herokuapp.com/api/lotofacil/",
    "max_number": 25,
    "prediction_count": 11,
    "storage_options": ["excel", "database"],
}
