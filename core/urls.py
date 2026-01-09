from django.urls import path
from .views import IssueListCreateView, IssueDetailView

urlpatterns = [
    path('issues', IssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:id>', IssueDetailView.as_view(), name='issue-detail'),
]
