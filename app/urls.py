# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('configuration/', views.configuration, name='configuration'),
    path('insights/', views.insights, name='insights'),
    path('workforce_data/', views.WorkforceDataView.as_view(), name='workforce_data'),
    path('workforce_activity/', views.WorkforceActivityView.as_view(), name='workforce_activity'),
    path('workforce_idle/', views.WorkforceIdleDataView.as_view(), name='workforce_idle'),
    path('group_talking/', views.GroupTalkingView.as_view(), name='group_talking'),
    path('pies/', views.PieChartDataView.as_view(), name='pie_chart'),
    path('pier_progress/', views.get_data_pier_progress, name='pier_progress'),
    # path('caging/', views.caging, name='caging'),
    path('all/', views.get_data, name='get_data'), 
    path('pie/', views.get_data_pie, name='pie_chart'),

     path('get-pier-progress-data/', views.get_pier_progress_data, name='get_pier_progress_data'),
    path("caging/", views.caging_view, name="caging"),


    path('time_series/', views.get_data_time_series, name='time_series'),
     path('workforce/idle-data/', views.Workforce_IdleDataView.as_view(), name='idle-data-with-date'),
    path('workforce/idle-data/all/', views.WorkforceIdleDataWithoutDateView.as_view(), name='idle-data-without-date'),

]
