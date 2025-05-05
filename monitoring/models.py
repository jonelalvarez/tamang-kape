# from django.db import models

# class CaffeineIntake(models.Model):
#     user_id = models.IntegerField()
#     drink_name = models.CharField(max_length=255)
#     caffeine_amount = models.FloatField()
#     serving_size = models.FloatField(null=True, blank=True)  # ✅ New Field
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.drink_name} - {self.caffeine_amount}mg ({self.serving_size}ml)"

from django.db import models
from django.contrib.auth.models import User

class CaffeineIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to User model
    drink_name = models.CharField(max_length=255)
    caffeine_amount = models.FloatField()
    serving_size = models.FloatField(null=True, blank=True)
    timestamp =  models.DateTimeField()  # 🆕 New field to store selected DateTime
    drink_id = models.IntegerField(null=True, blank=True)  # 🆕 New field to store the drink's ID
    categoryType = models.CharField(max_length=100, null=True, blank=True)
    
    is_created = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.drink_name} - {self.caffeine_amount}mg ({self.serving_size}ml)"
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
    bDate = models.DateField(null=True, blank=True)
    
    HEALTH_CHOICES = [
        ('none', 'None'),
        ('pregnant', 'Pregnant'),
        ('lactating', 'Lactating'),
        ('heart', 'Heart Condition'),
        ('hypertension', 'Hypertension'),
        ('diabetes', 'Diabetes'),
    ]

    health_condition = models.CharField(
        max_length=20, choices=HEALTH_CHOICES, default='none'
    )

    def __str__(self):
        return self.user.username
    
class CaffeineProduct(models.Model):
    drinkName = models.CharField(max_length=255)
    volumeML = models.IntegerField()
    calorie = models.IntegerField()
    caffeine = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=100)
    type = models.IntegerField()
    status = models.BooleanField(default=True)

    # 👉 Add these:
    flOz = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mgPerFlOz = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mgPer100ml = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return self.drinkName


class HealthTip(models.Model):
    title = models.CharField(max_length=500)
    detail = models.TextField()
    link = models.CharField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=100)
    tip = models.TextField()
    icon_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
    
class CreatedDrink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who created it
    drinkName = models.CharField(max_length=255)
    volumeML = models.IntegerField(null=True, blank=True)
    caffeine = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    mgPer100ml = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100)
    measurementMethod = models.CharField(max_length=50, null=True, blank=True)  # Add this line
    status = models.BooleanField(default=True)
    is_created = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.drinkName} created by user ID: {self.user.id}"