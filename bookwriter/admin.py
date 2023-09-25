from django.contrib import admin
from .models import Book, Section, Collaboration, UserProfile

admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(Section)
admin.site.register(Collaboration)
