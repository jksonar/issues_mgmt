from django import forms
from django.contrib.auth import get_user_model
from .models import Issue, Comment, Notification

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'category', 'status', 'priority', 'assigned_to']

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['content']
#         widgets = {
#             'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
#         }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Type your comment here. Use @username to mention users.'
            })
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['is_read']

class IssueFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All')] + Issue.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All')] + Issue.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assigned_to = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        empty_label='All',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search issues...'
        })
    )