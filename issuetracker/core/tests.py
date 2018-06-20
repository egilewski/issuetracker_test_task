"""Tests for `core` app."""
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Issue, IssueStatus, IssueCategory


class IssueTestCase(TestCase):
    """Tests for `Issue` model."""

    def setUp(self):
        """Set up environment for testing `Issue`."""
        self.issue = Issue.objects.create(
            title="Test issue title",
            description="Test issue description",
            status=IssueStatus.objects.create(title="New"),
            category=IssueCategory.objects.create(title="Other"),
            submitter=User.objects.create(username='submitter',
                                          email='submitter@example.com'),
            solver=User.objects.create(username='solver',
                                       email='solver@example.com'))

    def test_issue_not_removed_when_issuestatus_is_removed(self):
        """Test `Issue` not removed when `IssueSatus` assigned to it is."""
        self.issue.status.delete()
        self.assertTrue(Issue.objects.filter(pk=self.issue.pk).exists())

    def test_issue_not_removed_when_issuecategory_is_removed(self):
        """Test Issue not removed when IssueCategory assigned to it is."""
        self.issue.category.delete()
        self.assertTrue(Issue.objects.filter(pk=self.issue.pk).exists())

    def test_issue_not_removed_when_submitter_user_is_removed(self):
        """Test `Issue` not removed when `User` that submitted it is."""
        self.issue.submitter.delete()
        self.assertTrue(Issue.objects.filter(pk=self.issue.pk).exists())

    def test_issue_not_removed_when_solver_user_is_removed(self):
        """Test `Issue` not removed when `User` that solved it is."""
        self.issue.solver.delete()
        self.assertTrue(Issue.objects.filter(pk=self.issue.pk).exists())
