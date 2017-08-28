# formsss
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django import forms

import django_excel as excel
from .choices import *
from django.contrib.auth.forms import UserCreationForm
from models import *




class UserForm(forms.Form):
    username = forms.CharField(label = "Username", required = True)
    password = forms.CharField(label = "Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label = "Password", widget=forms.PasswordInput())


class Login(forms.Form):
    username = forms.CharField(label = "Username", required = True)
    password = forms.CharField(label = "Password", required = True, widget = forms.PasswordInput() )


class CurrentCategoryModel(forms.Form):
    model_title = forms.CharField(label = "Model Title",required=True, widget = forms.TextInput(attrs ={'class': 'centering'}))

    #def __init__(self,*args,**kwargs):
    #    extra = kwargs.pop('extra')
    #    super(CurrentCategoryModel,self).__init__(*args,**kwargs)
    #    for i, question in enumerate(extra.keys()):
    #        self.fields['keyword_%s' % i] = forms.CharField(label="Keyword", initial = question, )
    #        self.fields['category_%s' % i] = forms.CharField(label="Category", initial = extra[question])
    #        self.fields['delete_%s' %  i] = forms.BooleanField(label = "Delete")




class CurrentFiles(forms.Form):
    def __init__(self,*args,**kwargs):
        choice = kwargs.pop('choice')
        super(CurrentFiles,self).__init__(*args,**kwargs)
        self.fields['optionfile'].choices=choice
    optionfile = forms.ChoiceField(label = "", widget = forms.Select(attrs = {'class': 'form options', 'id': 'dataset_options'}))

class UploadFileForm(forms.Form):
    #def __init__(self,*args,**kwargs):
    #    choice = kwargs.pop('choice')
    #    super(UploadFileForm,self).__init__(*args,**kwargs)
    #    self.fields['option'].choices=choice
    #option = forms.ChoiceField(label = "", widget = forms.Select(attrs = {'class': 'form options'}) )
    new_data = forms.FileField(label = "Upload File", required=True,)
    sheet_name = forms.CharField(label = "Excel Sheet Name",required=True,)
    text_name = forms.CharField(label = "Column Name containing Text",required=True,)
    dataset_title = forms.CharField(required=True)

class AnalyticMethod_S(forms.Form):
    optionlytic = forms.ChoiceField(label = "", choices = ANALYTIC_OPTIONS, widget = forms.Select(attrs = {'class': 'form options', 'id': 'anlyt_options'}) )

class PresentMethod(forms.Form):
    def __init__(self,*args,**kwargs):
        choice = kwargs.pop('choice')
        super(PresentMethod,self).__init__(*args,**kwargs)
        self.fields['optionpresent'].choices=choice
    optionpresent = forms.ChoiceField(label = "", widget = forms.Select(attrs = {'class': 'form options'}))
