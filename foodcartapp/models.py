from django.db import models, transaction


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderManager(models.Manager):
    @transaction.atomic
    def create(self, firstname, lastname, address, phonenumber, products=False):
        order = Order(firstname=firstname, lastname=lastname, address=address, phonenumber=phonenumber)
        order.save()
        order_item = [OrderItem(order=order, price=0, **fields) for fields in products]
        OrderItem.objects.bulk_create(order_item)
        for item in OrderItem.objects.filter(order=order):
            item.price = item.product.price
            item.save(update_fields=['price'])
        return order


class Order(models.Model):
    STATUS = [
        ('0', 'необработанный'),
        ('1', 'обработанный')
    ]

    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50, blank=True)
    address = models.CharField('адрес доставки', max_length=100)
    phonenumber = models.CharField('телефон', max_length=12)
    status = models.CharField(max_length=1, default='необработанный', choices=STATUS)
    objects = OrderManager()

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products', verbose_name='заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products', verbose_name='товар')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    quantity = models.IntegerField('количество')

    def __str__(self):
        return f"{self.order.firstname} {self.order.lastname} {self.order.address}"

    class Meta:
        verbose_name = 'состав заказа'
        verbose_name_plural = 'состав заказа'

    def save(self, *args, **kwargs):
        self.price = self.product.price
        super(OrderItem, self).save(*args, **kwargs)
