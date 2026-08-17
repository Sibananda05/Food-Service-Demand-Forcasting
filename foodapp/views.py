import os
import joblib
import json 

import requests
from django.conf import settings
from datetime import date
from django.http import JsonResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.db.models import Sum

from .models import (
    SurplusFood,
    Redistribution,
    DemandForecast,
    Recipient
)

from .forms import (
    SurplusFoodForm,
    RedistributionForm
)


# ==================================================
# LOAD TRAINED ML MODEL
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "demand_model.pkl"
)

model = joblib.load(MODEL_PATH)


# ==================================================
# HOME PAGE
# ==================================================

def home(request):

    return render(
        request,
        "home.html"
    )


# ==================================================
# LIVE WEATHER API
# ==================================================

def get_weather_data(city):

    try:

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        temperature = data["main"]["temp"]

        rainfall = data.get(
            "rain",
            {}
        ).get(
            "1h",
            0
        )

        weather = data["weather"][0]["description"]

        return {
            "temperature": temperature,
            "rainfall": rainfall,
            "weather": weather
        }

    except (
        requests.RequestException,
        KeyError,
        TypeError,
        ValueError
    ):

        return None

def weather_data(request):

    city = request.GET.get("city", "").strip()

    if not city:
        return JsonResponse(
            {"error": "Please enter a city name."},
            status=400
        )

    try:

        weather = get_weather_data(city)

        return JsonResponse({
            "city": city,
            "temperature": weather["temperature"],
            "rainfall": weather["rainfall"],
            "weather": weather["weather"],
        })

    except Exception as e:

        return JsonResponse(
            {
                "error": "Unable to fetch weather data."
            },
            status=500
        )

# ==================================================
# DASHBOARD / ANALYTICS
# ==================================================

