# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.shortcuts import reverse

from . import forms

class CkEditorFormView(generic.FormView):
    form_class = forms.CkEditorForm
    template_name = 'note_editor.html'

    def get_success_url(self):
        return reverse('ckeditor-form')


ckeditor_form_view = CkEditorFormView.as_view()