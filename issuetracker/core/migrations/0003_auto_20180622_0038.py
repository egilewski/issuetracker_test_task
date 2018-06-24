# Generated by Django 2.0.6 on 2018-06-22 00:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_issueupdate'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issuecategory',
            options={'verbose_name_plural': 'issue categories'},
        ),
        migrations.AlterModelOptions(
            name='issuestatus',
            options={'verbose_name_plural': 'issue statuses'},
        ),
        migrations.AddField(
            model_name='issue',
            name='solved_at',
            field=models.DateTimeField(blank=True, help_text='Automatically set to the current time when `status` is changed to a solved one, unless it is changed manually.', null=True),
        ),
        migrations.AddField(
            model_name='issuestatus',
            name='is_solved',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issueupdate',
            name='solved_at',
            field=models.DateTimeField(blank=True, help_text='Automatically set to the current time when `status` is changed to a solved one, unless it is changed manually.', null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='solver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solved_issues', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='issuecategory',
            name='title',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='issuestatus',
            name='title',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
