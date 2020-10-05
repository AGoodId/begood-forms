# encoding: utf-8
from datetime import datetime
import re
import base64
import io


from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.sites.managers import CurrentSiteManager
from django.core.mail import get_connection, EmailMessage
from django.template import loader, Context
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.text import slugify


from jsonfield import JSONField

from reportlab.pdfgen import canvas
#from PyPDF2 import PdfFileWriter

from begood.fields import ListField
from begood_sites.fields import MultiSiteField, RadioChoiceField


USE_SENDGRID = not settings.DEBUG and settings.SENDGRID_API_KEY
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (Mail, Attachment, From, To, ReplyTo, HtmlContent, Content, MimeType)
except ImportError:
    print('sendgrid import exception')
    USE_SENDGRID = False


ACTION_TYPE_CHOICES = (
    ('em', _('Send email')),
    ('ex', _('Post to website')),
)

FIELD_TYPE_CHOICES = (
    ('t', _('Text')),
    ('ta', _('Text Area')),
    ('e', _('Email')),
    ('ph', _('Phone number')),
    ('n', _('Number')),
    ('b', _('Checkbox')),
    ('c', _('Choices')),
    ('d', _('Date')),
    ('tm', _('Time')),
    ('tq', _('CourseExam')),
    ('dt', _('Date & Time')),
    ('h', _('Hidden')),
    ('pn', _('Personal number')),
    ('he', _('Header')),
)

ACCEPTED_FILE_TYPES = [
  'image/jpg',
  'image/jpeg',
  'application/pdf'
  ]


def validate_phone_number(value):
  pattern = r'^\+?(\d|(\s\d)|(\d\s)){2,4}\s?\-?\s?(\d|(\s\d)|(\d\s)){5,7}$'
  valid_content = bool(re.match(pattern, value))
  if not valid_content:
    raise ValidationError(
        _(u"Inte rätt formaterat telefon nummer."))


def validate_ssn(value):
  def dubbla(k):
      k = 2 * k
      if k > 9:
          k -= 9
      return k

  def check(pnr):
      sum = 0
      for i in [1, 3, 5, 7, 9]:
          sum += int(pnr[i])
      for i in [0, 2, 4, 6, 8]:
          sum += dubbla(int(pnr[i]))
      return sum % 10 == 0

  ssn = value
  if len(value) != 12:
    raise ValidationError(
        _("Must be 12 numbers long"))

  day = int(value[6:8])
  month = int(value[4:6])

  if month < 1 or month > 12 or day < 1 or day > 31:
    raise ValidationError(
        _("Month or day seems to be wrong"))

  if not check(ssn[2:]):
    raise ValidationError(_("Incorrect SSN"))


