from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('author', 'Author'), ('collaborator', 'Collaborator')],
                            default='-')

    def __str__(self):
        return self.user.username


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='collaborations', through='Collaboration')

    def __str__(self):
        return self.title


class Section(models.Model):
    title = models.CharField(max_length=255)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    parent_section = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Subsection(models.Model):
    title = models.CharField(max_length=255)
    parent_section = models.ForeignKey('Section', on_delete=models.CASCADE, related_name='subsections')


class Collaboration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('Author', 'Author'), ('Collaborator', 'Collaborator')],
                            default='-')
    can_edit = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
