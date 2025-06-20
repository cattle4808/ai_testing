from rest_framework.permissions import BasePermission

class TokenPermission(BasePermission):
    def has_permission(self, request, view):
        tokens = ['ashjdguasgxugd176tex67nansdigfuy']
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            return False
        return auth.split(' ')[1] in tokens