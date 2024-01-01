from django.urls import path

from .views import (
    CardListAPIView,
    CardControlListAPIView,
    CardControlDetailAPIView,
    TransactionListAPIView,
)


urlpatterns = [
    path("cards/", CardListAPIView.as_view(), name="cards"),
    path(
        "card-controls/<uuid:card_control_id>",
        CardControlDetailAPIView.as_view(),
        name="card-control-detail",
    ),
    path("card-controls/", CardControlListAPIView.as_view(), name="card-controls"),
    path("transactions/", TransactionListAPIView.as_view(), name="transactions"),
]
