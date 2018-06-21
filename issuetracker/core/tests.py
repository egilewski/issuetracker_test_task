"""Tests for `core` app."""
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Issue, IssueStatus, IssueCategory


class IssueTestMixin():
    """Base class for test classes for `Issue` and realted models."""

    def setUp(self):
        """Set up environment for testing `Issue`."""
        self.issue = Issue.objects.create(
            title="Test issue title",
            description="Test issue description",
            status=IssueStatus.objects.create(title="New"),
            category=IssueCategory.objects.create(title="Other"),
            submitter=User.objects.create(username='submitter0',
                                          email='submitter0@example.com'),
            solver=User.objects.create(username='solver0',
                                       email='solver0@example.com'))


class IssueTestCase(IssueTestMixin, TestCase):
    """Tests for `Issue` model."""

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


class IssueUpdateTestCase(IssueTestMixin, TestCase):
    """Tests for `IssueUpdate` model.

    These tests still mostly concern the logic of `Issue.save`, but the
    one that affects `IssueUpdate`s creation and doesn't affect usage of
    `Issue`s by their clients.
    """

    def assert_issue_and_issuehistory_equal(self, issue_or_issue_history0,
                                            issue_or_issue_history1):
        """Assert that an Issue and an IssueHistory are equal."""
        for field_name in ('title', 'description', 'status', 'category',
                           'submitter', 'solver', 'created_at',
                           'updated_at'):
            self.assertEqual(
                getattr(issue_or_issue_history0, field_name),
                getattr(issue_or_issue_history1, field_name),
                "{} differs: {} != {}".format(
                    field_name, getattr(issue_or_issue_history0, field_name),
                    getattr(issue_or_issue_history1, field_name)))

    def test_issueupdate_created_when_issue_created(self):
        """Test new `IssueUpdate` is created when `Issue` is crated."""
        issue_update = self.issue.issue_updates.get()
        self.assert_issue_and_issuehistory_equal(self.issue, issue_update)

    def test_issueupdate_created_when_issue_updated(self):
        """Test new `IssueUpdate` is created when `Issue` is updated."""
        self.issue.title = "Test another issue title"
        self.issue.description = "Test another issue description"
        self.issue.status = IssueStatus.objects.create(title="Assigned")
        self.issue.category = IssueCategory.objects.create(title="Bug")
        self.issue.submitter = User.objects.create(
            username='submitter1', email='submitter1@example.com')
        self.issue.solver = User.objects.create(
            username='solver1', email='solver1@example.com')
        self.issue.save()

        issue_update = self.issue.issue_updates.latest()
        self.assert_issue_and_issuehistory_equal(self.issue, issue_update)

    def test_issueupdate_created_on_save_with_update_fields(self):
        """Test new IssueUpdate when Issue saved with update_fields."""
        self.issue.title = "Test another issue title"
        self.issue.description = "Test another issue description"
        self.issue.status = IssueStatus.objects.create(title="Assigned")
        self.issue.save(update_fields=['title', 'description'])

        issue_update = self.issue.issue_updates.latest()
        with self.assertRaises(AssertionError):
            # Not all updated values of `self.issue` fields were saved
            # to DB (as update for the `safe.issue` and as a new
            # `IssueUpdate`.
            self.assert_issue_and_issuehistory_equal(self.issue, issue_update)
        self.issue.refresh_from_db()
        self.assert_issue_and_issuehistory_equal(self.issue, issue_update)

    def test_issueupdate_not_created_on_save_with_empty_update_fields(self):
        """Test no IssueUpdate on Issue.save(update_fields=[])."""
        old_issue_updates_count = self.issue.issue_updates.count()
        self.issue.title = "Test another issue title"
        self.issue.save(update_fields=[])
        self.assertEqual(self.issue.issue_updates.count(),
                         old_issue_updates_count)
