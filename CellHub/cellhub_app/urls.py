from django.urls import path
from .views import IndexView 

urlpatterns = [
			   path('Holamundo/', IndexView, name="IndexView")
]
