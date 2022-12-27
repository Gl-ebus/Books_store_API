from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer


# pip install django-filter
# filter_backend можно устновить для всего проекта в settings


class BookViewSet(ModelViewSet):
	queryset = Book.objects.all()
	serializer_class = BooksSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	permission_classes = [IsOwnerOrStaffOrReadOnly]
	filterset_fields = ['price']
	search_fields = ['name', 'author']
	ordering_fields = ['price', 'author']

	def perform_create(self, serializer):
		serializer.validated_data['owner'] = self.request.user
		serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
	permission_classes = [IsAuthenticated]
	queryset = UserBookRelation.objects.all()
	serializer_class = UserBookRelationSerializer
	lookup_field = 'book'

	def get_object(self):
		obj, created = UserBookRelation.objects.get_or_create(
			user=self.request.user,
			book_id=self.kwargs['book'])
		return obj

