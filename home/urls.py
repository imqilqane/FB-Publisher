from django.urls import path
from . import views


urlpatterns = [
    path('', views.homeView, name='home'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('register/', views.registerView, name='register'),
    path('subscribe/', views.subscriptionView, name='subscription'),  
    path('add-coupon-code/', views.couponView, name='coupon'),  
    path('process_subscription/', views.process_subscription, name='process_subscription'),  
    path('payment_done/', views.payment_done, name='done'),
    path('you_canceled_payment/', views.you_canceled_payment, name='canceled'),
    path('activate/<str:uidb64>/<str:token>/', views.vereficationView, name='activate'),
    path('edit-settings/', views.editSettingsView, name='edit_settings'),
    path('profile/', views.prfileView, name='profile'),


]
