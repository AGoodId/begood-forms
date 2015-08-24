from datetime import datetime
import re


from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.managers import CurrentSiteManager
from django.core.mail import send_mail, send_mass_mail
from django.template import loader, Context
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags


from jsonfield import JSONField


from begood.fields import ListField  # TODO: Break out listfield
from begood_sites.fields import MultiSiteField, SingleSiteField


ACTION_TYPE_CHOICES = (
    ('em', _('Send email')),
    ('ex', _('Post to website')),
)

FIELD_TYPE_CHOICES = (
    ('t', _('Text')),
    ('ta', _('Text Area')),
    ('e', _('Email')),
    ('n', _('Number')),
    ('c', _('Choices')),
    ('d', _('Date')),
    ('tm', _('Time')),
    ('dt', _('Date & Time')),
    ('h', _('Hidden')),
)


class BeGoodForm(models.Model):
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'), blank=True)
  valid_content = models.TextField(_('thank you message'), blank=True)
  confirm_mail = models.BooleanField(_('send thank you to e-mail'), help_text=_('if there is an e-mail field the thank you message will be sent by email.'), default=False)
  confirm_subject = models.CharField(_('subject for thank you e-mail'), max_length=255, blank=True)
  action = models.CharField(
      _('action'), max_length=2,
      choices=ACTION_TYPE_CHOICES, default='em')
  target = models.TextField(
      _('target'),
      help_text=_("The email addresses to send to, or the website to post to."))

  sites = MultiSiteField()

  objects = models.Manager()
  on_site = CurrentSiteManager()

  class Meta:
    verbose_name = _('form')
    verbose_name_plural = _('forms')

  def __unicode__(self):
    return self.name

  def get_form_class(self):
    """
    Get a Django form class that this instance represents.
    """
    attrs = dict(
        (field.name, field.get_form_field()) for field in self.fields.all()
    )
    return type("GeneratedBeGoodForm", (forms.Form,), attrs)

  def process(self, request):
    form_class = self.get_form_class()

    if request.method == 'POST':
      form = form_class(request.POST)
      if form.is_valid():
        if self.action == 'em':
          # Construct an email and send it
          if 'subject' in form.cleaned_data:
            subject = form.cleaned_data['subject']
          else:
            subject = _('Submitted form: ') + self.name

          if 'from' in form.cleaned_data:
            from_address = form.cleaned_data['from']
          else:
            from_address = settings.DEFAULT_FROM_EMAIL

          # Create message from a template
          fields = [{'label': f.label, 'value': form.cleaned_data[f.name]} for f in form]
          send_date = datetime.now()
          context = Context({
              'fields': fields,
              'date': send_date,
          })
          t = loader.get_template('begood_forms/email.txt')
          message = t.render(context)

          mails = [
            (subject, message, from_address, self.target.split(','))
          ]

          # Interpolate content from form where wanted
          def replacement(m):
            key = m.group(2)
            try:
              return form.cleaned_data[key]
            except KeyError:
              return key
          pattern = r'{{( |&nbsp;)*([a-zA-Z0-9-]+)( |&nbsp;)*}}'
          self.valid_content = re.sub(pattern, replacement, self.valid_content)

          if self.confirm_mail and self.confirm_subject and self.valid_content:
            try:
              email_fields = [f.field for f in form if f.field.__class__.__name__ == 'EmailField']
              if email_fields:
                email = form.cleaned_data[slugify(email_fields[0].label)]
                # Ugly hack because wysiwyg-editor doesnt add linebreaks
                msg = strip_tags(self.valid_content.replace('</p>', '</p>\r\n\r\n').replace('<br>', '<br>\r\n'))
                mails.append((self.confirm_subject, msg, from_address, [email]))
            except:
              pass
          send_mass_mail(mails, fail_silently=True)

          # Store as a database entry as well
          form_message = BeGoodFormMessage(
              form=self, subject=subject, from_address=from_address,
              to_address=self.target, message=message, date=send_date, data=fields
          )
          form_message.save()
          form_message.sites.add(*self.sites.all().values_list('id', flat=True))
    else:
      form = form_class()

    return form


class BeGoodFormField(models.Model):
  form = models.ForeignKey(BeGoodForm, verbose_name=_('form'), related_name="fields")
  label = models.CharField(_('label'), max_length=255)
  name = models.SlugField(_('name'), max_length=100)
  initial = models.TextField(_('initial value'), blank=True)
  required = models.BooleanField(_('required'), default=True)
  type = models.CharField(
      _('type'), max_length=2,
      choices=FIELD_TYPE_CHOICES, default='t')
  choices = ListField(_('choices'), blank=True)
  order = models.PositiveIntegerField(_('order'))

  class Meta:
    ordering = ['order']
    verbose_name = _('field')
    verbose_name_plural = _('fields')

  def __unicode__(self):
    return unicode(self.form) + ' - ' + self.label

  def get_form_field(self):
    field = None
    if self.type == 't':  # Text
      field = forms.CharField(max_length=255)

    if self.type == 'ta':  # Text Area
      field = forms.CharField(widget=forms.widgets.Textarea())

    if self.type == 'e':  # Email
      field = forms.EmailField()

    if self.type == 'n':  # Number
      field = forms.DecimalField()

    if self.type == 'c':  # Choices
      field = forms.ChoiceField(choices=[(c, c) for c in self.choices])

    if self.type == 'd':  # Date
      field = forms.DateField()

    if self.type == 'tm':  # Time
      field = forms.TimeField()

    if self.type == 'dt':  # Date & Time
      field = forms.DateTimeField()

    if self.type == 'h':  # Hidden
      field = forms.CharField(widget=forms.widgets.HiddenInput())

    if field:
      field.required = self.required
      field.label = self.label
      if self.initial:
        field.initial = self.initial
      return field


class BeGoodFormMessage(models.Model):
  form = models.ForeignKey(BeGoodForm, verbose_name=_('form'), related_name="messages")
  subject = models.CharField(_('subject'), max_length=2047)
  from_address = models.CharField(_('from'), max_length=2047)
  to_address = models.CharField(_('to'), max_length=2047)
  message = models.TextField(_('message'), blank=True)
  date = models.DateTimeField(_('date'))
  data = JSONField()

  sites = MultiSiteField()

  objects = models.Manager()
  on_site = CurrentSiteManager()

  class Meta:
    ordering = ['date']
    verbose_name = _('message')
    verbose_name_plural = _('messages')

  def __unicode__(self):
    return 'Message from ' + unicode(self.form) + ' ' + unicode(self.date)
