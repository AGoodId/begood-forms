# encoding: utf-8
import datetime

from django.forms import widgets
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.shortcuts import render

from datatrans.utils import register

from begood.contrib.admin.widgets import WysiwygTextarea
from begood_sites.admin import SiteModelAdmin
from begood_forms.models import (
  BeGoodForm, BeGoodFormField, BeGoodFormMessage,
  BeGoodFormFileField, BeGoodFormMessageFile)


class BeGoodFormFieldInlineAdmin(admin.StackedInline):
  model = BeGoodFormField
  prepopulated_fields = {'name': ('label',)}
  fields = ['label', 'name', 'type', 'choices', 'initial', 'required', 'order']
  extra = 0


class BeGoodFormFileFieldInlineAdmin(admin.StackedInline):
  model = BeGoodFormFileField
  prepopulated_fields = {'name': ('label',)}
  fields = ['label', 'name', 'required', 'order']
  extra = 0


class BeGoodFormAdmin(SiteModelAdmin):
  fieldsets = [
      (None, {'fields': ['name', 'description', 'action', 'target', 'start_date', 'end_date']}),
      (_('Confirmation'), {'fields': ['valid_content', 'confirm_mail', 'confirm_subject']}),
      (_('Advanced'), {'fields': ['sites'], 'classes': ['collapse']}),
  ]
  list_display = ['name', 'messages_links']
  search_fields = ['name']
  actions = ['generate_list', 'export_csv']
  inlines = [BeGoodFormFieldInlineAdmin, BeGoodFormFileFieldInlineAdmin, ]

  def generate_list(modeladmin, request, queryset):
    context = {'forms': queryset}
    return render(request, 'begood_forms/form_message_list.html', context)
  generate_list.short_description = _("Get a list of all answers")

  def export_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse

    if queryset.count() > 1:
      return HttpResponse(_('You can only export 1 form at a time.'))
    queryset = queryset[0]

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s-%s.csv"' % (slugify(queryset.name), datetime.datetime.today().strftime("%Y-%m-%d"))

    writer = csv.writer(response)

    # First row is the categories.
    writer.writerow(['Datum'] + [unicode(f.label).encode('utf-8') for f in queryset.fields.all()])

    for msg in queryset.messages.all():
      row = [str(msg.date)]
      for f in queryset.fields.all():
        for test in msg.data:
          if test['label'] == f.label and f.type != 'he':
            row.append(unicode(test['value']).encode('utf-8'))
      writer.writerow(row)

    return response
  export_csv.short_description = _("Export as CSV")

  def messages_links(self, obj):
    count = BeGoodFormMessage.objects.filter(form_id=obj.id).count()
    return u'<a href="%sbegood_forms/begoodformmessage/?form=%d">%d %s</a>' % (
        settings.ADMIN_URL, obj.id, count, _('messages'))
  messages_links.short_description = _('Messages')
  messages_links.allow_tags = True

  def formfield_for_dbfield(self, field, **kwargs):
    if field.name == 'target':
      kwargs['widget'] = widgets.TextInput()
    if field.name == 'description' or field.name == 'valid_content':
      # Initiate description field with a wysiwyg editor
      kwargs['widget'] = WysiwygTextarea(
          attrs={'cols': 86, 'rows': 10}
      )
    return super(BeGoodFormAdmin, self).formfield_for_dbfield(field, **kwargs)


class BeGoodFormMessageFileInlineAdmin(admin.StackedInline):
  model = BeGoodFormMessageFile
  fields = ['file', 'form_filefield', 'file_link']
  readonly_fields = ['file', 'form_filefield', 'file_link']
  extra = 0

  def file_link(self, obj):
    return u'<a href="%s">%s</a>' % (obj.file.url, obj.file)
  file_link.short_description = _('Filen')
  file_link.allow_tags = True


class BeGoodFormMessageAdmin(SiteModelAdmin):
  list_display = ['form', 'from_address', 'to_address', 'date', ]
  list_display_links = ('from_address', 'to_address', 'date', )
  list_filter = ('form', 'date')
  search_fields = ['message', 'from_address', 'to_address', 'subject']
  fields = ['date', 'from_address', 'to_address', 'subject', 'message']
  readonly_fields = ['message', 'from_address', 'to_address', 'subject', 'date']
  list_per_page = 50
  inlines = [BeGoodFormMessageFileInlineAdmin, ]

  
class FormTranslation(object):
  fields = 'name description valid_content confirm_subject'.split()
class FormFieldTranslation(object):
  fields = ('label',)

register(BeGoodForm, FormTranslation)
register(BeGoodFormField, FormFieldTranslation)
  
admin.site.register(BeGoodForm, BeGoodFormAdmin)
admin.site.register(BeGoodFormMessage, BeGoodFormMessageAdmin)
