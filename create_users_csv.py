import csv
import os

# File path
csv_file = 'users.csv'

# Header and sample data
headers = ['email', 'password', 'phone']
sample_user = ['ramyavelu2420@gmail.com', '1234', '+919345823175']

# Check if the CSV exists
file_exists = os.path.isfile(csv_file)

# Create or append
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)

    # Write header if file doesn't exist
    if not file_exists:
        writer.writerow(headers)
        print("Header added.")

    # Write a sample user (only if it doesn't exist)
    with open(csv_file, mode='r') as check_file:
        users = check_file.read()
        if sample_user[0] not in users:
            writer.writerow(sample_user)
            print("Sample user added.")
        else:
            print("Sample user already exists.")
