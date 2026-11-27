import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv(
    "organlink_synthetic_dataset_20000.csv"
)

print("Dataset Loaded Successfully")

# ==========================================
# CLEAN DATA
# ==========================================

df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

print("Shape:", df.shape)

# ==========================================
# REMOVE UNNECESSARY COLUMNS
# ==========================================

if 'verification_status' in df.columns:
    df.drop(
        'verification_status',
        axis=1,
        inplace=True
    )

if 'compatibility_score' in df.columns:
    df.drop(
        'compatibility_score',
        axis=1,
        inplace=True
    )

# ==========================================
# ENCODE CATEGORICAL COLUMNS
# ==========================================

label_encoders = {}

categorical_columns = [

    'donor_gender',
    'donor_blood_group',
    'donor_organ',

    'recipient_gender',
    'recipient_blood_group',
    'required_organ',

    'crossmatch_result'

]

for col in categorical_columns:

    le = LabelEncoder()

    df[col] = le.fit_transform(
        df[col]
    )

    label_encoders[col] = le

# ==========================================
# FEATURES AND TARGET
# ==========================================

X = df.drop(
    "compatible",
    axis=1
)

y = df["compatible"]

print("\nFeatures Used:")
print(X.columns.tolist())

# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42

)

# ==========================================
# RANDOM FOREST
# ==========================================

model = RandomForestClassifier(

    n_estimators=200,

    random_state=42

)

model.fit(
    X_train,
    y_train
)

# ==========================================
# EVALUATE
# ==========================================

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    "\nAccuracy:",
    round(
        accuracy * 100,
        2
    ),
    "%"
)

# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(

    model,

    "organlink_model.pkl"

)

joblib.dump(

    label_encoders,

    "label_encoders.pkl"

)

print("\nModel Saved")
print("Encoders Saved")