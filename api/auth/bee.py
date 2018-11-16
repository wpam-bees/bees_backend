from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, generics, permissions, status
from rest_framework.response import Response

from bees.models import WorkerBee, EmployerBee


class BeeView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if self.get_object() is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class WorkerBeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerBee
        fields = '__all__'


class WorkerBeeView(BeeView):
    serializer_class = WorkerBeeSerializer

    def get_object(self):
        try:
            return self.request.user.worker_bee
        except ObjectDoesNotExist:
            return None


class EmployerBeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerBee
        fields = '__all__'


class EmployerBeeView(BeeView):
    serializer_class = EmployerBeeSerializer

    def get_object(self):
        try:
            return self.request.user.employer_bee
        except ObjectDoesNotExist:
            return None
