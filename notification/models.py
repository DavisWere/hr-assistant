from django.db import models
from django.utils import timezone
from users.models import User


class ChatMessage(models.Model):
    MESSAGE_SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="The user who sent or received this message"
    )
    sender_type = models.CharField(
        max_length=30,
        choices=MESSAGE_SENDER_CHOICES,
        help_text="Indicates if the sender was 'user' or 'assistant'"
    )
    message_text = models.TextField(help_text="The content of the message")
    timestamp = models.DateTimeField(default=timezone.now, help_text="Timestamp when the message was sent")

    def __str__(self):
        return f"{self.sender_type} @ {self.timestamp}: {self.message_text[:30]}"

class MessageFeedback(models.Model):
    FEEDBACK_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    ]

    message = models.ForeignKey(
        ChatMessage, 
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text="The ID of the assistant message being rated"
    )
    user = models.ForeignKey(
        User ,
        on_delete=models.CASCADE,
        to_field='id', 
        related_name='feedback_given',
        help_text="The user who provided the feedback"
    )
    feedback_type = models.CharField(
        max_length=8,
        choices=FEEDBACK_CHOICES,
        help_text="Type of feedback: 'positive' or 'negative'"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the feedback was provided"
    )

    def __str__(self):
        return f"{self.feedback_type.capitalize()} by {self.user} on {self.message}"
    

    class KnowledgeBaseArticle(models.Model):
       User,
       title = models.CharField(
        max_length=255,
        unique=True,
        help_text="Title of the article (e.g., 'Company Policies')"
    )
    content = models.TextField(
        help_text="The detailed content of the article"
    )
    category = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Category of the article (e.g., 'Policies', 'Well-being')"
    )
    keywords = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated keywords for search/matching"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the article was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp for the article"
    )

    def __str__(self):
        return self.title

class EscalationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        to_field='id',
        related_name='escalation_requests',
        help_text="The user who initiated the request"
    )
    issue_description = models.TextField(
        help_text="A brief description of the issue, often the last user message"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the request"
    )
    requested_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the request was made"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request was resolved"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        to_field='id',
        null=True,
        blank=True,
        related_name='resolved_escalations',
        help_text="The HR user who resolved the request"
    )

    def __str__(self):
        return f"{self.user} - {self.status} - {self.request_id}"
