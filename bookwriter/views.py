from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, Section, Collaboration, Subsection, UserProfile
from .permissions import IsAuthor, IsAuthorOrIsCollaborator
from .serializers import UserProfileSerializer, UserLoginSerializer, BookSerializer, SectionSerializer, \
    CollaborationSerializer, SubsectionSerializer


class UserRegistrationView(CreateAPIView):
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['user']['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['user']['email']
        role = serializer.validated_data['role']

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        user_profile = UserProfile.objects.create(user=user, role=role)

        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user_profile.role
        }

        return Response({'success': 'User created successfully.', 'response': response_data},
                        status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        user = authenticate(username=username, password=password, email=email)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response_data = {
                'id': user.id,
                'email': user.email,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
            return Response({'detail': 'Login successful.', 'response': response_data})
        else:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    serializer_class = UserProfileSerializer

    def post(self, request):
        logout(request)
        return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)


class BookListView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectionListView(ListCreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def perform_create(self, serializer):
        book_id = self.request.data.get('book')
        parent_section_id = self.request.data.get('parent_section_id')
        book = Book.objects.get(id=book_id)
        parent_section = None

        if parent_section_id:
            parent_section = Section.objects.get(id=parent_section_id)

        serializer.save(book=book, parent_section=parent_section)


class SectionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrIsCollaborator]


class SubsectionListView(ListCreateAPIView):
    queryset = Subsection.objects.all()
    serializer_class = SubsectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubsectionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Subsection.objects.all()
    serializer_class = SubsectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class CollaborationListView(ListCreateAPIView):
    queryset = Collaboration.objects.all()
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CollaborationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Collaboration.objects.all()
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]


class GrantCollaborationAccessView(UpdateAPIView):
    queryset = Collaboration.objects.all()
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def update(self, request, *args, **kwargs):
        collaborator_id = request.data.get('collaborator_id')

        try:
            collaboration = Collaboration.objects.get(id=collaborator_id)
        except Collaboration.DoesNotExist:
            return Response({'message': 'Collaboration not found'}, status=status.HTTP_404_NOT_FOUND)

        collaboration.can_edit = True
        collaboration.save()
        return Response({'message': 'Access granted successfully'}, status=status.HTTP_200_OK)


class RevokeCollaborationAccessView(UpdateAPIView):
    queryset = Collaboration.objects.all()
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def update(self, request, *args, **kwargs):
        collaborator_id = request.data.get('collaborator_id')

        try:
            collaboration = Collaboration.objects.get(id=collaborator_id)
        except Collaboration.DoesNotExist:
            return Response({'message': 'Collaboration not found'}, status=status.HTTP_404_NOT_FOUND)

        collaboration.can_edit = False
        collaboration.save()
        return Response({'message': 'Access revoked successfully'}, status=status.HTTP_200_OK)
