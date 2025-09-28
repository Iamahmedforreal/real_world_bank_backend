from django import permissions

class IsUthenticated(permissions.BasePermission):

    """Custom permission to only allow authenticated users to access the view."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    

class IsOwnerOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class transactionPermission(permissions.BasePermission):
    """Custom permission to only allow owners of a transaction to view it."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        return obj.from_account.customer.user == request.user or obj.to_account.customer.user == request.user

        
        
class IsCustomerOrReadOnly(permissions.BasePermission):
    """
    Allows customers to view and update their own profile.
    Admins can perform any action.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        # Object-level permission: only owner
        return obj.user == request.user
class IsAccountOwnerOrStaff(permissions.BasePermission):
    """
    Customer can view or manage their own accounts.
    Staff/Admin can manage any account.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.customer.user == request.user
    
class IsLoanOwnerOrStaff(permissions.BasePermission):
    """
    Only loan owner can view or repay.
    Staff/Admin can approve, reject, or update status.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.customer.user == request.user

