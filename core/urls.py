from django.urls import path
from .views import IssueCreateView

urlpatterns = [
    path('issues', IssueCreateView.as_view(), name='issue-create'),
]
