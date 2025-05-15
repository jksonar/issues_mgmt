from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Issue, Comment, Notification
from .forms import IssueForm, CommentForm, NotificationForm, IssueFilterForm

@login_required
def issue_list(request):
    filter_form = IssueFilterForm(request.GET)
    issues = Issue.objects.all()

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        assigned_to = filter_form.cleaned_data.get('assigned_to')
        search = filter_form.cleaned_data.get('search')

        if status:
            issues = issues.filter(status=status)
        if priority:
            issues = issues.filter(priority=priority)
        if assigned_to:
            issues = issues.filter(assigned_to=assigned_to)
        if search:
            issues = issues.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )

    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(issues, 10)  # Show 10 issues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form
    }
    return render(request, 'issues/issue_list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('issue_detail', pk=notification.issue.id)

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'issues/notifications_list.html', {'notifications': notifications})

@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    comment_form = CommentForm()
    return render(request, 'issues/issue_detail.html', {
        'issue': issue,
        'comment_form': comment_form
    })

@login_required
def issue_create(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()
            messages.success(request, 'Issue created successfully!')
            return redirect('issue_detail', pk=issue.pk)
    else:
        form = IssueForm()
    return render(request, 'issues/issue_form.html', {'form': form, 'action': 'Create'})

@login_required
def issue_edit(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if not (request.user.is_admin_user() or request.user == issue.created_by):
        messages.error(request, 'You do not have permission to edit this issue.')
        return redirect('issue_detail', pk=pk)

    if request.method == 'POST':
        form = IssueForm(request.POST, instance=issue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Issue updated successfully!')
            return redirect('issue_detail', pk=pk)
    else:
        form = IssueForm(instance=issue)
    return render(request, 'issues/issue_form.html', {'form': form, 'action': 'Edit'})

@login_required
def issue_delete(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if not request.user.is_admin_user():
        messages.error(request, 'Only admin users can delete issues.')
        return redirect('issue_detail', pk=pk)

    if request.method == 'POST':
        issue.delete()
        messages.success(request, 'Issue deleted successfully!')
        return redirect('issue_list')
    return render(request, 'issues/issue_confirm_delete.html', {'issue': issue})


@login_required
def add_comment(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.author = request.user
            comment.save()
            return redirect('issue_detail', pk=pk)
    return redirect('issue_detail', pk=pk)
