from django.contrib.auth.models import User
from rest_framework import serializers, generics, permissions


class UserSerializer(serializers.ModelSerializer):
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


class UserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
