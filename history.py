# history.py

import csv
from datetime import datetime

CSV_FILE = 'user_history.csv'

def save_history(user_id, input_data, result):
    """
    Save the user input and prediction result to a CSV file.
    
    :param user_id: Unique ID (or 'anonymous') to track user
    :param input_data: List of features submitted by user
    :param result: Predicted health risk label
    """
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id] + input_data + [result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])


def get_user_history(user_id):
    """
    Retrieve history of predictions for a specific user ID.
    
    :param user_id: The ID used to track the user
    :return: List of rows [age, gender, ..., result, date]
    """
    history = []
    try:
        with open(CSV_FILE, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == user_id:
                    history.append(row[1:])  # skip user_id in display
    except FileNotFoundError:
        pass  # No history yet

    return history
