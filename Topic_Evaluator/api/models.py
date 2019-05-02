from django.db import models

# Create your models here.
class WordCount(models.Model):
    word = models.CharField(max_length=100, primary_key=True)
    count = models.BigIntegerField()