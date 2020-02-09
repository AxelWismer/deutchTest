from django.shortcuts import render
from django.urls import reverse, reverse_lazy

# Views
from custom import customViews

# Forms
from .forms import ExamForm

# Models
from .models import Exam

# Create your views here.
APP_NAME = 'exams'
APP_LABEL = 'exams:'


class ExamListView(customViews.CustomListView):
    model = Exam
    template_name = 'custom/list.html'
    fields = ['title']


class ExamCreateView(customViews.CustomCreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'custom/create_form.html'
    success_url = reverse_lazy(APP_LABEL + 'exam_list')


class ExamUpdateView(customViews.CustomUpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'custom/update_form.html'


class ExamDeleteView(customViews.CustomDeleteView):
    model = Exam
    template_name = 'custom/confirm_delete.html'