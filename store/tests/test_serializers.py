from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
	def test_serializers(self):
		user = User.objects.create(username='test_user')
		b1 = Book.objects.create(name='TestBook1', price=25.00,
		                         author='Author 1', owner=user)
		b2 = Book.objects.create(name='TestBook2', price=19.00,
		                         author='Author 2', owner=user)
		data = BooksSerializer([b1, b2], many=True).data

		expected_data = [
			{'id': b1.id, 'name': 'TestBook1',
			 'price': '25.00', 'author': 'Author 1',
			 'owner': user.id, 'readers': []},
			{'id': b2.id, 'name': 'TestBook2',
			 'price': '19.00', 'author': 'Author 2',
			 'owner': user.id, 'readers': []}
		]

		self.assertEqual(expected_data, data)