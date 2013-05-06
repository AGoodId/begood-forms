from django.forms import widgets
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext as _


from begood.contrib.admin.widgets import WysiwygTextarea
from begood_sites.admin import SiteModelAdmin, SiteVersionAdmin
from begood_forms.models import BeGoodForm, BeGoodFormField, BeGoodFormMessage


class BeGoodFormFieldInlineAdmin(admin.StackedInline):
  model = BeGoodFormField
  prepopulated_fields = {'name': ('label',)}
  fields = ['label', 'name', 'type', 'choices', 'initial', 'required', 'order']
  extra = 0


class BeGoodFormAdmin(SiteModelAdmin):
  fieldsets = [
    (None, {'fields': ['name', 'description', 'valid_content', 'action', 'target']}),
    (_('Advanced'), {'fields': ['sites'], 'classes': ['collapse']}),
  ]
  list_display = ['name', 'messages_links']
  search_fields = ['name']
  inlines = [ BeGoodFormFieldInlineAdmin, ]

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


class BeGoodFormMessageAdmin(SiteModelAdmin):
  list_display = ['form', 'from_address', 'date']
  list_display_links = ('from_address', 'date')
  list_filter = ('form', 'date')
  search_fields = ['message', 'from_address', 'to_address', 'subject']
  fields = ['date', 'from_address', 'to_address', 'subject', 'message']
  readonly_fields = ['message', 'from_address', 'to_address', 'subject', 'date']
  list_per_page = 50


admin.site.register(BeGoodForm, BeGoodFormAdmin)
admin.site.register(BeGoodFormMessage, BeGoodFormMessageAdmin)
