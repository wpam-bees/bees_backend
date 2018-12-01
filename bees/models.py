from django.contrib.auth.models import User
from django.contrib.gis.db import models


class SoftDeleteModel(models.Model):
    class SoftDeleteQuerySet(models.QuerySet):
        def delete(self):
            self.update(is_deleted=True)

    class SoftDeleteManager(models.Manager):
        def get_queryset(self):
            return SoftDeleteModel.SoftDeleteQuerySet(self.model).filter(is_deleted=False)

    objects = SoftDeleteManager()
    base_objects = models.Manager()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Bee(models.Model):
    current_location = models.PointField(null=True)

    class Meta:
        abstract = True


class WorkerBee(Bee):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='worker_bee',
    )
    filters = models.OneToOneField(
        'JobFilter',
        on_delete=models.CASCADE,
        related_name='worker'
    )


class EmployerBee(Bee):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employer_bee',
    )
    credit_card = models.OneToOneField(
        'CreditCardData',
        on_delete=models.CASCADE,
        related_name='employer'
    )


class CreditCardData(models.Model):
    number = models.CharField(
        max_length=19,
        blank=True,
        default='',
    )
    exp_date = models.CharField(
        max_length=5,
        blank=True,
        default='',
    )
    cvv = models.CharField(
        max_length=3,
        blank=True,
        default='',
    )


class Job(models.Model):
    principal = models.OneToOneField(  # TODO: Rename?
        'EmployerBee',
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.PointField(null=True)
    initial_fee = models.DecimalField(
        max_digits=9,
        decimal_places=2,
    )


class Offer(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
    )
    bidder = models.ForeignKey(
        WorkerBee,
        null=True,
        on_delete=models.SET_NULL,
    )
    value = models.DecimalField(
        max_digits=9,
        decimal_places=2,
    )
    accepted = models.BooleanField(
        default=False,
    )


class Category(models.Model):
    name = models.CharField(max_length=100)


class JobFilter(models.Model):
    categories = models.ManyToManyField(
        Category,
        related_name='interests',
    )
    range = models.PositiveIntegerField(default=20)
    min_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0.0,
    )
