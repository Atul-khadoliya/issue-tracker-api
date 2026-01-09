from rest_framework import generics
from django.shortcuts import get_object_or_404
from .models import Issue, Comment
from .serializers import (
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
)


class IssueListCreateView(generics.ListCreateAPIView):
    queryset = Issue.objects.all().order_by('-created_at')
    serializer_class = IssueSerializer


class IssueDetailView(generics.RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueDetailSerializer
    lookup_field = 'id'


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, id=self.kwargs['id'])
        serializer.save(issue=issue)

