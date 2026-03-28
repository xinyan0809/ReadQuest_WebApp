from django.contrib import admin
from readquest.models import *

class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'earners')

class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author', 'pages', 'blurb')

class DetailsAdmin(admin.ModelAdmin):
    list_display = ('book', 'ratings', 'rating_average')
    prepopulated_fields = {'slug':('book.title',)}

admin.site.register(Userpage)
admin.site.register(Achievement)# AchievementAdmin)
admin.site.register(Book)# BookAdmin)
admin.site.register(ProgressRecord)

