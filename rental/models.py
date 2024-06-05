from django.db import models
from django.contrib.auth.models import User

class UAV(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    weight = models.FloatField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.brand} {self.model}"

class RentalRecord(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    uav = models.ForeignKey(UAV, on_delete=models.CASCADE)
    rental_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.member.username} - {self.uav.brand} {self.uav.model}"
