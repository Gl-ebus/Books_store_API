from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
	def test_serializers(self):
		user1 = User.objects.create(username='test_user1',
		                            first_name='Gosha', last_name='Petrov')
		user2 = User.objects.create(username='test_user2',
		                            first_name='Petya', last_name='Ivanov')
		user3 = User.objects.create(username='test_user3',
		                            first_name='Admin', last_name='Super')

		b1 = Book.objects.create(name='TestBook1', price=25.00,
		                         author='Author 1', owner=user1)
		b2 = Book.objects.create(name='TestBook2', price=19.00,
		                         author='Author 2')

		UserBookRelation.objects.create(user=user1, book=b1, like=True, rate=5)
		UserBookRelation.objects.create(user=user2, book=b1, like=True, rate=5)
		UserBookRelation.objects.create(user=user3, book=b1, like=True, rate=4)

		UserBookRelation.objects.create(user=user1, book=b2, like=True, rate=3)
		UserBookRelation.objects.create(user=user2, book=b2, like=False, rate=4)
		UserBookRelation.objects.create(user=user3, book=b2, like=True)

		books = Book.objects.annotate(
			likes_count=Count(Case(When(userbookrelation__like=True, then=1))),
			rating=Avg('userbookrelation__rate')
		).order_by('id')

		data = BooksSerializer(books, many=True).data
		expected_data = [
			{'id': b1.id, 'name': 'TestBook1',
			 'price': '25.00', 'author': 'Author 1',
			 'likes_count': 3,
			 'rating': '4.67',
			 'owner_name': 'test_user1',
			 'readers': [
				 {
					 'first_name': 'Gosha',
					 'last_name': 'Petrov',
				 },
				 {
					 'first_name': 'Petya',
					 'last_name': 'Ivanov',
				 },
				 {
					 'first_name': 'Admin',
					 'last_name': 'Super',
				 },
			 ]
			 },
			{'id': b2.id, 'name': 'TestBook2',
			 'price': '19.00', 'author': 'Author 2',
			 'likes_count': 2,
			 'rating': '3.50',
			 'owner_name': '',
			 'readers': [
				 {
					 'first_name': 'Gosha',
					 'last_name': 'Petrov',
				 },
				 {
					 'first_name': 'Petya',
					 'last_name': 'Ivanov',
				 },
				 {
					 'first_name': 'Admin',
					 'last_name': 'Super',
				 },
			 ]
			 }
		]

		self.assertEqual(expected_data, data)