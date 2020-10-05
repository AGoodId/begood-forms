from django.template import loader, Library, RequestContext
from django.conf import settings

from begood_forms.models import BeGoodForm


register = Library()


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__.lower()


@register.filter
def get_field_class(value):
  return getattr(settings, 'BEGOOD_FORM_CLASSES', {}).get(value, '')


@register.filter
def is_row(value):
  return value in [values[0] for values in getattr(settings, 'BEGOOD_FORM_ROWS', [])]

@register.filter
def is_end_of_row(value):
  return value in [values[1] for values in getattr(settings, 'BEGOOD_FORM_ROWS', [])]

@register.assignment_tag
def get_form(form):
  if not form:
    return None
  if isinstance(form, BeGoodForm):
    return form
  try:
    return BeGoodForm.objects.get(id=form)
  except:
    try:
      return BeGoodForm.objects.get(name=form)
    except:
      return None


@register.assignment_tag(takes_context=True)
def begood_form(context, form):
  form = get_form(form)
  request = context.get('request', None)

  if not form or not request:
    return None

  form.form = form.process(request)
  form.request = request
  return form


@register.filter
def render_form(form, template_path='begood_forms/form.html'):
  if form and form.form:
    t = loader.get_template(template_path)
    action = form.target if form.action == 'ex' else ''
    return t.render(RequestContext(form.request, {
        'begood_form': form,
        'form': form.form,
        'description': form.description,
        'valid_content': form.valid_content,
        'action': action,
    }))
