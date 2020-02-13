from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

# Views
from custom import views
from django.views import generic

from django.forms.models import inlineformset_factory

# Forms
from .forms import ExamForm, QuestionWordForm

# Models
from .models import Exam, Word

# Create your views here.
APP_NAME = 'exams'
APP_LABEL = 'exams:'


class ExamListView(views.CustomListView):
    model = Exam
    fields = ['title']

    def get_queryset(self):
        return self.model.objects.all().order_by('title')

class ExamCreateView(views.CustomCreateView):
    model = Exam
    form_class = ExamForm
    success_url = reverse_lazy(APP_LABEL + 'exam_list')

    def form_valid(self, form):
        super(ExamCreateView, self).form_valid(form)
        return redirect(APP_LABEL + 'words_create', pk=self.object.pk)


class ExamUpdateView(views.CustomUpdateView):
    model = Exam
    form_class = ExamForm

    def get_context_data(self, **kwargs):
        context = super(ExamUpdateView, self).get_context_data(**kwargs)
        context['object_list'] = self.object.word_set.all().order_by('position')
        context['fields'] = ['position', 'prefix', 'word']
        context['update'] = 'true'
        return context

class ExamDeleteView(views.CustomDeleteView):
    model = Exam


def createExamWords(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.word_set.all().delete()

    try:
        create_words(exam.evaluation_text.replace('\\n', ' ').replace('\\r', ' ').split(), exam.solution.replace('\\n', ' ').replace('\\r', ' ').split(), exam)
    except Exception as e:
        print("Error:", str(e))
        # Se eliminan las palabras creadas hasta el momento
        exam.word_set.all().delete()
        # Se muestra una pantalla de error
        return render(request, 'exams/create_word_error.html', context={'pk': pk})

    return redirect(APP_LABEL +  'exam_update', pk=pk)


def is_question_word(word):
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


# def create_words(questions, solution, exam):
#     valid_words = []
#     for word in questions:
#         if is_word(word):
#             valid_words.append(word)
#
#     count = -1
#     for word in valid_words:
#         # Obtengo la posicion de la palabra de la solucion
#         count = find_word(word, solution, count + 1)
#         solution_word = clean_word(solution[count])
#         prefix = clean_word(word)
#         # print("word:", word, 'clean:', clean_word(word), 'solution:', solution_word)
#         Word(
#             word=solution_word,
#             prefix=prefix,
#             exam=exam,
#             position=count,
#         ).save()


def create_words(questions, solution, exam):
    # print("questions", questions)
    # print("solution", solution)

    valid_words = []
    pos = -1
    for word in questions:
        pos += 1
        # Obtiene las palabras incompletas y las guarda junto con su posicion
        if is_question_word(word):
            valid_words.append(Word(prefix=clean_word(word), position=pos, exam=exam))

    count = -1
    # Recorro las palabras incompletas
    for word in valid_words:
        # Obtengo la posicion de la palabra de la solucion
        count = find_word(word, questions, solution, count + 1)
        solution_word = clean_word(solution[count])
        # print("word:", word, 'clean:', clean_word(word), 'solution:', solution_word)
        word.word = solution_word
        word.save()


class WordNotInSolution():
    pass

# Encuentra la palabra que corresponde con el prefijo y devuelve su posicion
def find_word(word, questions, solution, initial_pos):
    # Limpio la palabra para obtener el prefijo
    prefix = word.prefix
    # Recorro el vector de palabras de la solucion
    for pos in range(initial_pos, len(solution)):
        # Obtengo la palabra completa sin simbolos
        sol_word = clean_word(solution[pos])
        correct_word = False
        # Compruebo que la solucion sea mas grande que el prefijo
        if len(sol_word) > len(prefix):
            # Compruebo que el prefijo sea igual a la primera parte de la solucion
            if prefix == sol_word[0:len(prefix)]:
                # Compruebo que las palabras alrededor de la palabra incompleta coinciden con las palabras
                # alrededor de la palabras de la solucion permitiendo un error de uno de los lados
                if questions[word.position - 2 : word.position - 1] == solution[pos - 2 : pos - 1] \
                        or questions[word.position + 1 : word.position + 2] == solution[pos + 1 : pos + 2]:
                    return pos
    # Si no se encontro la palabra devuelvo false para provocar un error
    print("word:----------------- ", word)
    return None


# # Examen
# class ExamView(generic.FormView):
#     model = Exam
#     form_class = QuestionWordForm
#     template_name = APP_NAME + '/exam.html'
#
#     def get_exam_data(self):
#         inlineformset_factory(self.model, self.child_model, form=self.child_form_class, extra=self.child_size, max_num=self.child_size)
#         text = self.object.evaluation_text.split(' ')
#         words = self.object.word_set.all()
#         for word in words:
#             text[word.position] = self.form_class(instance=word)
#         return text
#
#     def get_context_data(self, **kwargs):
#         context = super(ExamView, self).get_context_data(**kwargs)
#         context['exam_text'] = get_exam_data()


class ExamView(views.MultipleModelUpdateView):
    model = Exam
    child_model = Word
    form_class = ExamForm
    child_form_class = QuestionWordForm
    template_name = APP_NAME + '/exam.html'

    def get_exam_data(self, formset):
        text = self.object.evaluation_text.replace('\\n', ' ').replace('\\r', ' ').replace('  ', ' ').split(' ')
        print(text)
        words = self.object.word_set.all()
        # Incluyo cada uno de los objetos palabras remplazando al texto de la palabra incompleta
        count = -1
        for word in words:
            count += 1
            form = formset[count]
            text[word.position] = {'form' : form, 'prefix' : word.prefix}
        return text

    def get_context_data(self, success_msg=None, form=None, formset=None, **kwargs):
        context = super(ExamView, self).get_context_data(success_msg, form, formset, **kwargs)
        formset = inlineformset_factory(self.model, self.child_model, form=self.child_form_class, extra=self.object.word_set.all().count(), max_num=self.object.word_set.all().count())(instance=self.object)
        context['formset'] = formset
        context['exam_text'] = self.get_exam_data(formset)
        return context
