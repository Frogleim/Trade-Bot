import pandas as pd
import talib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


def read_data():
    df = pd.read_csv('./data/MATICUSDT_feature.csv')
    return df


df = read_data()

N = 3
df['future_close'] = df['close'].shift(-N)
df['label'] = (df['future_close'] > df['close']).astype(int)
# Assuming df is your DataFrame and 'label' is your target variable
X = df.drop(['label'], axis=1)  # Features
y = df['label']  # Target

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Check data types in your DataFrame
print(X_train.dtypes)

# Initialize the model
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# 
# # Train the model# Check data types in your DataFrame
# print(X_train.dtypes)
# model.fit(X_train, y_train)
# # Make predictions
# predictions = model.predict(X_test)
#
# # Evaluate the model
# print(classification_report(y_test, predictions))