from django.db import models
from django.conf import settings
import re

class Issue(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_issues')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentioned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentioned_in_comments', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.issue.title}'

    def save(self, *args, **kwargs):
        # First save the comment
        super().save(*args, **kwargs)
        
        # Process mentions
        mentions = re.findall(r'@(\w+)', self.content)
        User = settings.AUTH_USER_MODEL
        
        # Clear existing mentions
        self.mentioned_users.clear()
        
        # Add new mentions and create notifications
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                if user != self.author:  # Don't notify the comment author
                    self.mentioned_users.add(user)
                    Notification.objects.create(
                        user=user,
                        comment=self,
                        issue=self.issue,
                        notification_type='MENTION',
                        message=f'{self.author.username} mentioned you in a comment'
                    )
            except User.DoesNotExist:
                continue

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('MENTION', 'Mention in Comment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
