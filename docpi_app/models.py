from django.db import models

# Create your models here.
class User(models.Model):
    user = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=50)
    password = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
        

class Documents(models.Model):
    # userDetails = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    userDetails = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(unique=True, max_length=150)
    shape = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
        
