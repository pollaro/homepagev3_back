from django.db import models


class HBLManager(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, null=True)
    guid = models.CharField(max_length=64, default=None, null=True)