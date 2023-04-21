class UserModelChoices:
    user = "User"
    moderator = "Moderator"
    admin = "Administrator"

    USER_TYPE_CHOICES = (
        (user, user),
        (moderator, moderator),
        (admin, admin)
    )

    female = "Female"
    male = "Male"
    other = "Other"

    USER_GENDER_CHOICES = (
        (female, female),
        (male, male),
        (other, other)
    )