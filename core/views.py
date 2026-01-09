from rest_framework import generics
from .models import Issue
from .serializers import IssueSerializer, IssueDetailSerializer


class IssueListCreateView(generics.ListCreateAPIView):
    queryset = Issue.objects.all().order_by('-created_at')
    serializer_class = IssueSerializer


class IssueDetailView(generics.RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueDetailSerializer
    lookup_field = 'id'
