from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Issue, Label
from .pagination import IssuePagination

from .serializers import (
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    LabelSerializer,
    IssueUpdateSerializer,
)


class IssueListCreateView(generics.ListCreateAPIView):
    serializer_class = IssueSerializer
    pagination_class = IssuePagination

    def get_queryset(self):
        queryset = Issue.objects.all().order_by('-created_at')

        status_param = self.request.query_params.get("status")
        assignee_param = self.request.query_params.get("assignee")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if assignee_param:
            queryset = queryset.filter(assignee=assignee_param)

        return queryset


class IssueRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Issue.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return IssueUpdateSerializer
        return IssueDetailSerializer

    @transaction.atomic
    def patch(self, request, id):
        issue = get_object_or_404(Issue, id=id)

        serializer = self.get_serializer(
            issue,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        incoming_version = serializer.validated_data.get("version")
        
        if incoming_version is None:
           return Response(
                {"version": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
           
        if incoming_version != issue.version:
            return Response(
                {
                    "detail": "Version conflict. Issue has been modified by another request.",
                    "current_version": issue.version,
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer.validated_data.pop("version")

        for attr, value in serializer.validated_data.items():
            setattr(issue, attr, value)

        issue.version += 1
        issue.save()

        return Response(
            IssueSerializer(issue).data,
            status=status.HTTP_200_OK,
        )


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



