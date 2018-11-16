from rest_framework import viewsets, serializers, permissions

from bees.models import WorkerBee


class WorkerBeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkerBee
        fields = '__all__'


class WorkerBeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkerBee.objects.all()
    serializer_class = WorkerBeeSerializer
    permission_classes = (permissions.IsAuthenticated,)
