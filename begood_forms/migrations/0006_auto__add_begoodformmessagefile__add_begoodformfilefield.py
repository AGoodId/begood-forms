# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BeGoodFormMessageFile'
        db.create_table(u'begood_forms_begoodformmessagefile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='message_files', to=orm['begood_forms.BeGoodFormMessage'])),
            ('form_filefield', self.gf('django.db.models.fields.related.ForeignKey')(related_name='message_files', to=orm['begood_forms.BeGoodFormFileField'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'begood_forms', ['BeGoodFormMessageFile'])

        # Adding model 'BeGoodFormFileField'
        db.create_table(u'begood_forms_begoodformfilefield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='filefields', to=orm['begood_forms.BeGoodForm'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'begood_forms', ['BeGoodFormFileField'])


    def backwards(self, orm):
        # Deleting model 'BeGoodFormMessageFile'
        db.delete_table(u'begood_forms_begoodformmessagefile')

        # Deleting model 'BeGoodFormFileField'
        db.delete_table(u'begood_forms_begoodformfilefield')


    models = {
        u'begood_forms.begoodform': {
            'Meta': {'object_name': 'BeGoodForm'},
            'action': ('django.db.models.fields.CharField', [], {'default': "'em'", 'max_length': '2'}),
            'confirm_mail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'confirm_subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sites': ('begood_sites.fields.MultiSiteField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.TextField', [], {}),
            'valid_content': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'begood_forms.begoodformfield': {
            'Meta': {'ordering': "['order']", 'object_name': 'BeGoodFormField'},
            'choices': ('begood.fields.ListField', [], {'blank': 'True'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['begood_forms.BeGoodForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'t'", 'max_length': '2'})
        },
        u'begood_forms.begoodformfilefield': {
            'Meta': {'ordering': "['order']", 'object_name': 'BeGoodFormFileField'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filefields'", 'to': u"orm['begood_forms.BeGoodForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'begood_forms.begoodformmessage': {
            'Meta': {'ordering': "['date']", 'object_name': 'BeGoodFormMessage'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['begood_forms.BeGoodForm']"}),
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '2047'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sites': ('begood_sites.fields.MultiSiteField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '2047'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '2047'})
        },
        u'begood_forms.begoodformmessagefile': {
            'Meta': {'object_name': 'BeGoodFormMessageFile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'form_filefield': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'message_files'", 'to': u"orm['begood_forms.BeGoodFormFileField']"}),
            'form_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'message_files'", 'to': u"orm['begood_forms.BeGoodFormMessage']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['begood_forms']