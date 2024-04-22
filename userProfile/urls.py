from django.urls import path
from . import views

app_name = 'userProfile'

urlpatterns=[
    path('',views.home,name="home"),
    path('register/',views.register,name="register"),
    path("aboutUs/",views.aboutUs,name="aboutUs"),
    path("profile_view/",views.profile_view,name="profile_view"),
    path("profile_update/",views.profile_update,name="profile_update"),
    
    ]