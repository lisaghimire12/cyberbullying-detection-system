from django.db import models

class DetectionLog(models.Model):
    text = models.TextField()
    prediction = models.CharField(max_length=50)
    hash_value = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prediction
