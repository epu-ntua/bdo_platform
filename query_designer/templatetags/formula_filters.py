from django import template

from query_designer.models import Formula

register = template.Library()


@register.filter
def format_errors(errors):
    return ', '.join(errors)


@register.filter
def variable_description(variable_tupple):
    return '%s (%s)' % (variable_tupple[1], Formula.find_unit(variable_tupple[0]))


@register.filter
def get_function_name(fn_with_params):
    return fn_with_params.split('(')[0]
