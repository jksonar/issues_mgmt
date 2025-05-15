from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Issue
from .forms import IssueForm
from django.core.paginator import Paginator

@login_required
def issue_list(request):
    issues = Issue.objects.all().order_by('-created_at')
    paginator = Paginator(issues, 10)  # Show 10 issues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'issues/issue_list.html', {'page_obj': page_obj})

@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    return render(request, 'issues/issue_detail.html', {'issue': issue})

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
