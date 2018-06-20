"""Models of the `core` app."""
from django.db import models
from django.contrib.auth.models import User


class IssueStatus(models.Model):
    """Status of an issue."""

    title = models.CharField(max_length=30)
    description = models.TextField(blank=True)


class IssueCategory(models.Model):
    """Category of an issue."""

    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)


class Issue(models.Model):
    """Representation of the core object of the project - an issue."""

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.ForeignKey(IssueStatus, models.SET_NULL, null=True)
    category = models.ForeignKey(IssueCategory, models.SET_NULL, null=True)
    # Actually `models.SET_NULL` or `models.CASCADE` depends on who has
    # intellectual rights to issues - the tracker or their submitters
    # (or if submitters allowed issues to stay). Using `models.SET_NULL`
    # allows to delete the user's issues before it's account is deleted.
    submitter = models.ForeignKey(User, models.SET_NULL, null=True,
                                  related_name='submitted_issues')
    solver = models.ForeignKey(User, models.SET_NULL, null=True,
                               related_name='solved_issues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
