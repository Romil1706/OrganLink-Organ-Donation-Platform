import joblib
import pandas as pd

# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load(
    "organlink_model.pkl"
)

encoders = joblib.load(
    "label_encoders.pkl"
)

# ==========================================
# ENCODER
# ==========================================

def encode(column, value):

    try:

        return encoders[column].transform(
            [value]
        )[0]

    except:

        return 0

# ==========================================
# PREDICT MATCH
# ==========================================

def predict_match(

    donor_age,
    donor_gender,
    donor_blood_group,
    donor_organ,

    recipient_age,
    recipient_gender,
    recipient_blood_group,
    required_organ,

    hla_match_score,
    crossmatch_result

):

    row = pd.DataFrame([{

        "donor_age":
            donor_age,

        "donor_gender":
            encode(
                "donor_gender",
                donor_gender
            ),

        "donor_blood_group":
            encode(
                "donor_blood_group",
                donor_blood_group
            ),

        "donor_organ":
            encode(
                "donor_organ",
                donor_organ
            ),

        "recipient_age":
            recipient_age,

        "recipient_gender":
            encode(
                "recipient_gender",
                recipient_gender
            ),

        "recipient_blood_group":
            encode(
                "recipient_blood_group",
                recipient_blood_group
            ),

        "required_organ":
            encode(
                "required_organ",
                required_organ
            ),

        "hla_match_score":
            hla_match_score,

        "crossmatch_result":
            encode(
                "crossmatch_result",
                crossmatch_result
            )

    }])
    print("\nMODEL FEATURES:")
    print(model.feature_names_in_)

    print("\nROW FEATURES:")
    print(row.columns.tolist())
    prediction = model.predict(
        row
    )[0]

    probability = model.predict_proba(
        row
    )[0][1]
    print("Prediction:", prediction)
    print("Probabilities:", probability)
    return (
        int(prediction),
        round(
            probability * 100,
            2
        )
    )