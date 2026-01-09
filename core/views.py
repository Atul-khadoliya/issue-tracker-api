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


class BulkIssueStatusUpdateView(generics.GenericAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    @transaction.atomic
    def put(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Expected a list of issue updates."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_issues = []

        for item in request.data:
            issue_id = item.get("id")
            new_status = item.get("status")

            if not issue_id or not new_status:
                return Response(
                    {"detail": "Each item must contain id and status."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            issue = get_object_or_404(Issue, id=issue_id)

            if new_status not in dict(Issue.STATUS_CHOICES):
                return Response(
                    {"detail": f"Invalid status '{new_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            issue.status = new_status
            issue.version += 1
            issue.save()

            updated_issues.append(issue)

        return Response(
            IssueSerializer(updated_issues, many=True).data,
            status=status.HTTP_200_OK,
        )
