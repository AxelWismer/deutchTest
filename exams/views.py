from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

# Views
from custom import customViews

# Forms
from .forms import ExamForm

# Models
from .models import Exam, Word

# Create your views here.
APP_NAME = 'exams'
APP_LABEL = 'exams:'


class ExamListView(customViews.CustomListView):
    model = Exam
    fields = ['title']


class ExamCreateView(customViews.CustomCreateView):
    model = Exam
    form_class = ExamForm
    success_url = reverse_lazy(APP_LABEL + 'exam_list')


class ExamUpdateView(customViews.CustomUpdateView):
    model = Exam
    form_class = ExamForm

    def get_context_data(self, **kwargs):
        context = super(ExamUpdateView, self).get_context_data(**kwargs)
        context['object_list'] = self.object.word_set.all().order_by('position')
        context['fields'] = ['position', 'word']
        context['update'] = 'true'
        return context

class ExamDeleteView(customViews.CustomDeleteView):
    model = Exam


def createExamWords(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.word_set.all().delete()
    create_words(exam.evaluation_text.split(), exam.solution.split(), exam)
    return redirect(APP_LABEL +  'exam_update', pk=pk)


def is_word(word):
    prev = ''
    for i in word:
        if i == '_' and i == prev:
            return True
        else:
            prev = i
    return False

def clean_word(word):
    w = ''
    for i in word:
        if i.isalpha():
            w += i
        elif not i.isalpha() and w == '':
            continue
        else:
            return w
    return w

def create_words(words, solution, exam):
    count = -1
    for word in words:
        count+= 1
        if is_word(word):
            # print("word:", word, 'clean:', clean_word(word))
            Word(
                word=clean_word(solution[count]),
                prefix=clean_word(word),
                exam=exam,
                position=count,
            ).save()



