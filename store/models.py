from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Book(models.Model):
	name = models.CharField(max_length=255)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	author = models.CharField(max_length=255)
	owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return f'{self.id}: {self.name}, {self.author}, price: {self.price}'