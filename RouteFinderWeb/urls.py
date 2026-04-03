from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path('results/', views.ResultsView.as_view(), name='results'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='RouteFinderWeb/password_change.html', success_url='/profile/'), name='password_change'),
    path('discover/', views.SaleDiscoveryView.as_view(), name='discover'),
    path('toggle-rating/', views.ToggleRatingView.as_view(), name='toggle_rating'),
]
