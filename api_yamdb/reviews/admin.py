from django.contrib import admin
from reviews.models import Category, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    list_filter = ('name', 'slug',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    list_filter = ('name', 'slug',)
