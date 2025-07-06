import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Load the dataset
df = pd.read_csv("Rule_Based_Health_Risk_Dataset.csv")

# Encode categorical columns
label_encoders = {}
for col in ['Gender', 'Symptoms', 'Medical_History', 'Medications', 'Lab_Reports', 'Lifestyle', 'Risk_Level']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # Save encoder for future use

# Define features and target
X = df.drop(['Patient_ID', 'Risk_Level'], axis=1)
y = df['Risk_Level']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and calculate accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the model
with open("health_model.pkl", "wb") as f:
    pickle.dump(model, f)

# Save the encoders (optional, but helpful if you want dynamic encoding later)
with open("encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)