class BeGoodForm(models.Model):
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'), blank=True)
  valid_content = models.TextField(_('thank you message'), blank=True)
  confirm_mail = models.BooleanField(_('send thank you to e-mail'), help_text=_('if there is an e-mail field the thank you message will be sent to the first defined e-mail field by email.'), default=False)
  confirm_subject = models.CharField(_('subject for thank you e-mail'), max_length=255, blank=True)
  action = models.CharField(
      _('action'), max_length=2,
      choices=ACTION_TYPE_CHOICES, default='em')
  target = models.TextField(
      _('target'),
      help_text=_("The email addresses to send to, or the website to post to."))

  start_date = models.DateTimeField(blank=True, null=True)
  end_date = models.DateTimeField(blank=True, null=True)

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
    fileattrs = dict(
      (filefield.name, filefield.get_form_field()) for filefield in self.filefields.all()
    )
    attrs.update(fileattrs)
    return type("GeneratedBeGoodForm", (forms.Form,), attrs)

  def is_open(self):
    if self.end_date:
      return self.start_date < datetime.now() and datetime.now() < self.end_date
    return self.start_date < datetime.now()

  def to_open(self):
    if self.start_date:
      return datetime.now() < self.start_date
    return False

  def is_closed(self):
    return self.end_date < datetime.now()

  def have_filefields(self):
    return self.filefields.exists()

  def process(self, request):
    form_class = self.get_form_class()

    if request.method == 'POST':

      if not self.is_open():
        form = form_class()
        return form

      form = form_class(request.POST, request.FILES)
      if form.is_valid():
        filefields = [f.field for f in form if f.field.__class__.__name__ == 'FileField']
        file_atts = []
        valid_errors = []
        for f in filefields:
          try:
            file_att = request.FILES[f.help_text]
            if file_att.content_type in ACCEPTED_FILE_TYPES:
              file_atts.append(file_att)
            else:
              error = ValidationError(
                _('Ogiltig filtyp: %(filtyp)s : %(filnamn)s'),
                code='invalid',
                params={'filtyp': file_att.content_type,'filnamn': file_att._name},
                )
              valid_errors.append(error)
          except MultiValueDictKeyError as e:
            if f.required:  # Add form.field
              return form
        if valid_errors:
          raise ValidationError(valid_errors)

        if self.action == 'em':
          # Construct an email and send it
          if 'subject' in form.cleaned_data:
            subject = form.cleaned_data['subject']
          else:
            subject = _('Submitted form: ') + self.name

          if 'from' in form.cleaned_data:
            from_address = form.cleaned_data['from']
          elif '@' in self.target:
            from_address = self.target.split(',')[0]
          else:
            from_address = settings.DEFAULT_FROM_EMAIL

          # Create message from a template
          fields = [{'label': f.label, 'value': form.cleaned_data[f.name]} for f in form if f.field.__class__.__name__ != 'FileField']
          send_date = datetime.now()
          context = Context({
              'fields': fields,
              'date': send_date,
          })
          t = loader.get_template('begood_forms/email.txt')
          message = t.render(context)

          # Interpolate content from form where wanted
          def replacement(m):
            key = m.group(2)
            try:
              return form.cleaned_data[key]
            except KeyError:
              return key
          pattern = r'{{( |&nbsp;)*([a-zA-Z0-9-]+)( |&nbsp;)*}}'
          self.valid_content = re.sub(pattern, replacement, self.valid_content)

          begood_form_pdf = getattr(settings, "BEGOOD_FORM_PDF", False)
          if begood_form_pdf:
            from reportlab.lib.units import cm, inch

            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import Paragraph, Frame
            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            styleH = styles['Heading1']
            story = []
            #add some flowables
            story.append(Paragraph(self.name,styleH))

            for field in fields:
              if not isinstance(field['value'], basestring):
                value = str(field['value'])
              else:
                value = field['value']
              row_string = u':'.join((field['label'], value)).encode('utf-8').strip()
              story.append(Paragraph(row_string, styleN))

            date_string = 'Skickat: ' + send_date.strftime("%m/%d/%Y, %H:%M:%S")
            story.append(Paragraph(date_string, styleN))

            pdf_buffer = io.BytesIO()
            pdf = canvas.Canvas(pdf_buffer, bottomup=1)

            f = Frame(inch, inch, 6*inch, 9*inch, showBoundary=1)
            f.addFromList(story,pdf)

            #from reportlab.platypus import SimpleDocTemplate, Image
            #pdf.translate(cm,cm)
            pdf.showPage()
            for att in []: #file_atts:
              print('test')
              print(att)
              if att.temporary_file_path():
                file_path = att.temporary_file_path()
                image_file = file_path + '/' + att.name
              if att.content_type == 'application/pdf':
                pass
              else:
                pdf.drawImage(att, 0, 0, width=cm*10, preserveAspectRatio=True)
              pdf.showPage()
            pdf.save()

          mails = None
          if self.confirm_mail and self.confirm_subject and self.valid_content:
            email_fields = [f.field for f in form if f.field.__class__.__name__ == 'EmailField']
            if email_fields:
              field = self.fields.filter(type='e')[0].name
              email = form.cleaned_data[field]
              thank_you_context = Context({
                  'valid_content': self.valid_content.encode('utf-8'),  # ??
              })
              t = loader.get_template('begood_forms/thank_you_mail.html')
              thank_you_message = t.render(thank_you_context)
              # Ugly hack because wysiwyg-editor doesnt add linebreaks
              # msg = strip_tags(self.valid_content.replace('</p>', '</p>\r\n\r\n').replace('<br>', '<br>\r\n'))

              # Overwrite the first message with one with a correct email specified
              mail1 = EmailMessage(
                subject,
                message,
                email,
                self.target.split(','),
                headers={
                  'Reply-To': email,
                  'Sender': settings.DEFAULT_FROM_EMAIL,
                },
              )
              try:
                if begood_form_pdf:
                  mail1.attach(filename='sammanfattning.pdf', content=pdf_buffer.getvalue())
                  pdf_buffer.close()
                for att in file_atts:
                  mail1.attach(filename=att._name, content=att.read())
              except Exception as e:
                pdf_buffer.close()
                print('BeGoodForm email attachment error: %s' % e)
                raise
              mails = [mail1]
              if USE_SENDGRID:
                print('mail sendgrid')
                mail2 = Mail(
                  from_email=From(from_address),
                  to_emails=To(email),
                  subject=self.confirm_subject)
                #print(thank_you_message)
                mail2.add_content(mime_type='text/html', content=str(thank_you_message.encode('utf-8')))
                mail2.reply_to=ReplyTo(from_address)
              else:
                mail2 = EmailMessage(
                  self.confirm_subject,
                  thank_you_message,
                  from_address,
                  [email],
                  headers={
                    'Reply-To': from_address,
                    'Sender': settings.DEFAULT_FROM_EMAIL,
                  },
                )
                mails.append(mail2)
          
          if not mails:
              mail1 = EmailMessage(
                subject,
                message,
                from_address,
                self.target.split(','),
                headers={
                  'Reply-To': from_address,
                  'Sender': settings.DEFAULT_FROM_EMAIL,
                },
              )
              try:
                if begood_form_pdf:
                  mail1.attach(filename='sammanfattning.pdf', content=pdf_buffer.getvalue())
                  pdf_buffer.close()
                for att in file_atts:
                  mail1.attach(filename=att._name, content=att.read())
              except Exception as e:
                pdf_buffer.close()
                print('BeGoodForm email attachment error: %s' % e)
                raise
              mails = [mail1]

          if USE_SENDGRID:
            try:
              sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
              response = sg.send(mail2)
            except Exception as e:
              print(str(e))
              raise

          fail_silently = getattr(settings, "EMAIL_FAIL_SILENTLY", True)
          conn = get_connection(fail_silently=fail_silently)
          conn.send_messages(mails)

          # Store as a database entry as well
          form_message = BeGoodFormMessage(
              form=self, subject=subject, from_address=from_address,
              to_address=self.target, message=message, date=send_date, data=fields
          )
          form_message.save()
          form_message.sites.add(*self.sites.all().values_list('id', flat=True))
          for f in filefields:
            try:
              this_file = request.FILES[f.help_text]
              form_filefield = BeGoodFormFileField.objects.get(form=self, label=f.label)
              message_file = BeGoodFormMessageFile(
                form_message=form_message,
                form_filefield=form_filefield,
                file=this_file)
              message_file.save()
            except MultiValueDictKeyError as e:
              pass
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

    if self.type == 'ph':  # Phone number
      field = forms.CharField(validators=[validate_phone_number])

    if self.type == 'b':  # Checkbox
      field = forms.BooleanField(required=False)

    if self.type == 'c':  # Choices
      field = forms.ChoiceField(choices=[(c, c) for c in self.choices])
    
    if self.type == 'tq':  # Test Choices
      choices = []
      correct = ""
      for tq in self.choices:
        tq=tq.split(u';;')
        choices.append((tq[0],tq[0]))
        if(tq[1] == "True"):
          correct = tq[0]

      field = RadioChoiceField(choices)
      field.correct = correct
        
    if self.type == 'd':  # Date
      field = forms.DateField()

    if self.type == 'tm':  # Time
      field = forms.TimeField()

    if self.type == 'dt':  # Date & Time
      field = forms.DateTimeField()

    if self.type == 'h':  # Hidden
      field = forms.CharField(widget=forms.widgets.HiddenInput())

    if self.type == 'pn':  # Social security number
      field = forms.CharField(
          help_text=_('YYYYMMDDXXXX'),
          validators=[validate_ssn]
      )

    if self.type == 'he':  # Header
      self.required = False
      class HeaderWidget(forms.Widget):
        def render(self, name, value, attrs=None):
          label =  self.attrs['label']
          return mark_safe('<h3>'+label+'</h3>')

      field = forms.CharField(
          widget=HeaderWidget(attrs={'label': self.label})
      )
      self.label = None

    if field:
      field.required = self.required
      field.label = self.label
      if self.initial:
        field.initial = self.initial
      return field


class BeGoodFormFileField(models.Model):
  form = models.ForeignKey(BeGoodForm, verbose_name=_('form'), related_name="filefields")
  label = models.CharField(_('label'), max_length=255)
  name = models.SlugField(_('name'), max_length=100)
  required = models.BooleanField(_('required'), default=True)
  order = models.PositiveIntegerField(_('order'))

  class Meta:
    ordering = ['order']
    verbose_name = _('filefield')
    verbose_name_plural = _('filefields')

  def __unicode__(self):
    return unicode(self.form) + ' - ' + self.label

  def get_form_field(self):
    field = forms.FileField()
    field.required = self.required
    field.label = self.label
    field.help_text = self.name
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


class BeGoodFormMessageFile(models.Model):
  form_message = models.ForeignKey(
    BeGoodFormMessage,
    verbose_name=_('form_message'),
    related_name="message_files")
  form_filefield = models.ForeignKey(
    BeGoodFormFileField,
    verbose_name=_('form_filefield'),
    related_name="message_files")
  file = models.FileField(
    upload_to='formfiles',
    max_length=255,
    blank=True,
    null=True)
