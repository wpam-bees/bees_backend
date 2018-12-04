from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers, generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from bees.models import WorkerBee, EmployerBee, JobFilter, CreditCardData


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.CharField(source='worker_bee.balance', read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'worker_bee',
            'employer_bee',
            'password',
            'balance',
        )
        read_only_fields = (
            'worker_bee',
            'employer_bee',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        filters = JobFilter.objects.create()
        WorkerBee.objects.create(user=serializer.instance, filters=filters)
        credit_card = CreditCardData.objects.create()
        EmployerBee.objects.create(user=serializer.instance, credit_card=credit_card)

        headers = self.get_success_headers(serializer.data)
        token = Token.objects.create(user=serializer.instance)
        return Response(token.key, status=status.HTTP_201_CREATED, headers=headers)
