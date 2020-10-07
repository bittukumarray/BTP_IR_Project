from django.urls import path, include
from .views import *


urlpatterns = [
    path('get-docs/', get_ranked_docs.as_view()),
    path('create-index/', createIndex.as_view()),
    path('get-suggested-data/', getSuggestData.as_view()),

]