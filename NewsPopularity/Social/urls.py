from django.conf.urls import url, include

# from django.contrib import admin
from Social import views

urlpatterns = [
    url(r'^$', view=views.index, name='index'),
]
