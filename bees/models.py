from django.contrib.auth.models import User
from django.contrib.gis import measure
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.conf import settings


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
    balance = models.PositiveIntegerField(
        default=0,
    )

    def active_jobs(self, queryset=None):
        if not queryset:
            queryset = Job.objects.all()
        my_offers = Offer.objects.filter(
            bidder=self,
            accepted=True,
        )
        return queryset.exclude(finished=True)\
            .filter(offers__in=my_offers)


class EmployerBee(Bee):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employer_bee',
    )
    braintree_id = models.CharField(
        max_length=20,
        null=True,
    )
    # credit_card = models.OneToOneField(
    #     'CreditCardData',
    #     on_delete=models.CASCADE,
    #     related_name='employer'
    # )

    def create_braintree_client(self):
        resp = settings.gateway.customer.create({
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
        })
        if resp.is_success:
            self.braintree_id = resp.customer.id
        return resp


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


class JobQuerySet(models.QuerySet):
    def available(self):
        offers = Offer.objects.filter(accepted=True)
        return self.exclude(offers__in=offers).exclude(finished=True)


class Job(models.Model):
    objects = JobQuerySet.as_manager()

    principal = models.ForeignKey(  # TODO: Rename?
        'EmployerBee',
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.PointField(null=True)
    initial_fee = models.DecimalField(
        max_digits=9,
        decimal_places=2,
    )
    finished = models.BooleanField(default=False)

    @property
    def is_accepted(self):
        return Offer.objects.filter(
            job=self,
            accepted=True,
        ).exists()

    @property
    def marked_finished(self):
        return Offer.objects.filter(
            job=self,
            accepted=True,
            finished=True
        ).exists()

    @property
    def worker(self):
        offer = Offer.objects.filter(
            job=self,
            accepted=True,
        ).first()
        if offer is None:
            return None
        return offer.bidder

    def accept(self, worker):
        # Shortcut method of adding offer while bidding is not implemented
        Offer.objects.create(
            job=self,
            bidder=worker,
            value=self.initial_fee,
            accepted=True,
        )
        return self

    @transaction.atomic
    def finish(self):
        accepted_offer = Offer.objects.filter(
            job=self,
            accepted=True,
        ).first()
        if not accepted_offer.finished:
            raise ValidationError('Bee worker must finish job first')
        self.finished = True
        worker = self.worker
        worker.balance += self.initial_fee
        worker.save()
        self.save()
        return self


class Offer(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='offers',
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
    finished = models.BooleanField(
        default=False,
    )

    @transaction.atomic
    def finish(self):
        self.finished = True
        self.save()
        return self


class Category(models.Model):
    name = models.CharField(max_length=100)


class JobFilter(models.Model):
    categories = models.ManyToManyField(
        Category,
        related_name='interests',
    )
    radius = models.PositiveIntegerField(default=20)
    min_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0.0,
    )

    def apply(self, queryset):
        return queryset.filter(
            Q(location__isnull=True) | Q(distance__lte=(measure.Distance(km=self.radius))),
            initial_fee__gte=self.min_price,
            category__in=self.categories.all(),
        )
