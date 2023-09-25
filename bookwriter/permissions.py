from rest_framework.permissions import BasePermission

from .models import UserProfile


class IsAuthor(BasePermission):
    """
    Custom permission to allow only Authors to perform actions.
    """

    def has_permission(self, request, view):
        user = request.user
        user_role = UserProfile.objects.filter(user__id=user.id).first()
        return user.is_authenticated and (user_role.role == 'Author' or user_role.role == 'author')


class IsAuthorOrIsCollaborator(BasePermission):
    """
    Custom permission to allow only Authors or Collaborators to perform actions.
    """

    def has_permission(self, request, view):
        user = request.user
        user_role = UserProfile.objects.filter(user__id=user.id).first()
        return user.is_authenticated and (
                user_role.role == 'Author' or user_role.role == 'author' or user.role == "Collaborator" or user_role.role == 'collaborator')
