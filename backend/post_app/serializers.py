from rest_framework.serializers import ModelSerializer

from post_app.models import Tag, Post

class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            "name",
        )


class PostInputSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class PostOutputSerializer(ModelSerializer):
    tags = TagSerializer(many=True).data

    class Meta:
        model = Post
        fields = '__all__'