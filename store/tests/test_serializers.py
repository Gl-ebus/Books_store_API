from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
	def test_serializers(self):
		b1 = Book.objects.create(name='TestBook1', price=25.00,
		                         author='Author 1')
		b2 = Book.objects.create(name='TestBook2', price=19.00,
		                         author='Author 2')
		data = BooksSerializer([b1, b2], many=True).data

		expected_data = [
			{'id': b1.id, 'name': 'TestBook1',
			 'price': '25.00', 'author': 'Author 1'},
			{'id': b2.id, 'name': 'TestBook2',
			 'price': '19.00', 'author': 'Author 2'}
		]

		self.assertEqual(expected_data, data)