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

    def get_queryset(self):
        return self.model.objects.all().order_by('title')

class ExamCreateView(customViews.CustomCreateView):
    model = Exam
    form_class = ExamForm
    success_url = reverse_lazy(APP_LABEL + 'exam_list')

    def form_valid(self, form):
        super(ExamCreateView, self).form_valid(form)
        return redirect(APP_LABEL + 'words_create', pk=self.object.pk)


class ExamUpdateView(customViews.CustomUpdateView):
    model = Exam
    form_class = ExamForm

    def get_context_data(self, **kwargs):
        context = super(ExamUpdateView, self).get_context_data(**kwargs)
        context['object_list'] = self.object.word_set.all().order_by('position')
        context['fields'] = ['position', 'prefix', 'word']
        context['update'] = 'true'
        return context

class ExamDeleteView(customViews.CustomDeleteView):
    model = Exam


def createExamWords(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.word_set.all().delete()
    try:
        create_words(exam.evaluation_text.split(), exam.solution.split(), exam)
    except Exception as e:
        print("Error:", str(e))
        # Se eliminan las palabras creadas hasta el momento
        exam.word_set.all().delete()
        # Se muestra una pantalla de error
        return render(request, 'exams/create_word_error.html', context={'pk': pk})

    return redirect(APP_LABEL +  'exam_update', pk=pk)


def is_word(word):
    prev_2 = ''
    prev = ''
    for i in word:
        # Revisa que existan al menos dos caracteres seguidos _ o . y que el caracter anterior sea una letra
        if (i == '_' or i == '.') and i == prev and prev_2.isalpha():
            return True
        else:
            prev_2 = prev
            prev = i
    return False


# Obtiene la palabra limpia descartando caracteres antes y despues
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


def create_words(questions, solution, exam):
    valid_words = []
    for word in questions:
        if is_word(word):
            valid_words.append(word)

    count = -1
    for word in valid_words:
        # Obtengo la posicion de la palabra de la solucion
        count = find_word(word, solution, count + 1)
        solution_word = clean_word(solution[count])
        prefix = clean_word(word)
        # print("word:", word, 'clean:', clean_word(word), 'solution:', solution_word)
        Word(
            word=solution_word,
            prefix=prefix,
            exam=exam,
            position=count,
        ).save()


# Encuentra la palabra que corresponde con el prefijo y devuelve su posicion
def find_word(word, solution, initial_pos):
    # Limpio la palabra para obtener el prefijo
    prefix = clean_word(word)
    # Recorro el vector de palabras de la solucion
    for pos in range(initial_pos, len(solution)):
        # Obtengo la palabra completa sin simbolos
        sol_word = clean_word(solution[pos])
        correct_word = False
        # Recorro el prefijo comparandolo letra a letra con la palabra
        if len(sol_word) > len(prefix):
            for i in range(len(prefix)):
                if prefix[i] == sol_word[i]:
                    correct_word = True
                else:
                    correct_word = False
                    break
        # Si todas las letras coincidieron devuelvo la posicion de la palabra de la solucion
        if correct_word:
            return pos
    # Si no se encontro la palabra devuelvo false para provocar un error
    return False