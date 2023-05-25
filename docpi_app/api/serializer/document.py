from rest_framework import serializers
from docpi_app.models import Documents, User
from docpi_app.api.serializer.user import UserSerializer

class DocumentSerializer(serializers.ModelSerializer):
    # documents = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # userDetails = UserSerializer()
    class Meta:
        model = Documents
        # exclude = ('id',)
        fields = '__all__'
        # fields = ('field4', 'field5', 'field6')