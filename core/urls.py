from django.urls import path
from .views import (
    IssueListCreateView,
    IssueDetailView,
    CommentCreateView,
    IssueLabelReplaceView,
)

urlpatterns = [
    path('issues', IssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:id>', IssueDetailView.as_view(), name='issue-detail'),
    path('issues/<int:id>/comments', CommentCreateView.as_view(), name='issue-comment-create'),
    path('issues/<int:id>/labels', IssueLabelReplaceView.as_view(), name='issue-label-replace'),
]
