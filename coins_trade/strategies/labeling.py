import pandas as pd
import talib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle


def read_data():
    df = pd.read_csv('./data/MATICUSDT_feature.csv')
    return df


df = read_data()

N = 3
df['future_close'] = df['close'].shift(-N)
df['label'] = (df['future_close'] > df['close']).astype(int)

# Drop the 'future_close' as it's no longer needed after labeling
df.drop(columns=['future_close'], inplace=True)

# Assuming df is your DataFrame and 'label' is your target variable
X = df.drop(['label'], axis=1)  # Features
y = df['label']  # Target

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Convert datetime columns to Unix timestamp (seconds since epoch)
X_train['open_time'] = pd.to_datetime(X_train['open_time']).view(int) / 1e9
X_test['open_time'] = pd.to_datetime(X_test['open_time']).view(int) / 1e9
X_train['close_time'] = pd.to_datetime(X_train['close_time']).view(int) / 1e9
X_test['close_time'] = pd.to_datetime(X_test['close_time']).view(int) / 1e9
# Initialize the model
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate the model
print(classification_report(y_test, predictions))
with open('./model/random_forest_model.sav', 'wb') as file:
    pickle.dump(model, file)
