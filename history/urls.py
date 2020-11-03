from django.urls import path
from . import views

app_name = 'history'
urlpatterns = [
    path('history', views.HistoryListView.as_view(), name = 'history-list'),
    path('history/self', views.UserHistoryList.as_view(), name = 'user-history-list'),
    path('history/recover/<int:pk>', views.Recovery, name = 'recover-confirm'),
    path('history/recover/<int:pk>/<attr>', views.Recovery_by_attribute, name = 'recover_by_attr-confirm'),
]