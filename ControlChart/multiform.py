#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
View class to create at Form at of multiple ModelsForms
"""

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView


class MultiFormMixin(ContextMixin):
    """
    Mixin Class to handle the data of a MultiFormView
    """
    form_classes = {}
    prefixes = {}
    success_urls = {}
    grouped_forms = {}

    initial = {}
    prefix = None
    success_url = None

    def get_form_classes(self):
        """
        Retruns a dictonary with the classes of the used ModelForms
        """
        return self.form_classes

    def get_forms(self, form_classes, form_names=None, bind_all=False):
        """
        Creates the form instances out of the given form classes
        :param form_classes: Dictonary with form classes
        :param form_names: List of forms which data should be used in the kwargs
        :param bind_all: Set True to use the data of all forms
        :return: Dictonary with the created form instances
        """
        return dict(
            [(key,
              self._create_form(
                  key, cls, (form_names and key in form_names) or bind_all)) \
             for key, cls in form_classes.items()])

    def get_form_kwargs(self, form_name, bind_form=False):
        """
        Gets the prefix, initials and POST arguments from a given form
        :param form_name: Name of the form
        :param bind_form: Set True to read the POST data
        :return: Dictionary with the following keys ['initial', 'prefix' and
                 'data', files (only if bind_form)]
        """
        kwargs = {}
        kwargs.update({'initial': self.get_initial(form_name)})
        kwargs.update({'prefix': self.get_prefix(form_name)})

        if bind_form:
            kwargs.update(self._bind_form_data())

        return kwargs

    def forms_valid(self, forms, form_name):
        """
        Calls the form_valid method of the given form
        :param forms: Dictonary of all Form classes
        :param form_name: Form name which should check
        :return: Returns the result of the from_valid method or redirects to the
                 success_url if the form has no valid method
        """
        form_valid_method = '%s_form_valid' % form_name
        if hasattr(self, form_valid_method):
            return getattr(self, form_valid_method)(forms[form_name])
        else:
            return HttpResponseRedirect(self.get_success_url(form_name))

    def forms_invalid(self, forms):
        """
        Renders the forms
        """
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_initial(self, form_name):
        """
        Calls the get_initial method for the given fomr
        :param form_name: Name of the form
        :return: Dictonary with initial data
        """
        initial_method = 'get_%s_initial' % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def get_prefix(self, form_name):
        """
        Prefix of the given form
        """
        return self.prefixes.get(form_name, self.prefix)

    def get_success_url(self, form_name=None):
        """
        Returns the success_url form the given form or if no form_name given the
        success_url of the MultiForm
        """
        return self.success_urls.get(form_name, self.success_url)

    def _create_form(self, form_name, klass, bind_form):
        form_kwargs = self.get_form_kwargs(form_name, bind_form)
        form_create_method = 'create_%s_form' % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def _bind_form_data(self):
        if self.request.method in ('POST', 'PUT'):
            return {'data': self.request.POST,
                    'files': self.request.FILES, }
        return {}


class MultiFormsView(TemplateResponseMixin,
                     MultiFormMixin,
                     ProcessFormView):
    """
    View class to create at Form at of multiple ModelsForms
    """
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get('action')
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        elif self._group_exists(form_name):
            return self._process_grouped_forms(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _group_exists(self, group_name):
        return group_name in self.grouped_forms

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name,))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_grouped_forms(self, group_name, form_classes):
        form_names = self.grouped_forms[group_name]
        forms = self.get_forms(form_classes, form_names)
        if all([forms.get(form_name).is_valid()
                for form_name in form_names.values()]):
            return self.forms_valid(forms, '')
        else:
            return self.forms_invalid(forms)

    def _process_all_forms(self, form_classes):
        forms = self.get_forms(form_classes, None, True)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms, '')
        else:
            return self.forms_invalid(forms)



