from datetime import datetime


from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.sites.managers import CurrentSiteManager
from django.core.mail import send_mail
from django.template import loader, Context


from begood.fields import ListField # TODO: Break out listfield
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
  ('t', _('Time')),
  ('dt', _('Date & Time')),
  ('h', _('Hidden')),
)


class BeGoodForm(models.Model):
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'), blank=True)
  valid_content = models.TextField(_('thank you message'), blank=True)
  action = models.CharField(_('action'), max_length=2,
      choices=ACTION_TYPE_CHOICES, default='em')
  target = models.TextField(_('target'),
      help_text="The email addresses to send to, or the website to post to.")

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
    attrs = dict((field.name, field.get_form_field())
        for field in self.fields.all())
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

          send_mail(subject, message, from_address, self.target.split(','), fail_silently=True)

          # Store as a database entry as well
          form_message = BeGoodFormMessage(form=self, subject=subject, from_address=from_address,
              to_address=self.target, message=message, date=send_date)
          form_message.save()
          form_message.sites.add(*self.sites.all().values_list('id', flat=True))
    else:
      form = form_class()

    return form


class BeGoodFormField(models.Model):
  form = models.ForeignKey(BeGoodForm, related_name="fields")
  label = models.CharField(_('label'), max_length=255)
  name = models.SlugField(_('name'), max_length=100)
  initial = models.TextField(_('initial value'), blank=True)
  required = models.BooleanField(_('required'), default=True)
  type = models.CharField(_('type'), max_length=2,
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
    if self.type == 't': # Text
      return forms.CharField(max_length=255, required=self.required, label=self.label)

    if self.type == 'ta': # Text Area
      return forms.CharField(required=self.required, label=self.label, widget=forms.widgets.Textarea())

    if self.type == 'e': # Email
      return forms.EmailField(required=self.required, label=self.label)

    if self.type == 'n': # Number
      return forms.DecimalField(required=self.required, label=self.label)

    if self.type == 'c': # Choices
      return forms.ChoiceField(choices=[(c,c) for c in self.choices], required=self.required, label=self.label)

    if self.type == 'd': # Date
      return forms.DateField(required=self.required, label=self.label)

    if self.type == 't': # Time
      return forms.TimeField(required=self.required, label=self.label)

    if self.type == 'dt': # Date & Time
      return forms.DateTimeField(required=self.required, label=self.label)

    if self.type == 'h': # Hidden
      return forms.CharField(required=self.required, label=self.label, widget=forms.widgets.HiddenInput())


class BeGoodFormMessage(models.Model):
  form = models.ForeignKey(BeGoodForm, related_name="messages")
  subject = models.CharField(_('subject'), max_length=2047)
  from_address = models.CharField(_('from'), max_length=2047)
  to_address = models.CharField(_('to'), max_length=2047)
  message = models.TextField(_('message'), blank=True)
  date = models.DateTimeField(_('date'))

  sites = MultiSiteField()

  objects = models.Manager()
  on_site = CurrentSiteManager()

  class Meta:
    ordering = ['date']
    verbose_name = _('message')
    verbose_name_plural = _('messages')

  def __unicode__(self):
    return 'Message from ' + unicode(self.form) + ' ' + unicode(self.date)

