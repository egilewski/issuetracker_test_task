"""Admin views for `core` app."""
from django.db.models import Min, Max, Avg, F
from django.contrib import admin

from .models import Issue, IssueStatus, IssueCategory
from .utils import round_timedelta_to_minute


class IssueAdmin(admin.ModelAdmin):
    """Admin options for `Issue` model."""

    readonly_fields = ('created_at', 'updated_at', 'submitter', 'solver')

    def get_actions(self, request):
        """Return list of available action.

        Excludes `delete_selected` from the default list.
        """
        actions = super(IssueAdmin, self).get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def has_delete_permission(self, request, obj=None):
        """Return False to disable deletion."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Return model instances change list/actions page view.

        Add stats variables to the context.
        """
        extra_context = extra_context or {}
        stats = self.model.objects.filter(solved_at__isnull=False).aggregate(
            min_solution_time=Min(F('solved_at') - F('created_at')),
            max_solution_time=Max(F('solved_at') - F('created_at')),
            avg_solution_time=Avg(F('solved_at') - F('created_at')))
        extra_context['min_solution_time'] = round_timedelta_to_minute(
            stats['min_solution_time'])
        extra_context['max_solution_time'] = round_timedelta_to_minute(
            stats['max_solution_time'])
        extra_context['avg_solution_time'] = round_timedelta_to_minute(
            stats['avg_solution_time'])
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueStatus)
admin.site.register(IssueCategory)