def dashboard(request):

    # ----------------------------------------------
    # DEMAND STATISTICS
    # ----------------------------------------------

    total_predictions = DemandForecast.objects.count()

    total_predicted_meals = (
        DemandForecast.objects.aggregate(
            total=Sum("predicted_demand")
        )["total"] or 0
    )

    total_recommended_meals = (
        DemandForecast.objects.aggregate(
            total=Sum("recommended_preparation")
        )["total"] or 0
    )


    # ----------------------------------------------
    # SURPLUS FOOD STATISTICS
    # ----------------------------------------------

    total_surplus_food = (
        SurplusFood.objects.count()
    )

    total_surplus_quantity = (
        SurplusFood.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    safe_food = (
        SurplusFood.objects.filter(
            status="SAFE"
        ).count()
    )

    unsafe_food = (
        SurplusFood.objects.filter(
            status="UNSAFE"
        ).count()
    )

    redistributed_food = (
        SurplusFood.objects.filter(
            status="REDISTRIBUTED"
        ).count()
    )


    # ----------------------------------------------
    # REDISTRIBUTION STATISTICS
    # ----------------------------------------------

    total_redistributions = (
        Redistribution.objects.count()
    )

    total_redistributed_quantity = (
        Redistribution.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )


    # ----------------------------------------------
    # RECIPIENT STATISTICS
    # ----------------------------------------------

    total_recipients = (
        Recipient.objects.count()
    )

    verified_recipients = (
        Recipient.objects.filter(
            verified=True
        ).count()
    )


    # ----------------------------------------------
    # RECENT PREDICTIONS
    # ----------------------------------------------

    recent_predictions = (
        DemandForecast.objects
        .all()
        .order_by("-date")[:5]
    )


    # ----------------------------------------------
    # CHART DATA
    # ----------------------------------------------

    chart_predictions = list(
        DemandForecast.objects
        .all()
        .order_by("-date")[:10]
    )

    # Reverse so the chart displays
    # oldest → newest

    chart_predictions.reverse()

    chart_labels = json.dumps([
    prediction.date.strftime("%d %b")
    for prediction in chart_predictions
])

    chart_values = json.dumps([
    prediction.predicted_demand
    for prediction in chart_predictions
])

    chart_values = [
        prediction.predicted_demand
        for prediction in chart_predictions
    ]


    # ----------------------------------------------
    # RECENT SURPLUS FOOD
    # ----------------------------------------------

    recent_surplus = (
        SurplusFood.objects
        .all()
        .order_by("-created_at")[:5]
    )


    # ----------------------------------------------
    # RECENT REDISTRIBUTIONS
    # ----------------------------------------------

    recent_redistributions = (
        Redistribution.objects
        .all()
        .order_by("-distributed_at")[:5]
    )

    # ----------------------------------------------
# IMPACT ANALYTICS
# ----------------------------------------------

    if total_surplus_quantity > 0:
      redistribution_rate = round(
        (total_redistributed_quantity / total_surplus_quantity) * 100,
        1
    )
    else:
     redistribution_rate = 0

    estimated_food_saved = total_redistributed_quantity


    # ----------------------------------------------
    # DASHBOARD CONTEXT
    # ----------------------------------------------

    context = {
        # Impact
        "redistribution_rate": redistribution_rate,
        "estimated_food_saved": estimated_food_saved,

        # Demand
        "total_predictions":
            total_predictions,

        "total_predicted_meals":
            total_predicted_meals,

        "total_recommended_meals":
            total_recommended_meals,


        # Surplus
        "total_surplus_food":
            total_surplus_food,

        "total_surplus_quantity":
            total_surplus_quantity,

        "safe_food":
            safe_food,

        "unsafe_food":
            unsafe_food,

        "redistributed_food":
            redistributed_food,


        # Redistribution
        "total_redistributions":
            total_redistributions,

        "total_redistributed_quantity":
            total_redistributed_quantity,


        # Recipients
        "total_recipients":
            total_recipients,

        "verified_recipients":
            verified_recipients,


        # Recent data
        "recent_predictions":
            recent_predictions,

        "recent_surplus":
            recent_surplus,

        "recent_redistributions":
            recent_redistributions,


        # Chart data
        "chart_labels":
            chart_labels,

        "chart_values":
            chart_values,
    }


    # ----------------------------------------------
    # RENDER DASHBOARD
    # ----------------------------------------------

    return render(
        request,
        "dashboard.html",
        context
    )


# ==================================================
# DEMAND PREDICTION WITH REAL-TIME WEATHER
# ==================================================

def predict_demand(request):

    prediction = None
    recommended = None
    error = None
    weather_data = None

    if request.method == "POST":

        try:

            # --------------------------------------
            # USER INPUT
            # --------------------------------------

            attendance = int(
                request.POST.get(
                    "attendance",
                    0
                )
            )

            city = request.POST.get(
                "city",
                ""
            ).strip()

            holiday = int(
                request.POST.get(
                    "holiday",
                    0
                )
            )

            day_of_week = int(
                request.POST.get(
                    "day_of_week",
                    0
                )
            )

            # --------------------------------------
            # VALIDATION
            # --------------------------------------

            if attendance < 0:

                raise ValueError(
                    "Attendance cannot be negative."
                )

            if not city:

                raise ValueError(
                    "Please enter a city."
                )

            if holiday not in [0, 1]:

                raise ValueError(
                    "Invalid holiday value."
                )

            if day_of_week not in range(7):

                raise ValueError(
                    "Invalid day of week."
                )

            # --------------------------------------
            # GET REAL-TIME WEATHER
            # --------------------------------------

            weather_data = get_weather_data(city)

            if not weather_data:

                raise ValueError(
                    "Unable to get weather data."
                )

            temperature = float(
                weather_data["temperature"]
            )

            rainfall = float(
                weather_data["rainfall"]
            )

            # --------------------------------------
            # PREPARE ML INPUT
            # --------------------------------------

            input_data = [[
                attendance,
                temperature,
                rainfall,
                holiday,
                day_of_week
            ]]

            # --------------------------------------
            # MAKE ML PREDICTION
            # --------------------------------------

            prediction = model.predict(
                input_data
            )[0]

            prediction = max(
                0,
                round(prediction)
            )

            # --------------------------------------
            # RECOMMENDED PREPARATION
            # 5% EXTRA
            # --------------------------------------

            recommended = round(
                prediction * 1.05
            )

            # --------------------------------------
            # SAVE FORECAST
            # --------------------------------------

            DemandForecast.objects.create(

                date=date.today(),

                predicted_demand=prediction,

                recommended_preparation=recommended

            )

        # ------------------------------------------
        # TEMPORARY DEBUGGING
        # ------------------------------------------

        except Exception as e:

            error = (
                f"Prediction error: {str(e)}"
            )

    return render(

        request,

        "predict.html",

        {
            "prediction": prediction,

            "recommended": recommended,

            "error": error,

            "weather_data": weather_data,
        }

    )
# ==================================================
# FOOD SAFETY CHECK
# ==================================================

def check_food_safety(request):

    result = None
    error = None

    if request.method == "POST":

        try:

            storage_temperature = float(
                request.POST.get(
                    "storage_temperature",
                    4
                )
            )

            storage_time_hours = float(
                request.POST.get(
                    "storage_time_hours",
                    0
                )
            )


            # --------------------------------------
            # VALIDATION
            # --------------------------------------

            if storage_time_hours < 0:

                raise ValueError(
                    "Storage time cannot be negative."
                )


            # --------------------------------------
            # SAFETY RULE
            #
            # Temperature <= 5°C
            # Storage time <= 24 hours
            # --------------------------------------

            if (
                storage_temperature <= 5
                and storage_time_hours <= 24
            ):

                result = "SAFE"

            else:

                result = "UNSAFE"


        except (
            ValueError,
            TypeError
        ):

            error = (
                "Please enter valid storage values."
            )


    return render(
        request,
        "food_safety.html",
        {
            "result": result,
            "error": error,
        }
    )


# ==================================================
# ADD SURPLUS FOOD
# ==================================================

def add_surplus_food(request):

    if request.method == "POST":

        form = SurplusFoodForm(
            request.POST
        )

        if form.is_valid():

            food = form.save()

            # --------------------------------------
            # AUTOMATIC FOOD SAFETY CHECK
            # --------------------------------------

            food.check_safety()

            return redirect(
                "surplus_list"
            )

    else:

        form = SurplusFoodForm()


    return render(
        request,
        "add_surplus.html",
        {
            "form": form
        }
    )


# ==================================================
# SURPLUS FOOD LIST
# ==================================================

def surplus_list(request):

    foods = SurplusFood.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "surplus_list.html",
        {
            "surplus_foods": foods
        }
    )


