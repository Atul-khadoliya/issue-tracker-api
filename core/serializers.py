from rest_framework import serializers
from .models import Issue,Comment,Label


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'description',
            'status',
            'assignee',
            'version',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'body',
            'author',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment body cannot be empty.")
        return value

        
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            'id',
            'name',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'name': {'validators': []},  
        }
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Label name cannot be empty.")
        return value.strip()

        

class IssueDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'description',
            'status',
            'assignee',
            'version',
            'created_at',
            'updated_at',
            'comments',
            'labels',
        ]
        read_only_fields = fields

class IssueUpdateSerializer(serializers.ModelSerializer):
    version = serializers.IntegerField(required=True)

    class Meta:
        model = Issue
        fields = [
            'title',
            'description',
            'status',
            'assignee',
            'version',
        ]
        
        

class IssueCSVRowSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=Issue.STATUS_CHOICES,
        required=True
    )
    assignee = serializers.IntegerField(required=False, allow_null=True)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value
