from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate_new_password(self, value):
        validate_password(
            value,
            user=self.context.get('user'),
        )
        return value