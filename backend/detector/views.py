import json
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

model = pickle.load(open("../model/model.pkl", "rb"))
vectorizer = pickle.load(open("../model/vectorizer.pkl", "rb"))

@csrf_exempt
def predict(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data["message"]

        vec = vectorizer.transform([text])
        prediction = model.predict(vec)[0]

        return JsonResponse({"prediction": prediction})
