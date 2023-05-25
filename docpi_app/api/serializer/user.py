from rest_framework import serializers
from docpi_app.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ('id',)
        fields = '__all__'
        # fields = ('field4', 'field5', 'field6')