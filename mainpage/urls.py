from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('contest', views.contest, name='contest'),
    path('ranking', views.ranking, name='ranking'),
]
