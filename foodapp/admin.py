from django.contrib import admin

from .models import (
    MealRecord,
    DemandForecast,
    Recipient,
    SurplusFood,
    Redistribution
)


# ==================================================
# MEAL RECORD
# ==================================================

@admin.register(MealRecord)
class MealRecordAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "attendance",
        "meals_prepared",
        "meals_consumed",
        "holiday",
        "rainfall",
        "temperature",
    )

    list_filter = (
        "holiday",
        "date",
    )

    search_fields = (
        "date",
    )

    ordering = (
        "-date",
    )


# ==================================================
# DEMAND FORECAST
# ==================================================

@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "predicted_demand",
        "recommended_preparation",
    )

    list_filter = (
        "date",
    )

    ordering = (
        "-date",
    )


# ==================================================
# RECIPIENT
# ==================================================

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "recipient_type",
        "capacity",
        "verified",
    )

    list_filter = (
        "recipient_type",
        "verified",
    )

    search_fields = (
        "name",
        "recipient_type",
    )


# ==================================================
# SURPLUS FOOD
# ==================================================

@admin.register(SurplusFood)
class SurplusFoodAdmin(admin.ModelAdmin):

    list_display = (
        "food_name",
        "quantity",
        "storage_temperature",
        "storage_time_hours",
        "status",
        "is_safe",
        "created_at",
    )

    list_filter = (
        "status",
        "is_safe",
    )

    search_fields = (
        "food_name",
    )

    ordering = (
        "-created_at",
    )


# ==================================================
# REDISTRIBUTION
# ==================================================

@admin.register(Redistribution)
class RedistributionAdmin(admin.ModelAdmin):

    list_display = (
        "surplus",
        "recipient",
        "quantity",
        "distributed_at",
    )

    list_filter = (
        "recipient",
        "distributed_at",
    )

    search_fields = (
        "surplus__food_name",
        "recipient__name",
        "recipient__recipient_type",
    )

    ordering = (
        "-distributed_at",
    )