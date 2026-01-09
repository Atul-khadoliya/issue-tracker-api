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
            'issue',
            'author',
            'body',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            'id',
            'name',
        ]
        read_only_fields = ['id']
        
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
