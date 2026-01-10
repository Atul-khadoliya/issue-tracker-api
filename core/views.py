from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Issue, Label
from .pagination import IssuePagination
import csv
import io
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils.timezone import is_aware

from .serializers import (
    IssueSerializer,
    IssueDetailSerializer,
    CommentSerializer,
    LabelSerializer,
    IssueUpdateSerializer,
    IssueCSVRowSerializer,
)


# GET /issues (list with filtering & pagination) + POST /issues (create issue)
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


# GET /issues/{id} (retrieve) + PATCH /issues/{id} (update with optimistic concurrency)
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


# POST /issues/{id}/comments — add a comment to an issue
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, id=self.kwargs['id'])
        serializer.save(issue=issue)


# PUT /issues/{id}/labels — replace issue labels atomically
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


# PUT /issues/bulk-status — transactional bulk status update
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


# POST /issues/import — CSV import with per-row validation and partial success
class IssueCSVImportView(generics.GenericAPIView):
    serializer_class = IssueCSVRowSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"detail": "CSV file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not file.name.endswith(".csv"):
            return Response(
                {"detail": "Only CSV files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decoded_file = file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        required_fields = {"title", "description", "status", "assignee"}
        if not required_fields.issubset(reader.fieldnames):
            return Response(
                {
                    "detail": "CSV must contain headers: title, description, status, assignee"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_rows = 0
        created = 0
        failed = 0
        errors = []

        for index, row in enumerate(reader, start=1):
            total_rows += 1

            serializer = IssueCSVRowSerializer(data=row)
            if serializer.is_valid():
                Issue.objects.create(**serializer.validated_data)
                created += 1
            else:
                failed += 1
                errors.append(
                    {
                        "row": index,
                        "errors": serializer.errors,
                    }
                )

        return Response(
            {
                "total_rows": total_rows,
                "created": created,
                "failed": failed,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )


# GET /reports/top-assignees — aggregate issues by assignee
class TopAssigneesReportView(generics.GenericAPIView):
    queryset = Issue.objects.none()

    def get(self, request):
        data = (
            Issue.objects
            .exclude(assignee__isnull=True)
            .values("assignee")
            .annotate(issue_count=Count("id"))
            .order_by("-issue_count")
        )

        return Response(list(data), status=status.HTTP_200_OK)


# GET /reports/latency — average resolution time for resolved/closed issues
class IssueLatencyReportView(generics.GenericAPIView):
    queryset = Issue.objects.none()

    def get(self, request):
        resolved_issues = Issue.objects.filter(
            status__in=["resolved", "closed"]
        )

        latency_expression = ExpressionWrapper(
            F("updated_at") - F("created_at"),
            output_field=DurationField()
        )

        result = resolved_issues.aggregate(
            average_latency=Avg(latency_expression)
        )

        return Response(
            {
                "average_resolution_time": result["average_latency"]
            },
            status=status.HTTP_200_OK,
        )


# GET /issues/{id}/timeline — derived timeline of issue history (bonus)
class IssueTimelineView(generics.GenericAPIView):
    queryset = Issue.objects.all()
    lookup_field = 'id'

    def get(self, request, id):
        issue = get_object_or_404(Issue, id=id)

        events = []

        events.append({
            "type": "created",
            "timestamp": issue.created_at,
            "details": {
                "title": issue.title,
                "status": issue.status,
            }
        })

        if issue.updated_at and issue.updated_at != issue.created_at:
            events.append({
                "type": "status_change",
                "timestamp": issue.updated_at,
                "details": {
                    "status": issue.status,
                }
            })

        for comment in issue.comments.all():
            events.append({
                "type": "comment",
                "timestamp": comment.created_at,
                "details": {
                    "author": comment.author.username if comment.author else None,
                    "body": comment.body,
                }
            })

        labels = list(issue.labels.values_list("name", flat=True))
        if labels:
            events.append({
                "type": "label_update",
                "timestamp": issue.updated_at,
                "details": {
                    "labels": labels,
                }
            })

        events.sort(key=lambda e: e["timestamp"])

        return Response(events, status=status.HTTP_200_OK)
