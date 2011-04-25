# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Task'
        db.create_table('django_ztask_task', (
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('function_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('args', self.gf('django.db.models.fields.TextField')()),
            ('kwargs', self.gf('django.db.models.fields.TextField')()),
            ('retry_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_exception', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('next_attempt', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('failed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('django_ztask', ['Task'])


    def backwards(self, orm):
        
        # Deleting model 'Task'
        db.delete_table('django_ztask_task')


    models = {
        'django_ztask.task': {
            'Meta': {'object_name': 'Task'},
            'args': ('django.db.models.fields.TextField', [], {}),
            'failed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'function_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'last_exception': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'next_attempt': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'retry_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        }
    }

    complete_apps = ['django_ztask']
