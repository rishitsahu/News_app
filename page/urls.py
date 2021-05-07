from django.urls import path
from . import views
urlpatterns = [
    path('',views.search,name="Search"),
    path('drive',views.save,name="Save"),
    path('upload',views.upload,name="Upload"),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about')
]