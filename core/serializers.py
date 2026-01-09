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
