from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        profile = getattr(user, 'profile', None)

        update_last_login(None, user)

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'groups': list(
                user.groups.values_list('name', flat=True)
            ),
            'area': profile.area.key if profile else None,
            'cargo': profile.cargo if profile else None,
        }

        return data