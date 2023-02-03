from csv import DictReader
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

ALREDY_LOADED_ERROR_MESSAGE = """
Если вам нужно перезалить данные из файлов CSV в базу данных,
то сначала удалите файл db.sqlite3, затем выполните миграции
командой `python manage.py migrate` для создание новой пустой базы данных.
"""


def import_category(row):
    Category.objects.get_or_create(**row)


def import_genre(row):
    Genre.objects.get_or_create(**row)


def import_users(row):
    User.objects.get_or_create(**row)


def import_titles(row):
    Title.objects.get_or_create(
        name=row['name'],
        year=row['year'],
        category_id=row['category']
    )


def import_genre_title(row):
    title = Title.objects.get(id=row['title_id'])
    title.genre.add(Genre.objects.get(id=row['genre_id']))


def import_reviews(row):
    Review.objects.get_or_create(
        title_id=row['title_id'],
        text=row['text'],
        author_id=row['author'],
        score=row['score'],
        pub_date=row['pub_date'],
    )


def import_comments(row):
    Comment.objects.get_or_create(
        review_id=row['review_id'],
        text=row['text'],
        author=User.objects.get(id=row['author']),
        pub_date=row['pub_date'],
    )


DATA_CSV = {
    import_category: 'static/data/category.csv',
    import_genre: 'static/data/genre.csv',
    import_users: 'static/data/users.csv',
    import_titles: 'static/data/titles.csv',
    import_genre_title: 'static/data/genre_title.csv',
    import_reviews: 'static/data/review.csv',
    import_comments: 'static/data/comments.csv'
}


class Command(BaseCommand):
    help = "Загрузка данных в базу данных из таблиц CSV"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(("Загружаем данные в базу..."))
        )
        for method, file_path in DATA_CSV.items():
            for row in DictReader(open(f'{settings.BASE_DIR}/{file_path}',
                                  encoding='utf-8')):
                method(row)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Файл {file_path} успешно импортирован"
                )
            )
