import json

from django.contrib.gis import measure, geos
from django.contrib.gis.db.models import functions
from django.db import transaction
from django.db.models import Q, F
from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_filters import rest_framework as filters

from bees.models import Job, Offer


class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()

    def create(self, validated_data):
        return geos.Point(
            validated_data.get('lat'),
            validated_data.get('lon'),
            srid=4326,
        )

    def update(self, instance, validated_data):
        return self.create(validated_data)


class JobSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField(read_only=True)
    active = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    @staticmethod
    def get_distance(obj):
        if hasattr(obj, 'distance') and obj.distance is not None:
            return obj.distance.km
        return None

    @staticmethod
    def get_status(obj):
        if obj.finished:
            return 'Finished'
        if obj.marked_finished:
            return 'Marked finished'
        if obj.is_accepted:
            return 'Progress'
        return 'Awaiting for worker'

    def get_active(self, obj):
        request = self.context['request']
        offer = Offer.objects.filter(
            job=obj,
            accepted=True,
        ).first()
        if not offer:
            return True
        return offer.bidder != request.user.worker_bee

    class Meta:
        model = Job
        fields = '__all__'


class JobFilter(filters.FilterSet):
    offers__isnull = filters.BooleanFilter(field_name='offers', lookup_expr='isnull')

    class Meta:
        model = Job
        fields = ('category', 'principal', 'offers__isnull', 'finished')


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = JobFilter

    def get_queryset(self):
        queryset = self.queryset
        location = self.request.META.get('HTTP_GEOLOCATION')
        if location:
            serializer = LocationSerializer(data=json.loads(location))

            serializer.is_valid(raise_exception=True)
            user_location = serializer.save()
            queryset = queryset.annotate(
                distance=functions.Distance('location', user_location),
            ).order_by(
                F('distance').asc(nulls_first=True),
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(principal=self.request.user.employer_bee)

    def perform_destroy(self, instance):
        has_offer = Offer.objects.filter(
            job=instance,
            accepted=True,
        ).exists()
        if instance.finished or has_offer:
            raise ValidationError('Accepted and finished jobs cannot be removed')
        instance.delete()

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        queryset = self.filter_queryset(self.get_queryset()).available()
        filters = request.user.worker_bee.filters
        queryset = filters.apply(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def active(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = request.user.worker_bee.active_jobs(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    @transaction.atomic
    def accept(self, request, *args, **kwargs):
        job = self.get_object()
        if job.is_accepted:
            raise ValidationError({'non_field_errors': 'This offer is already accepted'})
        job = job.accept(request.user.worker_bee)
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def finish(self, request, *args, **kwargs):
        job = self.get_object()
        accepted_offer = job.offers.get(accepted=True)
        if accepted_offer.bidder != request.user.worker_bee:
            raise ValidationError({'non_field_errors': 'You cannot finish job that isn\'t yours'})
        accepted_offer.finish()
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def accept_finished(self, request, *args, **kwargs):
        job = self.get_object()
        if job.principal != request.user.employer_bee:
            raise ValidationError({'non_field_errors': 'You cannot finish job that isn\'t yours'})
        job.finish()
        serializer = self.get_serializer(job)
        return Response(serializer.data)
