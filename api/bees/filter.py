from decimal import Decimal
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated

from bees.models import JobFilter


class JobFilterSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        try:
            radius = int(data.get('radius'))
        except ValueError:
            raise serializers.ValidationError({
                'radius': 'This field must be parsable to number',
            })
        try:
            min_price = float(data.get('minPrice'))
        except ValueError:
            raise serializers.ValidationError({
                'min_price': 'This field must be parsable to number',
            })
        return {
            'radius': radius,
            'min_price': min_price,
        }

    def to_representation(self, instance):
        return {
            'radius': str(instance.radius),
            'min_price': str(Decimal(instance.min_price).quantize(Decimal('0.01'))),
        }

    class Meta:
        model = JobFilter
        fields = ('min_price', 'radius')


class FiltersView(generics.RetrieveUpdateAPIView):
    serializer_class = JobFilterSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.worker_bee.filters
