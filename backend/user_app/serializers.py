from rest_framework.serializers import ModelSerializer

from user_app.models import User, UserProfile, UserLoginOTP, UserPasswordResetToken, UserToken, UserTokenUsage


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


class UserLoginOTPInputSerializer(ModelSerializer):

    class Meta:
        model = UserLoginOTP
        fields = '__all__'


class UserLoginOTPOutputSerializer(ModelSerializer):
    user = ShowUserSerializer()

    class Meta:
        model = UserLoginOTP
        fields = ("id", "user", "created", "otp_expires_at")


class UserPasswordResetTokenInputSerializer(ModelSerializer):

    class Meta:
        model = UserPasswordResetToken
        fields = '__all__'


class UserPasswordResetTokenOutputSerializer(ModelSerializer):
    user = ShowUserSerializer()

    class Meta:
        model = UserPasswordResetToken
        fields = '__all__'


class UserTokenInputSerializer(ModelSerializer):

    class Meta:
        model = UserToken
        fields = '__all__'


class UserTokenOutputSerializer(ModelSerializer):
    user = ShowUserSerializer()

    class Meta:
        model = UserToken
        fields = ('id', 'user', 'alias', 'created', 'updated')


class UserTokenUsageInputSerializer(ModelSerializer):

    class Meta:
        model = UserTokenUsage
        fields = '__all__'


class UserTokenUsageOutputSerializer(ModelSerializer):
    token = UserTokenOutputSerializer()

    class Meta:
        model = UserTokenUsage
        fields = '__all__'
