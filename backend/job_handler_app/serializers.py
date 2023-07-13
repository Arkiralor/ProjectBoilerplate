import pickle

from rest_framework.serializers import CharField, DateTimeField, Serializer, SerializerMethodField, ModelSerializer

from job_handler_app.models import EnqueuedJob


class RQJobSerializer(Serializer):
    """
    Serializer for RQ jobs; used to return job information to the client.
    """
    id = CharField(
        help_text="The job's ID",
        read_only=True
    )
    status = SerializerMethodField()
    result = CharField(
        help_text="The job's return value",
        read_only=True
    )
    data = SerializerMethodField()
    queue = SerializerMethodField()
    created_at = DateTimeField(
        help_text="The time the job was created",
        read_only=True
    )
    enqueued_at = DateTimeField(
        help_text="The time the job was enqueued",
        read_only=True
    )

    def get_status(self, obj):
        """
        Return the value of the `_status` attribute as `status`.
        """
        return getattr(obj, '_status', None)

    def get_data(self, obj):
        """
        Return the value of the `_data: bytes` attribute as `data`.
        """
        data = getattr(obj, '_data', None)
        if data is not None:
            deserialized_data = pickle.loads(data)
            return deserialized_data
        return None

    def get_queue(self, obj):
        """
        Return the value of the `origin` attribute as `queue`.
        """
        return getattr(obj, 'origin', None)


class EnqueuedJobSerializer(ModelSerializer):

    class Meta:
        model = EnqueuedJob
        fields = '__all__'