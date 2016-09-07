# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.manager
import jsonfield.fields
import begood.fields
import begood_sites.fields
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeGoodForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('valid_content', models.TextField(verbose_name='thank you message', blank=True)),
                ('confirm_mail', models.BooleanField(default=False, help_text='if there is an e-mail field the thank you message will be sent to the first defined e-mail field by email.', verbose_name='send thank you to e-mail')),
                ('confirm_subject', models.CharField(max_length=255, verbose_name='subject for thank you e-mail', blank=True)),
                ('action', models.CharField(default=b'em', max_length=2, verbose_name='action', choices=[(b'em', 'Send email'), (b'ex', 'Post to website')])),
                ('target', models.TextField(help_text='The email addresses to send to, or the website to post to.', verbose_name='target')),
                ('sites', begood_sites.fields.MultiSiteField(to='sites.Site')),
            ],
            options={
                'verbose_name': 'form',
                'verbose_name_plural': 'forms',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='BeGoodFormField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('name', models.SlugField(max_length=100, verbose_name='name')),
                ('initial', models.TextField(verbose_name='initial value', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('type', models.CharField(default=b't', max_length=2, verbose_name='type', choices=[(b't', 'Text'), (b'ta', 'Text Area'), (b'e', 'Email'), (b'n', 'Number'), (b'c', 'Choices'), (b'd', 'Date'), (b'tm', 'Time'), (b'dt', 'Date & Time'), (b'h', 'Hidden'), (b'pn', 'Personal number'), (b'he', 'Header')])),
                ('choices', begood.fields.ListField(verbose_name='choices', blank=True)),
                ('order', models.PositiveIntegerField(verbose_name='order')),
                ('form', models.ForeignKey(related_name='fields', verbose_name='form', to='begood_forms.BeGoodForm')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'field',
                'verbose_name_plural': 'fields',
            },
        ),
        migrations.CreateModel(
            name='BeGoodFormMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=2047, verbose_name='subject')),
                ('from_address', models.CharField(max_length=2047, verbose_name='from')),
                ('to_address', models.CharField(max_length=2047, verbose_name='to')),
                ('message', models.TextField(verbose_name='message', blank=True)),
                ('date', models.DateTimeField(verbose_name='date')),
                ('data', jsonfield.fields.JSONField(default=dict)),
                ('form', models.ForeignKey(related_name='messages', verbose_name='form', to='begood_forms.BeGoodForm')),
                ('sites', begood_sites.fields.MultiSiteField(to='sites.Site')),
            ],
            options={
                'ordering': ['date'],
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
