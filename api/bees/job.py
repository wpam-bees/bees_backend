from django.contrib.gis import measure, geos
from django.contrib.gis.db.models import functions
from django.db.models import Q, F
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from bees.models import Job


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
    distance = serializers.SerializerMethodField()

    @staticmethod
    def get_distance(obj):
        if obj.distance is not None:
            return obj.distance.km
        return None

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('distance', )


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = self.queryset
        serializer = LocationSerializer(data=self.request.query_params)  # TODO: Send it in headers?

        serializer.is_valid(raise_exception=True)
        user_location = serializer.save()
        queryset = queryset.annotate(
            distance=functions.Distance('location', user_location),
        ).order_by(
            F('distance').asc(nulls_first=True),
        )

        return queryset

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        radius = request.query_params.get('radius')
        queryset = self.filter_queryset(self.get_queryset())

        if not radius:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(
            Q(location__isnull=True) | Q(distance__lte=(measure.Distance(m=radius))),
        )
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

