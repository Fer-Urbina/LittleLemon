from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, default='Default Title')

    def __str__(self)-> str:
        return self.title

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('menuitem', 'user')
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)

    STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Delivered', 'Delivered'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateField(db_index=True, default=timezone.now)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, default=1)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=2)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=2)

    class Meta:
        unique_together = ('order', 'menuitem')
