from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):

	def setUp(self) -> None:
		# тестовый пользователь для проверки изменения данных в БД
		self.user = User.objects.create(username='test_user')
		self.url = reverse('book-list')

		self.b1 = Book.objects.create(name='TestBook1', price=25.00,
		                         author='Author 1', owner=self.user)
		self.b2 = Book.objects.create(name='TestBook2', price=19.00,
		                         author='Author 2', owner=self.user)
		self.b3 = Book.objects.create(name='TestBook 3', price=30.00,
		                         author='Author 1', owner=self.user)
		self.b4 = Book.objects.create(name='TestBook 4', price=22.00,
		                         author='Author 4', owner=self.user)


	def test_get(self):
		resp = self.client.get(self.url)
		serializer_data = BooksSerializer([self.b1, self.b2, self.b3, self.b4], many=True).data
		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.assertEqual( serializer_data, resp.data)

	def test_get_filter(self):
		resp = self.client.get(self.url, data={'price': 22})
		serializer_data = BooksSerializer([self.b4], many=True).data
		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.assertEqual( serializer_data, resp.data)

	def test_search(self):
		resp = self.client.get(self.url, data={'search': 'Author 1'})
		serializer_data = BooksSerializer([self.b1, self.b3], many=True).data
		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.assertEqual(serializer_data, resp.data)

	def test_ordering(self):
		resp = self.client.get(self.url, data={'ordering': '-price'})
		serializer_data = BooksSerializer([self.b3, self.b1, self.b4, self.b2], many=True).data
		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.assertEqual(serializer_data, resp.data)

	def test_create(self):
		self.client.force_login(self.user) # авторизиация пользователя
		data = {
			"name": "Programming in Python 3",
			"price": 920,
			"author": "Mark Summerfield"
		}
		json_data = json.dumps(data) # Преобразует словарь в объект JSON
		resp = self.client.post(self.url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
		self.assertEqual(5, Book.objects.count())
		self.assertEqual(self.user, Book.objects.last().owner)

	def test_update(self):
		self.client.force_login(self.user)  # авторизиация пользователя

		url = reverse('book-detail', args=(self.b1.id, ))
		data = {
			"name": self.b1.name,
			"price": 1500,
			"author": self.b1.author
		}
		json_data = json.dumps(data)
		resp = self.client.put(url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.b1.refresh_from_db() # Обновляет объект данными из БД
		self.assertEqual(1500, self.b1.price)

	def test_update_not_owner(self):
		user = User.objects.create(username='test_user_2')
		self.client.force_login(user)  # авторизиация пользователя

		url = reverse('book-detail', args=(self.b1.id, ))
		data = {
			"name": self.b1.name,
			"price": 1500,
			"author": self.b1.author,
			"owner": user.id
		}
		json_data = json.dumps(data)
		resp = self.client.put(url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_403_FORBIDDEN, resp.status_code)
		self.b1.refresh_from_db() # Обновляет объект данными из БД
		self.assertEqual(25, self.b1.price)

	def test_update_not_owner_but_staff(self):
		user = User.objects.create(username='test_user_2', is_staff=True)
		self.client.force_login(user)  # авторизиация пользователя

		url = reverse('book-detail', args=(self.b1.id, ))
		data = {
			"name": self.b1.name,
			"price": 1500,
			"author": self.b1.author,
			"owner": user.id
		}
		json_data = json.dumps(data)
		resp = self.client.put(url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.b1.refresh_from_db() # Обновляет объект данными из БД
		self.assertEqual(1500, self.b1.price)

	def test_delete(self):
		self.client.force_login(self.user)

		delete_id = self.b4.id
		url = reverse('book-detail', args=(delete_id, ))
		resp = self.client.delete(url, content_type='application/json')
		self.assertEqual(status.HTTP_204_NO_CONTENT, resp.status_code)
		self.assertEqual(3, Book.objects.count())
		resp_check_del = self.client.get(url)
		self.assertEqual(status.HTTP_404_NOT_FOUND, resp_check_del.status_code)

	def test_delete_not_owner(self):
		user = User.objects.create(username='test_user_2')
		self.client.force_login(user)  # авторизиация пользователя

		delete_id = self.b4.id
		url = reverse('book-detail', args=(delete_id, ))
		resp = self.client.delete(url, content_type='application/json')
		self.assertEqual(status.HTTP_403_FORBIDDEN, resp.status_code)
		self.assertEqual(4, Book.objects.count())


class BooksRalationTestCase(APITestCase):
	def setUp(self) -> None:
		# тестовые пользователи для проверки изменения данных в БД
		self.user = User.objects.create(username='test_user')
		self.client.force_login(self.user)
		self.user2 = User.objects.create(username='test_user_2')

		self.b1 = Book.objects.create(name='TestBook1', price=25.00,
		                         author='Author 1', owner=self.user)
		self.b2 = Book.objects.create(name='TestBook2', price=19.00,
		                         author='Author 2', owner=self.user)
		self.url = reverse('userbookrelation-detail', args=(self.b1.id,))

	def test_like_bookmarks(self):
		json_data = json.dumps( {"like": True} )  # Преобразует словарь в объект JSON
		resp = self.client.patch(self.url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.b1.refresh_from_db() # Обновляет объект данными из БД
		relation = UserBookRelation.objects.get(user=self.user,
		                                        book=self.b1)
		self.assertTrue(relation.like)

		# test 'in_bookmarks'
		json_data = json.dumps( {"in_bookmarks": True} )
		resp = self.client.patch(self.url, data=json_data,
		                         content_type='application/json')
		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.b1.refresh_from_db()  # Обновляет объект данными из БД
		relation = UserBookRelation.objects.get(user=self.user,
		                                        book=self.b1)
		self.assertTrue(relation.in_bookmarks)

	def test_rate(self):
		json_data = json.dumps( {"rate": 5} )

		resp = self.client.patch(self.url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_200_OK, resp.status_code)
		self.b1.refresh_from_db() # Обновляет объект данными из БД
		relation = UserBookRelation.objects.get(user=self.user,
		                                        book=self.b1)
		self.assertEqual(5, relation.rate)

	def test_rate_wrong(self):
		json_data = json.dumps( {"rate": 0 } )

		resp = self.client.patch(self.url, data=json_data,
		                        content_type='application/json')

		self.assertEqual(status.HTTP_400_BAD_REQUEST, resp.status_code, resp.data)
		self.b1.refresh_from_db() # Обновляет объект данными из БД
		relation = UserBookRelation.objects.get(user=self.user,
		                                        book=self.b1)
		self.assertEqual(None, relation.rate, resp.data)