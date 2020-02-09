from django.urls import path
from .views import \
    ExamListView, ExamCreateView, ExamUpdateView, ExamDeleteView, createExamWords
app_name = 'exams'

urlpatterns = [
    # Exams
    path('exam/', ExamListView.as_view(), name='exam_list'),
    path('exam/create', ExamCreateView.as_view(), name='exam_create'),
    path('exam/change/<int:pk>', ExamUpdateView.as_view(), name='exam_update'),
    path('exam/delete/<int:pk>', ExamDeleteView.as_view(), name='exam_delete'),
    path('words/create/<int:pk>', createExamWords, name='words_create'),

]