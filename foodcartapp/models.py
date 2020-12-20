from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


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
    def create(self, firstname, lastname, address, phonenumber, products):
        order = super().create(firstname=firstname, lastname=lastname, address=address, phonenumber=phonenumber)
        order_item = [OrderItem(order=order, price=fields['product'].price, **fields) for fields in products]
        OrderItem.objects.bulk_create(order_item)
        return order


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'необработанный'),
        ('processed', 'обработанный')
    ]

    PAYMENT_TYPE = [
        ('electronic', 'электронно'),
        ('cash', 'наличными')
    ]

    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50, blank=True)
    address = models.CharField('адрес доставки', max_length=100)
    phonenumber = PhoneNumberField('телефон', null=False, blank=False)
    status = models.CharField('статус заказа', max_length=10, default='pending', choices=STATUS_CHOICES, db_index=True)
    comment = models.TextField('комментарий к заказу', blank=True)
    registration_date = models.DateTimeField('дата регистарции', default=timezone.now, db_index=True)
    call_date = models.DateTimeField('дата звонка', blank=True, null=True)
    deliver_date = models.DateTimeField('дата доставки', blank=True, null=True)
    payment_type = models.CharField('вид оплаты', max_length=10, default='electronic', choices=PAYMENT_TYPE,
                                    db_index=True)
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='orders', verbose_name='ресторан')
    objects = OrderManager()

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


def validate_quantity(value):
    if value <= 0:
        raise ValidationError(
            "количество не может быть равно нулю или быть отрицательным числом",
            params={'value': value},
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products', verbose_name='заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products', verbose_name='товар')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, null=True)
    quantity = models.IntegerField('количество', validators=[validate_quantity])

    def __str__(self):
        return f"{self.order.firstname} {self.order.lastname} {self.order.address}"

    class Meta:
        verbose_name = 'состав заказа'
        verbose_name_plural = 'состав заказа'

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super(OrderItem, self).save(*args, **kwargs)
