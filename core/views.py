from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Issue, Label
from .serializers import (
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    LabelSerializer,
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


class IssueLabelReplaceView(generics.GenericAPIView):
    queryset = Issue.objects.all()   
    serializer_class = LabelSerializer

    @transaction.atomic
    def put(self, request, id):
        issue = get_object_or_404(Issue, id=id)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        labels = []
        for label_data in serializer.validated_data:
            label, _ = Label.objects.get_or_create(
                name=label_data["name"]
            )
            labels.append(label)

        issue.labels.set(labels)

        return Response(
            LabelSerializer(labels, many=True).data,
            status=status.HTTP_200_OK,
        )