# ==================================================
# REDISTRIBUTE SURPLUS FOOD
# ==================================================

def redistribute_food(
    request,
    food_id
):

    food = get_object_or_404(
        SurplusFood,
        id=food_id
    )


    # ----------------------------------------------
    # ONLY SAFE FOOD CAN BE REDISTRIBUTED
    # ----------------------------------------------

    if food.status != "SAFE":

        return redirect(
            "surplus_list"
        )


    # ----------------------------------------------
    # POST REQUEST
    # ----------------------------------------------

    if request.method == "POST":

        form = RedistributionForm(
            request.POST
        )

        if form.is_valid():

            redistribution = form.save(
                commit=False
            )


            # --------------------------------------
            # CHECK QUANTITY
            # --------------------------------------

            if redistribution.quantity > food.quantity:

                form.add_error(
                    "quantity",
                    "Redistribution quantity cannot "
                    "exceed available surplus quantity."
                )

            else:

                # ----------------------------------
                # CONNECT TO SURPLUS FOOD
                # ----------------------------------

                redistribution.surplus = food

                redistribution.save()


                # ----------------------------------
                # UPDATE FOOD QUANTITY
                # ----------------------------------

                food.quantity -= (
                    redistribution.quantity
                )


                # ----------------------------------
                # UPDATE STATUS
                # ----------------------------------

                if food.quantity == 0:

                    food.status = "REDISTRIBUTED"

                food.save()


                return redirect(
                    "surplus_list"
                )


    else:

        form = RedistributionForm()


    # ----------------------------------------------
    # DISPLAY SURPLUS LIST
    # ----------------------------------------------

    foods = SurplusFood.objects.all().order_by(
        "-created_at"
    )


    return render(
        request,
        "surplus_list.html",
        {
            "surplus_foods": foods,
            "redistribution_form": form,
            "selected_food": food
        }
    )


# ==================================================
# RECIPIENT MANAGEMENT
# ==================================================

def recipient_list(request):

    recipients = Recipient.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "recipient_list.html",
        {
            "recipients": recipients
        }
    )


# ==================================================
# ADD RECIPIENT
# ==================================================

def add_recipient(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        recipient_type = request.POST.get(
            "recipient_type",
            ""
        ).strip()

        capacity = request.POST.get(
            "capacity",
            ""
        )

        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not name:

            return render(
                request,
                "add_recipient.html",
                {
                    "error":
                        "Recipient name is required."
                }
            )

        if not recipient_type:

            return render(
                request,
                "add_recipient.html",
                {
                    "error":
                        "Recipient type is required."
                }
            )

        try:

            capacity = int(capacity)

        except (ValueError, TypeError):

            return render(
                request,
                "add_recipient.html",
                {
                    "error":
                        "Capacity must be a valid number."
                }
            )

        if capacity <= 0:

            return render(
                request,
                "add_recipient.html",
                {
                    "error":
                        "Capacity must be greater than 0."
                }
            )

        # ------------------------------------------
        # CREATE RECIPIENT
        # ------------------------------------------

        Recipient.objects.create(
            name=name,
            recipient_type=recipient_type,
            capacity=capacity,
            verified=False
        )

        return redirect(
            "recipient_list"
        )

    return render(
        request,
        "add_recipient.html"
    )


# ==================================================
# VERIFY RECIPIENT
# ==================================================

def verify_recipient(
    request,
    recipient_id
):

    recipient = get_object_or_404(
        Recipient,
        id=recipient_id
    )

    recipient.verified = True

    recipient.save()

    return redirect(
        "recipient_list"
    )

