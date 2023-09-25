from django.urls import path

from . import views

urlpatterns = [
    path('api/login', views.UserLoginView.as_view(), name='login'),
    path('api/signup', views.UserRegistrationView.as_view(), name='signup'),
    path('api/logout', views.UserLogoutView.as_view(), name='logout'),

    path('api/books/', views.BookListView.as_view(), name='book-list'),
    path('api/books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),

    path('api/sections/', views.SectionListView.as_view(), name='section-list'),
    path('api/sections/<int:pk>/', views.SectionDetailView.as_view(), name='section-detail'),

    path('api/subsections/', views.SubsectionListView.as_view(), name='subsection-list'),
    path('api/subsections/<int:pk>/', views.SubsectionDetailView.as_view(), name='subsection-detail'),

    path('api/collaborations/', views.CollaborationListView.as_view(), name='collaboration-list'),
    path('api/collaborations/<int:pk>/', views.CollaborationDetailView.as_view(), name='collaboration-detail'),

    path('api/grant-access/', views.GrantCollaborationAccessView.as_view(),
         name='grant-collaboration-access'),
    path('api/revoke-access/', views.RevokeCollaborationAccessView.as_view(),
         name='revoke-collaboration-access'),
]
