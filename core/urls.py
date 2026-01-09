from django.urls import path
from .views import (
    IssueListCreateView,
    IssueRetrieveUpdateView,
    CommentCreateView,
    IssueLabelReplaceView,
    BulkIssueStatusUpdateView,
    IssueCSVImportView,
    TopAssigneesReportView,
)

urlpatterns = [
    path('issues', IssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:id>', IssueRetrieveUpdateView.as_view(), name='issue-detail-update'),
    path('issues/<int:id>/comments', CommentCreateView.as_view(), name='issue-comment-create'),
    path('issues/<int:id>/labels', IssueLabelReplaceView.as_view(), name='issue-label-replace'),
    path('issues/bulk-status', BulkIssueStatusUpdateView.as_view(), name='issue-bulk-status'),
    path('issues/import', IssueCSVImportView.as_view(), name='issue-csv-import'),
    path('reports/top-assignees', TopAssigneesReportView.as_view(), name='report-top-assignees'),

]
