from django.db import models

# Create your models here.


class Exam(models.Model):
    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Examenes'

    title = models.CharField(u'Título', max_length=256)
    solution = models.TextField(u'Solución')
    evaluation_text = models.TextField(u'Texto de evaluación')

    def __str__(self):
        return self.title


class Word(models.Model):
    class Meta:
        verbose_name = 'Palabra'
        verbose_name_plural = 'Palabras'

    word = models.CharField(u'Palabra', max_length=10)
    prefix = models.CharField(u'Prefijo', max_length=30)
    solution = models.CharField(u'Solución', max_length=10)
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE, verbose_name='Examen')

    def __str__(self):
        return self.word
