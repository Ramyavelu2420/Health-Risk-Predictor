import pandas as pd

def load_user_history(user_id):
    try:
        df = pd.read_csv('user_history.csv', header=None)
        df.columns = ['User_ID', 'Age', 'Gender', 'Symptoms', 'Medical_History', 'Medications', 'Lab_Reports', 'Lifestyle', 'Prediction', 'Date']
        user_df = df[df['User_ID'] == user_id]
        return user_df
    except FileNotFoundError:
        return pd.DataFrame()
