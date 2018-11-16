from rest_framework import viewsets, serializers, permissions

from bees.models import EmployerBee


class EmployerBeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployerBee
        fields = '__all__'


class EmployerBeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmployerBee.objects.all()
    serializer_class = EmployerBeeSerializer
    permission_classes = (permissions.IsAuthenticated,)
