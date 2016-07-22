# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BeGoodForm'
        db.create_table(u'begood_forms_begoodform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('valid_content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('action', self.gf('django.db.models.fields.CharField')(default='em', max_length=2)),
            ('target', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'begood_forms', ['BeGoodForm'])

        # Adding M2M table for field sites on 'BeGoodForm'
        db.create_table(u'begood_forms_begoodform_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('begoodform', models.ForeignKey(orm[u'begood_forms.begoodform'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(u'begood_forms_begoodform_sites', ['begoodform_id', 'site_id'])

        # Adding model 'BeGoodFormField'
        db.create_table(u'begood_forms_begoodformfield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['begood_forms.BeGoodForm'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('initial', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='t', max_length=2)),
            ('choices', self.gf('begood.fields.ListField')(blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'begood_forms', ['BeGoodFormField'])

        # Adding model 'BeGoodFormMessage'
        db.create_table(u'begood_forms_begoodformmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['begood_forms.BeGoodForm'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=2047)),
            ('from_address', self.gf('django.db.models.fields.CharField')(max_length=2047)),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=2047)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'begood_forms', ['BeGoodFormMessage'])

        # Adding M2M table for field sites on 'BeGoodFormMessage'
        db.create_table(u'begood_forms_begoodformmessage_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('begoodformmessage', models.ForeignKey(orm[u'begood_forms.begoodformmessage'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(u'begood_forms_begoodformmessage_sites', ['begoodformmessage_id', 'site_id'])


    def backwards(self, orm):
        
        # Deleting model 'BeGoodForm'
        db.delete_table(u'begood_forms_begoodform')

        # Removing M2M table for field sites on 'BeGoodForm'
        db.delete_table('begood_forms_begoodform_sites')

        # Deleting model 'BeGoodFormField'
        db.delete_table(u'begood_forms_begoodformfield')

        # Deleting model 'BeGoodFormMessage'
        db.delete_table(u'begood_forms_begoodformmessage')

        # Removing M2M table for field sites on 'BeGoodFormMessage'
        db.delete_table('begood_forms_begoodformmessage_sites')


    models = {
        u'begood_forms.begoodform': {
            'Meta': {'object_name': 'BeGoodForm'},
            'action': ('django.db.models.fields.CharField', [], {'default': "'em'", 'max_length': '2'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sites': ('begood_sites.fields.MultiSiteField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
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
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'t'", 'max_length': '2'})
        },
        u'begood_forms.begoodformmessage': {
            'Meta': {'ordering': "['date']", 'object_name': 'BeGoodFormMessage'},
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
