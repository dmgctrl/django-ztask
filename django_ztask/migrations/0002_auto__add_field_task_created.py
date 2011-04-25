# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Task.created'
        db.add_column('django_ztask_task', 'created', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Task.created'
        db.delete_column('django_ztask_task', 'created')


    models = {
        'django_ztask.task': {
            'Meta': {'object_name': 'Task'},
            'args': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
