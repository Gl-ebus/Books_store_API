from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from store.models import Book
from store.serializers import BooksSerializer

# pip install django-filter
# filter_backend можно устновить для всего проекта в settings: django_filters.rest_framework


class BookViewSet(ModelViewSet):
	queryset = Book.objects.all()
	serializer_class = BooksSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	permission_classes = [IsAuthenticatedOrReadOnly]
	filterset_fields = ['price']
	search_fields = ['name', 'author']
	ordering_fields = ['price', 'author']
