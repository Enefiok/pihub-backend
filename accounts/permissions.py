from rest_framework import permissions


class IsManagementOrReadOnly(permissions.BasePermission):
    """
    Default policy for most modules.
    - CEO, Lead Developer, Admin: full access (create/edit/delete).
    - Everyone else who is authenticated: read-only (view only).
    """
    MANAGEMENT_ROLES = ['CEO', 'LEAD_DEVELOPER', 'ADMIN']

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in self.MANAGEMENT_ROLES


class IsMarketerOrManagement(permissions.BasePermission):
    """
    For Blog and Gallery modules.
    - CEO, Lead Developer, Admin, Marketer: full access.
    - Everyone else who is authenticated: read-only.
    """
    FULL_ACCESS_ROLES = ['CEO', 'LEAD_DEVELOPER', 'ADMIN', 'MARKETER']

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in self.FULL_ACCESS_ROLES


class IsManagementOrReceptionistCreateOnly(permissions.BasePermission):
    """
    For Bookings.
    - CEO, Lead Developer, Admin: full access (create/edit/delete).
    - Receptionist: can create (walk-ins) and view, but not edit/delete.
    - Everyone else who is authenticated: read-only.
    """
    MANAGEMENT_ROLES = ['CEO', 'LEAD_DEVELOPER', 'ADMIN']

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST':
            return request.user.role in self.MANAGEMENT_ROLES or request.user.role == 'RECEPTIONIST'

        # PUT, PATCH, DELETE — management only
        return request.user.role in self.MANAGEMENT_ROLES


class IsManagementStrict(permissions.BasePermission):
    """
    For the Staff module (managing other staff accounts).
    - CEO, Lead Developer only — Admin is deliberately excluded here.
    - Everyone else who is authenticated: read-only.
    """
    STRICT_ROLES = ['CEO', 'LEAD_DEVELOPER']

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in self.STRICT_ROLES