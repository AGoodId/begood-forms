from django.forms import widgets
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import render


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
      (None, {'fields': ['name', 'description', 'action', 'target']}),
      (_('Confirmation'), {'fields': ['valid_content', 'confirm_mail', 'confirm_subject']}),
      (_('Advanced'), {'fields': ['sites'], 'classes': ['collapse']}),
  ]
  list_display = ['name', 'messages_links']
  search_fields = ['name']
  actions = ['generate_list']
  inlines = [BeGoodFormFieldInlineAdmin, ]

  def generate_list(modeladmin, request, queryset):
    context = {'forms': queryset}
    return render(request, 'begood_forms/form_message_list.html', context)
  generate_list.short_description = _("Get a list of all answers")

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
  list_display = ['form', 'from_address', 'to_address', 'date', ]
  list_display_links = ('from_address', 'to_address', 'date', )
  list_filter = ('form', 'date')
  search_fields = ['message', 'from_address', 'to_address', 'subject']
  fields = ['date', 'from_address', 'to_address', 'subject', 'message']
  readonly_fields = ['message', 'from_address', 'to_address', 'subject', 'date']
  list_per_page = 50


admin.site.register(BeGoodForm, BeGoodFormAdmin)
admin.site.register(BeGoodFormMessage, BeGoodFormMessageAdmin)
