from rest_framework import generics
from .models import Issue
from .serializers import IssueSerializer

class IssueCreateView(generics.CreateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer