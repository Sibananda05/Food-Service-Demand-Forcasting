from django.db import models
from django.core.validators import MinValueValidator


# ==================================================
# MEAL RECORD
# ==================================================

class MealRecord(models.Model):

    date = models.DateField()

    attendance = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    meals_prepared = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    meals_consumed = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    holiday = models.BooleanField(
        default=False
    )

    rainfall = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)]
    )

    temperature = models.FloatField(
        default=25.0
    )

    def __str__(self):
        return str(self.date)


# ==================================================
# DEMAND FORECAST
# ==================================================

class DemandForecast(models.Model):

    date = models.DateField()

    predicted_demand = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    recommended_preparation = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return str(self.date)


# ==================================================
# RECIPIENT
# ==================================================

class Recipient(models.Model):

    name = models.CharField(
        max_length=150
    )

    recipient_type = models.CharField(
        max_length=100
    )

    capacity = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name


# ==================================================
# SURPLUS FOOD
# ==================================================

class SurplusFood(models.Model):

    food_name = models.CharField(
        max_length=100
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(0)]
    )

    storage_temperature = models.FloatField(
        default=4.0
    )

    storage_time_hours = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)]
    )

    status = models.CharField(
        max_length=20,

        choices=[
            ("PENDING", "Pending"),
            ("SAFE", "Safe"),
            ("UNSAFE", "Unsafe"),
            ("REDISTRIBUTED", "Redistributed"),
        ],

        default="PENDING"
    )

    is_safe = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def check_safety(self):

        if (
            self.storage_temperature <= 5
            and self.storage_time_hours <= 24
        ):

            self.is_safe = True
            self.status = "SAFE"

        else:

            self.is_safe = False
            self.status = "UNSAFE"

        self.save(
            update_fields=[
                "is_safe",
                "status"
            ]
        )

    def __str__(self):

        return self.food_name


# ==================================================
# REDISTRIBUTION
# ==================================================

class Redistribution(models.Model):

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    surplus = models.ForeignKey(
        SurplusFood,
        on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE
    )

    distributed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.surplus.food_name} → "
            f"{self.recipient.name}"
        )

