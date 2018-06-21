"""Models of the `core` app."""
from typing import Union, Iterable

from django.db import models, transaction
from django.contrib.auth.models import User


class IssueStatus(models.Model):
    """Status of an issue."""

    title = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        """Meta attributes of `IssueCategory` model."""

        verbose_name_plural = 'issue statuses'

    def __str__(self):
        """Return str representation of the instance."""
        return "IssueStatus `{}`".format(self.title)


class IssueCategory(models.Model):
    """Category of an issue."""

    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        """Meta attributes of `IssueCategory` model."""

        verbose_name_plural = 'issue categories'

    def __str__(self):
        """Return str representation of the instance."""
        return "IssueCategory `{}`".format(self.title)


class IssueBase(models.Model):
    """Mixin with DB fields for `Issue` model.

    Used to have another model with the same fields as the `Issue`,
    without inheriting it's behavior.
    """

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
    solver = models.ForeignKey(User, models.SET_NULL, null=True, blank=True,
                               related_name='solved_issues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta attributes of `Issue` model."""

        abstract = True


class Issue(IssueBase):
    """Representation of the core object of the project - an issue."""

    def save(self,
             force_insert: (bool, "Force using SQL INSERT") = False,
             force_update: (bool, "Force using SQL UPDATE") = False,
             using: (str, "Alias of the DB to use") = None,
             update_fields: (Union[Iterable, None],
                             "Fields which valus to save to DB. `None`"
                             " will cause all fields to be saved, empty"
                             " iterable will abort saving.") = None):
        """Save the `Issue` and create an `IssueUpdate`."""
        if update_fields is not None and not update_fields:
            return
        with transaction.atomic():
            super().save(force_insert, force_update, using, update_fields)
            field_names = [field_name for field_name in
                           {f.name for f in self._meta.get_fields()} &
                           {f.name for f in IssueUpdate._meta.get_fields()}
                           if field_name != 'id']
            data_source = self if update_fields is None else \
                type(self).objects.get(pk=self.pk)
            IssueUpdate.objects.create(
                issue=self,
                **{f: getattr(data_source, f) for f in field_names})

    def __str__(self):
        """Return str representation of the instance."""
        return "Issue {}: `{}`".format(self.pk, self.title)


class IssueUpdate(IssueBase):
    """Representation of an issue state after each modification.

    Not currently read anywhere, but it's almost guaranteed that the
    full history will be needed in the future.
    """

    issue = models.ForeignKey(Issue, models.CASCADE,
                              related_name='issue_updates')
    # Override to change `related_name`s in order to avoid clash with
    # reverse accessors to `Issue`.
    submitter = models.ForeignKey(User, models.SET_NULL, null=True,
                                  related_name='submitted_issue_updates')
    solver = models.ForeignKey(User, models.SET_NULL, null=True,
                               related_name='solved_issue_updates')
    # Override to remove `auto_now` and `auto_now_add` arguments.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        """Meta attributes of `IssueUpdate` model."""

        get_latest_by = ['updated_at', 'pk']

    def __str__(self):
        """Return str representation of the instance."""
        return "IssueUpdate {} of `{}` on {}".format(
            self.pk, self.issue, self.updated_at)
