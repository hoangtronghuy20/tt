from django.db import models
from django.db.models.functions import Now
from django.contrib.auth.models import User

class Part(models.Model):
    name = models.CharField(max_length = 200)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __str__(self):
        return self.name

class Test(models.Model):
    part_id = models.ForeignKey(Part, on_delete=models.CASCADE)
    name = models.CharField(max_length = 250)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __str__(self):
        return self.name

class Question(models.Model):
    ANSWER = {
        "A": "A",
        "B": "B",
        "C": "C",
        "D": "D",
    }
    part_id = models.ForeignKey(Part, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.TextField(blank=True)
    photo = models.ImageField(upload_to='images/', blank=True)
    audio = models.FileField(upload_to='audio/', blank=True)
    option_a = models.TextField(blank=True)
    option_b = models.TextField(blank=True)
    option_c = models.TextField(blank=True)
    option_d = models.TextField(blank=True)
    correct = models.CharField(max_length=1, choices=ANSWER)
    isRelease = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __str__(self):
        return self.question

class Language(models.Model):
    REGION = {
        "1": "en",
        "2": "vi",
        "3": "jp",
        "4": "fr",
    }
    language = models.CharField(max_length = 50)
    region = models.CharField(max_length = 50, choices=REGION)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __str__(self):
        return self.language

class Translate(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True)
    language_id = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True)
    option_a = models.TextField(blank=True)
    option_b = models.TextField(blank=True)
    option_c = models.TextField(blank=True)
    option_d = models.TextField(blank=True)
    hint = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __str__(self):
        return self.option_a

class Result(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    isListening = models.BooleanField(default=False)
    score = models.IntegerField()
    time = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __int__(self):
        return self.score

class Feedback(models.Model):
    user_id = models.CharField(max_length = 50, null=True, blank=True)
    version = models.CharField(max_length = 50)
    android = models.CharField(max_length = 50)
    fullname = models.CharField(max_length = 150, null=True, blank=True)
    content = models.TextField(max_length = 50)
    created = models.DateTimeField(auto_now_add=True, db_default=Now())

    def __str__(self):
        return self.content
