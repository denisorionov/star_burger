from django.db import models


class Banner(models.Model):
    STATUS_CHOICES = [
        ('show', 'отображать'),
        ('not_show', 'не отображать')
    ]

    title = models.CharField('название', max_length=50)
    src = models.ImageField('баннер', upload_to='banners')
    text = models.CharField('текст', max_length=50)
    status = models.CharField('статус показа', max_length=10, default='show', choices=STATUS_CHOICES, db_index=True)
    order = models.PositiveIntegerField('порядок', default=0, blank=False, null=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'
        ordering = ['order']
