from docpi_app.api.views import (
    get_dataframe,
    upload_file, filter_dataframe, sort_dataframe, sortAndFilter, Signup, Signin, GetTableName
                                     )
from django.urls import path

urlpatterns = [
    path('df/<str:filename>/', get_dataframe.as_view(), name='get_dataframe'),
    path('file/<int:user>/', upload_file.as_view(), name='upload_file'),
    path('sort/<str:column>/<str:order>/<str:filename>/', sort_dataframe.as_view(), name='sort_dataframe'),
    path('filter/<str:column>/<str:value>/<str:filename>/', filter_dataframe.as_view(), name='filter_dataframe'),
    path('sortAndFilter/', sortAndFilter.as_view(), name='sortAndFilter_dataframe'),
    path('signup/', Signup.as_view(), name='sortAndFilter_dataframe'),
    path('signin/', Signin.as_view(), name='sortAndFilter_dataframe'),
    path('table/', GetTableName.as_view(), name='sortAndFilter_dataframe'),
]
