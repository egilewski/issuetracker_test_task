"""Models of the `core` app."""
from typing import Union, Iterable

from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User

from .middleware import get_current_user


class IssueStatus(models.Model):
    """Status of an issue."""

    title = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    is_solved = models.BooleanField()

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
    solved_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Automatically set to the current time when `status`"
        " is changed to a solved one, unless it is changed manually.")

    class Meta:
        """Meta attributes of `Issue` model."""

        abstract = True


class Issue(IssueBase):
    """Representation of the core object of the project - an issue."""

    @classmethod
    def from_db(cls, db, field_names, values):
        """Load field values from DB.

        Save values of the field `status.is_solved` to attribute
        `_initial_status_is_solved` and `solved_at` to attribute
        `_initial_solved_at` for later use in `save`.
        """
        instance = super().from_db(db, field_names, values)
        instance._initial_status_is_solved = instance.status.is_solved \
            if instance.status else False
        instance._initial_solved_at = instance.solved_at
        return instance

    def __init__(self, *args, **kwargs):
        """Initialize the instance."""
        super().__init__(*args, **kwargs)
        self._initial_status_is_solved = False
        self._initial_solved_at = None

    def save(self,
             force_insert: (bool, "Force using SQL INSERT") = False,
             force_update: (bool, "Force using SQL UPDATE") = False,
             using: (str, "Alias of the DB to use") = None,
             update_fields: (Union[Iterable, None],
                             "Fields which valus to save to DB. `None`"
                             " will cause all fields to be saved, empty"
                             " iterable will abort saving.") = None):
        """Save the instance to DB.

        If the issue is created, `submitter` will be set to the current
        user. If the issue becomes solved, `solver` will be set to the
        current user, and `solved_at` to the current time. Warning: if
        you have passed an iterable for argument `update_fields` that
        does not include fields named above, they will be set on the
        object, but not saved to the DB.

        Side effect: create `IssueUpdate`.
        """
        if update_fields is not None and not update_fields:
            return
        if not self.pk:
            self.submitter = get_current_user()
        self._set_solver_and_solved_at_if_became_solved(update_fields)

        field_names = [field_name for field_name in
                       {f.name for f in self._meta.get_fields()} &
                       {f.name for f in IssueUpdate._meta.get_fields()}
                       if field_name != 'id']

        with transaction.atomic():
            super().save(force_insert, force_update, using, update_fields)

            if update_fields is None:
                fields2values = {f: getattr(self, f) for f in field_names}
            else:
                original_self = type(self).objects.get(pk=self.pk)
                fields2values = {
                    f: getattr(self if f in update_fields else original_self,
                               f)
                    for f in field_names}

            IssueUpdate.objects.create(issue=self, **fields2values)

    def _set_solver_and_solved_at_if_became_solved(self, update_fields):
        """Set `self.solved_at` and `self.solver` if appropriate.

        Set `self.solved_at` to the current time if became solved and
        wasn't changed manually (in comparison to the value the instance
        was loaded with).
        """
        if self.solved_at != self._initial_solved_at:
            became_solved = False
        elif update_fields and 'status' not in update_fields:
            became_solved = False
        elif not self.status or not self.status.is_solved:
            became_solved = False
        elif self.pk:
            became_solved = not self._initial_status_is_solved
        else:
            became_solved = True

        if became_solved:
            self.solver = get_current_user()
            self.solved_at = timezone.now()
            # In case of a second `save` call on the same object.
            self._initial_solved_at = self.solved_at

    def __str__(self):
        """Return str representation of the instance."""
        return "Issue {}: `{}`".format(self.pk, self.title)


class IssueUpdate(IssueBase):
    """Representation of an issue state after each modification.

    Not currently being  read anywhere, but it's almost guaranteed that
    the full history will be needed in the future.
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
