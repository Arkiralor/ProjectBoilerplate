from user_app.models import User
from user_app.utils import UserTokenUtils

def main():
    user = User.objects.all()[1]
    print(f"User ID:{user.id}")
    user_token = UserTokenUtils.create_permanent_token(user)
    print(f"Token: {user_token}")
    user_id = UserTokenUtils.get_user_id(token=user_token)
    print(f"UserID: {user_id}")

    try:
        new_user = User.objects.filter(pk=user_id).first()
        assert new_user == user

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()