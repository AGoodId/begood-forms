# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BeGoodForm.start_date'
        db.add_column(u'begood_forms_begoodform', 'start_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BeGoodForm.end_date'
        db.add_column(u'begood_forms_begoodform', 'end_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BeGoodForm.start_date'
        db.delete_column(u'begood_forms_begoodform', 'start_date')

        # Deleting field 'BeGoodForm.end_date'
        db.delete_column(u'begood_forms_begoodform', 'end_date')


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
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['begood_forms']