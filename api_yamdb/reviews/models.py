from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year_to_current

User = get_user_model()


class Category(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        verbose_name='Уникальное имя категории',
        unique=True,
    )


class Genre(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        verbose_name='Уникальное имя жанра',
        unique=True,
    )


class Title(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория произведения',
        related_name='titles',
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        null=True,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год создания',
        validators=(validate_year_to_current,)
    )
    genre = models.ManyToManyField(
        to=Genre,
        blank=True,
        related_name='title_genres',
    )


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        verbose_name="Отзыв",
        help_text='Напишите текст вашего отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата',
        help_text='Укажите дату публикции',
        auto_now_add=True,
        db_index=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='Укажите автора отзыва',
        verbose_name='Автор',
        related_name='reviews',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_title_author'
            ),
        )


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name="Комментарий",
        help_text='Напишите ваш комментарий к посту',
        max_length=2500,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата',
        help_text='Укажите дату публикции',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
