# from https://github.com/treyhunner/django-widget-tweaks/commit/e89ba60899abfce2953bd3f5583645f5d73447a3
# adapted with snippets from widget_tweaks; modified by Nils Rokita
# TODO: move to django-spectre-css on redesign

from django import template
import re

from widget_tweaks.templatetags.widget_tweaks import ATTRIBUTE_RE

register = template.Library()


@register.tag
def render_multi_field(parser, token):
    """
    Takes form field as first argument, field number as second argument, and
    list of attribute-value pairs for all other arguments.
    Attribute-value pairs should be in the form of attribute=value OR
    attribute="a value"
    """
    error_msg = ('%r tag requires a form field and index followed by a list '
                 'of attributes and values in the form attr="value"'
                 % token.split_contents()[0])
    try:
        bits = token.split_contents()
        form_field = bits[1]
        field_index = int(bits[2])
        attr_list = bits[3:]
    except ValueError:
        raise template.TemplateSyntaxError(error_msg)

    attr_assign_dict = {}
    attr_concat_dict = {}
    for pair in attr_list:
        match = ATTRIBUTE_RE.match(pair)
        if not match:
            raise template.TemplateSyntaxError(error_msg + ": %s" % pair)
        dct = match.groupdict()
        attr, sign, value = \
            dct['attr'], dct['sign'], parser.compile_filter(dct['value'])
        if sign == "=":
            attr_assign_dict[attr] = value
        else:
            attr_concat_dict[attr] = value

    return MultiFieldAttributeNode(form_field, attr_assign_dict,
                                   attr_concat_dict, index=field_index)


class MultiFieldAttributeNode(template.Node):
    def __init__(self, field, assign_dict, concat_dict, index):
        self.field = field
        self.assign_dict = assign_dict
        self.concat_dict = concat_dict
        self.index = index

    def render(self, context):
        bounded_field = template.Variable(self.field).resolve(context)
        field = bounded_field.field.fields[self.index]
        widget = bounded_field.field.widget.widgets[self.index]

        attrs = widget.attrs.copy()
        print(attrs)
        for k, v in self.assign_dict.items():
            attrs[k] = v.resolve(context)
        for k, v in self.concat_dict.items():
            attrs[k] = widget.attrs.get(k, '') + ' ' + v.resolve(context)
        if bounded_field.errors:
            attrs['class'] = attrs.get('class', '') + ' error'

        if not bounded_field.form.is_bound:
            data = bounded_field.form.initial.get(bounded_field.name,
                                                  field.initial)
            if callable(data):
                data = data()
            data = bounded_field.field.widget.decompress(data)[self.index]
        else:
            data = bounded_field.data[self.index]
        return widget.render('%s_%d' % (bounded_field.html_name, self.index),
                             data, attrs)
