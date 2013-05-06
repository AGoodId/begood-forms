from django.template import loader, Library, RequestContext


from begood_forms.models import BeGoodForm


register = Library()


@register.assignment_tag
def get_form(id_or_name):
  try:
    return BeGoodForm.objects.get(id=id_or_name)
  except BeGoodForm.DoesNotExist:
    try:
      return BeGoodForm.objects.get(name=id_or_name)
    except BeGoodForm.DoesNotExist:
      return None


@register.assignment_tag(takes_context=True)
def begood_form(context, id_or_name):
  form = get_form(id_or_name)
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
      'form': form.form,
      'description': form.description,
      'valid_content': form.valid_content,
      'action': action,
    }))
