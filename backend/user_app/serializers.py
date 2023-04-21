from rest_framework.serializers import ModelSerializer

from user_app.models import User, UserProfile


class UserRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password"
        )
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class ShowUserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "date_joined",
            "slug",
            "unsuccessful_login_attempts",
            "blocked_until",
            "date_joined"
        )


class UserProfileInputSerializer(ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileOutputSerializer(ModelSerializer):
    user = ShowUserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'
