import jwt
from rest_framework.permissions import BasePermission
from django.conf import settings
from UserSupportService.models import User


class ValidateUserRole(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split()[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(pk=payload['user_id'])
            if user.is_admin:
                return True
            else:
                return False
        except KeyError as e:
            print(e)
            return False
        except jwt.ExpiredSignatureError:
            return False
        except jwt.DecodeError as e:
            print(e)
            return False
        except jwt.InvalidTokenError:
            return False
        except User.DoesNotExist:
            return False
