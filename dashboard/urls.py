from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboardView, name='dashboard'),
    path('favorate/<str:pk>', views.addGroupToFavorate, name='favorate'),
    path('unfavorate/<str:pk>', views.removeGroupfromFavorate, name='unfavorate'),

]
