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

# Decoratos
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .decorators import staff_user_required


# Create your views here.
APP_NAME = 'exams'
APP_LABEL = 'exams:'


@method_decorator(login_required, name='dispatch')
class ExamListView(views.CustomListView):
    model = Exam
    fields = ['title', 'level']

    def get_queryset(self):
        if self.request.user.is_staff:
            self.fields = ['title', 'level', 'valid']
            return self.model.objects.all().order_by('level').order_by('title')
        else:
            return self.model.objects.filter(valid=True).order_by('level').order_by('title')


@method_decorator(staff_user_required, name='dispatch')
class ExamCreateView(views.CustomCreateView):
    model = Exam
    form_class = ExamForm
    success_url = reverse_lazy(APP_LABEL + 'exam_list')

    def form_valid(self, form):
        super(ExamCreateView, self).form_valid(form)
        return redirect(APP_LABEL + 'words_create', pk=self.object.pk)


@method_decorator(staff_user_required, name='dispatch')
class ExamUpdateView(generic.UpdateView):
    model = Exam
    form_class = ExamForm
    success_url = reverse_lazy(APP_LABEL  + 'exam_list')
    template_name = 'custom/update_form.html'

    def get_context_data(self, **kwargs):
        context = super(ExamUpdateView, self).get_context_data(**kwargs)
        context['object_list'] = self.object.word_set.all().order_by('position')
        context['fields'] = ['position', 'prefix', 'word']
        context['update'] = 'true'
        context['object'] = self.object
        return context

    def form_valid(self, form):
        super(ExamUpdateView, self).form_valid(form)
        return createExamWords(self.request, pk=self.object.pk)


@method_decorator(staff_user_required, name='dispatch')
class ExamDeleteView(views.CustomDeleteView):
    model = Exam


@staff_user_required
def createExamWords(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.word_set.all().delete()

    try:
        create_words(exam.evaluation_text.replace('\\n', ' ').replace('\\r', ' ').split(), exam.solution.replace('\\n', ' ').replace('\\r', ' ').split(), exam)
    except Exception as e:
        print("Error:", str(e))
        # Se marca el examen como invalido para que se lo corrija
        exam.valid = False
        exam.save()
        # Se muestra una pantalla de error
        return render(request, 'exams/create_word_error.html', context={'pk': pk})
    # Se marca el examen como valido para que sea visible por los estudiantes
    exam.valid = True
    exam.save()
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
                if questions[word.position - 1] == solution[pos - 1] \
                        or questions[word.position + 1] == solution[pos + 1]:
                    return pos
    # Si no se encontro la palabra devuelvo false para provocar un error
    print("word:----------------- ", prefix)
    return None


@method_decorator(login_required, name='dispatch')
class ExamView(views.MultipleModelUpdateView):
    model = Exam
    child_model = Word
    form_class = ExamForm
    child_form_class = QuestionWordForm
    template_name = APP_NAME + '/exam.html'

    def get_exam_data(self, formset, correct_answers=None):
        text = self.object.evaluation_text.replace('\\n', ' ').replace('\\r', ' ').replace('  ', ' ').split(' ')
        # print(text)
        words = self.object.word_set.all().order_by('position')
        # Incluyo cada uno de los objetos palabras remplazando al texto de la palabra incompleta
        count = -1
        for word in words:
            count += 1
            form = formset[count]
            text[word.position] = {'form' : form, 'prefix' : word.prefix }
            if correct_answers:
                # Si existen se agregan las respuestas correctas
                text[word.position]['correct_answer'] = correct_answers[count]
        return text

    def get_context_data(self, success_msg=None, form=None, formset=None, correct_answers=None, score=None, **kwargs):
        context = super(ExamView, self).get_context_data(success_msg, form, formset, **kwargs)
        if formset:
            context['formset'] = formset
        else:
            formset = inlineformset_factory(self.model, self.child_model, form=self.child_form_class, extra=self.object.word_set.all().count(), max_num=self.object.word_set.all().count())(instance=self.object)
            context['formset'] = formset
        if correct_answers: context['correct_answers'] = True
        if score is not None:
            context['score'] = score
            context['porcent'] = round((score / len(formset))*100, 2)
        context['exam_text'] = self.get_exam_data(formset, correct_answers)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = self.get_context_data()
        form = data['form']
        formset = data['formset']
        formset = inlineformset_factory(self.model, self.child_model, form=self.child_form_class,
                                        extra=self.object.word_set.all().count(),
                                        max_num=self.object.word_set.all().count())(self.request.POST, instance=self.object)
        if formset.is_valid():
          return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        words = self.object.word_set.all().order_by('position')
        score = 0
        correct_answers = []
        for pos in range(len(formset)):
            # Marco los casilleros como solo lectura
            formset[pos].fields['answer'].widget.attrs['readonly'] = True
            # if words[pos].correct(self.request.POST.get('word_set-' + str(pos) +'-answer')):
            if words[pos].correct(formset[pos].cleaned_data['answer']):
                score += 1
                correct_answers.append(None)
            else:
                correct_answers.append(words[pos].word)
        return render(self.request, self.template_name, self.get_context_data(formset=formset, correct_answers=correct_answers, score=score))

