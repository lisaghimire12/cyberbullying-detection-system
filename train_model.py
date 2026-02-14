import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score



print("\nLoading dataset...")
data = pd.read_csv("data/dataset.csv")

print("Total Rows:", len(data))

# Clean
data = data.dropna()
data["Text"] = data["Text"].astype(str).str.lower()
data["Label"] = data["Label"].astype(str)

print("\nLabel Distribution:")
print(data["Label"].value_counts())

X = data["Text"]
y = data["Label"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Vectorizer
vectorizer = TfidfVectorizer(
    max_features=12000,
    ngram_range=(1,2),
    stop_words="english"
)
TfidfVectorizer(
    ngram_range=(1,2),
    max_features=20000,
    stop_words="english"
)


X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model
model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

print("\nTraining model...")
model.fit(X_train_vec, y_train)

# Evaluate
preds = model.predict(X_test_vec)

print("\nAccuracy:", accuracy_score(y_test, preds))
print("\nClassification Report:\n")
print(classification_report(y_test, preds))

# Save
pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))

print("\nModel & Vectorizer saved successfully!")
