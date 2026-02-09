import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import pickle

# ============================
# 1. LOAD & CLEAN DATA
# ============================

data = pd.read_csv("data/dataset.csv")

data = data.dropna(subset=["Text", "Label"])
data["Text"] = data["Text"].astype(str).str.lower()
data["Label"] = data["Label"].astype(str)

X = data["Text"]
y = data["Label"]

# ============================
# 2. STRATIFIED SPLIT
# keeps class balance
# ============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ============================
# 3. PIPELINE (VECTORIZER + MODEL)
# ============================

pipeline = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9,
            sublinear_tf=True,
            stop_words="english"
        )
    ),
    (
        "clf",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="liblinear"
        )
    )
])

# ============================
# 4. TRAIN
# ============================

pipeline.fit(X_train, y_train)

# ============================
# 5. EVALUATE
# ============================

predictions = pipeline.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, predictions))
print("\nDetailed Report:\n")
print(classification_report(y_test, predictions))

# ============================
# 6. SAVE MODEL
# ============================

pickle.dump(pipeline, open("model/model.pkl", "wb"))

print("\nTraining Completed & Model Saved")
