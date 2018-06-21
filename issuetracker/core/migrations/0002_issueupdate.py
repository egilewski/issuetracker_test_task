# Generated by Django 2.0.6 on 2018-06-21 17:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_issue_and_issuestatus_and_issuecvategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.IssueCategory')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_updates', to='core.Issue')),
                ('solver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solved_issue_updates', to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.IssueStatus')),
                ('submitter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_issue_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': ['updated_at', 'pk'],
            },
        ),
    ]
