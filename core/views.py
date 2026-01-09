from rest_framework import generics
from .models import Issue
from .serializers import IssueSerializer


class IssueListCreateView(generics.ListCreateAPIView):
    queryset = Issue.objects.all().order_by('-created_at')
    serializer_class = IssueSerializer

