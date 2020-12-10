from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('home.urls', 'home'), namespace = 'home')),
    path('task-progress', include('celery_progress.urls')),
    path('facebook/', include(('facebook.urls', 'facebook'), namespace = 'fb')),
    path('dashboard/', include(('dashboard.urls','dashboard'),namespace='dash')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('resetpassword/',auth_views.PasswordResetView.as_view(template_name='home/reset.html'), name='reset_password'),
    path('resetpasswordsent/',auth_views.PasswordResetDoneView.as_view(template_name='home/resetsent.html'), name='password_reset_done'),
    path('resetpassword/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='home/resetconf.html'), name='password_reset_confirm'),
    path('resetpasswordcompete/',auth_views.PasswordResetCompleteView.as_view(template_name='home/resetcomplete.html'), name='password_reset_complete'),
    path('celery-progress/', include('celery_progress.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
