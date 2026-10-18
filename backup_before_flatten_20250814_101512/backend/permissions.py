from rest_framework import permissions

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'patient')

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'doctor')

class IsOwnerOrDoctor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if user is a doctor
        if hasattr(request.user, 'doctor'):
            return True
        
        # Check if user is the owner (patient)
        if hasattr(request.user, 'patient'):
            return obj.patient == request.user.patient
        
        return False

class IsAppointmentParticipant(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow creation for authenticated users
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        # Check if user is a doctor
        if hasattr(request.user, 'doctor'):
            return obj.doctor == request.user.doctor
        
        # Check if user is the patient
        if hasattr(request.user, 'patient'):
            return obj.patient == request.user.patient
        
        return False 