from django.db import models

# Create your models here.


class Exam(models.Model):
    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Examenes'

    title = models.CharField(u'Título', max_length=256)
    solution = models.TextField(u'Solución')
    evaluation_text = models.TextField(u'Texto de evaluación')
    LEVEL_CHOICES = (('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'))
    level = models.CharField(u'Nivel', max_length=2, choices=LEVEL_CHOICES ,default=LEVEL_CHOICES[0][0])
    valid = models.BooleanField(u'Examen valido', default=True)

    def __str__(self):
        return self.title


class Word(models.Model):
    class Meta:
        verbose_name = 'Palabra'
        verbose_name_plural = 'Palabras'

    word = models.CharField(u'Palabra', max_length=10)
    prefix = models.CharField(u'Prefijo', max_length=30)
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE, verbose_name='Examen')
    position = models.IntegerField(u'Posición')

    def __str__(self):
        return str(self.word) + ', ' + str(self.position)

    def answer(self):
        return self.word[len(str(self.prefix)):]

    def correct(self, answer):
        return answer == self.answer()
