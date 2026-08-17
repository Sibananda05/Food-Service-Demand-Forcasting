from django.urls import path

from . import views


urlpatterns = [

    # ==================================================
    # HOME
    # ==================================================

    path(
        "",
        views.home,
        name="home"
    ),


    # ==================================================
    # DASHBOARD
    # ==================================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),


    # ==================================================
    # DEMAND PREDICTION
    # ==================================================

    path(
        "predict/",
        views.predict_demand,
        name="predict"
    ),


    # ==================================================
    # FOOD SAFETY
    # ==================================================

    path(
        "food-safety/",
        views.check_food_safety,
        name="food_safety"
    ),


    # ==================================================
    # SURPLUS FOOD
    # ==================================================

    path(
        "add-surplus/",
        views.add_surplus_food,
        name="add_surplus"
    ),

    path(
        "surplus-list/",
        views.surplus_list,
        name="surplus_list"
    ),


    # ==================================================
    # REDISTRIBUTION
    # ==================================================

    path(
        "redistribute/<int:food_id>/",
        views.redistribute_food,
        name="redistribute"
    ),


    # ==================================================
    # RECIPIENT MANAGEMENT
    # ==================================================

    path(
        "recipients/",
        views.recipient_list,
        name="recipient_list"
    ),

    path(
        "recipients/add/",
        views.add_recipient,
        name="add_recipient"
    ),

    path(
        "recipients/verify/<int:recipient_id>/",
        views.verify_recipient,
        name="verify_recipient"
    ),
    path(
    "weather-data/",
    views.weather_data,
    name="weather_data"
),

]

