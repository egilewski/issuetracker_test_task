"""Admin views for `core` app."""
from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Issue, IssueStatus, IssueCategory


class IssueAdmin(admin.ModelAdmin):
    """Admin options for `Issue` model."""

    def get_actions(self, request):
        """Return list of available action.

        Excludes `delete_selected` from the default list.
        """
        actions = super(IssueAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """Return False to disable deletion."""
        return False


admin.site.unregister(Group)


admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueStatus)
admin.site.register(IssueCategory)
