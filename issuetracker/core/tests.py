"""Tests for `core` app.

Many tests are not implemented to save time, those implemented and the
names of those not implemented are enough for demonstration.
"""
import unittest

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
            status=IssueStatus.objects.create(title="New", is_solved=False),
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
        self.issue.status = IssueStatus.objects.create(title="Assigned",
                                                       is_solved=False)
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
        self.issue.status = IssueStatus.objects.create(title="Assigned",
                                                       is_solved=False)
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


@unittest.skip("Implement")
class IssueAdminTestCase(TestCase):
    """Tests for admin view.

    While usually the admin part isn't being covered by tests, in this
    case it is presented to our users.
    """

    # Should use something like django-webtest to check the generated
    # HTML.

    def test_deletion_is_disabled(self):
        """Test no `delete selected` and deletion view is disabled."""
        self.fail()

    def test_stat_shortest_time_to_solve(self):
        """Test the correct shortest time is present on the page.

        The time should be next to `Shortest time` title (after
        stripping tags).
        """
        self.fail()

    def test_stat_longest_time_to_solve(self):
        """Test the correct longest time is present on the page.

        The time should be next to `Longest time` title (after stripping
        tags).
        """
        self.fail()

    def test_stat_average_time_to_solve(self):
        """Test the correct average time is present on the page.

        The time should be next to `Average time` title (after stripping
        tags).
        """
        self.fail()

    def test_site_header(self):
        """Test the site header is customized."""
        self.fail()

    def test_index_title(self):
        """Test index title is customized."""
        self.fail()

    def test_site_url(self):
        """Test `site_url` is empty.

        Admin should not have a link to itself `site_url` normally is.
        """
        self.fail()


@unittest.skip("Implement")
class Migration0004TestCase(TestCase):
    """Tests for `core` 0004 migration that fills `Issue.solved_at`."""

    # The test can be done on the migration, like discribed in
    # https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    # Direct testing of the function
    # `core.migrations.0004_fill_issue_solved_at.fill_issue_solved_at`
    # may have to be removed in the future because of incompatible
    # changes in models `Issue` and `IssueHistory`. That may be
    # acceptable though - if we control all installations of the
    # project, and will apply that migration while this test case is
    # still operational, after which we can squash that migration away
    # and remove this test case.

    def test_issue_that_was_solved_with_its_latest_update(self):
        """Test `solved_at` of Issue that just got a solved status."""
        self.fail()

    def test_issue_that_was_solved_with_not_its_latest_update(self):
        """Test issue that was solved before last update."""
        self.fail()

    def test_issue_that_was_solved_and_reopened(self):
        """Test issue that was solved and reopened is still open.

        It is OK for such issue to have `solved_at` set as long as its
        status is not affected.
        """
        self.fail()

    def test_issueupdate_created_with_new_solved_at(self):
        """Test IssueUpdate is created for the issue change as normal.

        It may not be created, because the custom `save` method, it is
        normally created in, is not available in migrations.
        """
        self.fail()
