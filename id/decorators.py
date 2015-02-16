from django.core.exceptions import PermissionDenied

def admin_only(user):
	if not user.is_authenticated(): raise PermissionDenied
	if user.profile.is_admin: return True
	raise PermissionDenied

def staff_only(user):
	if not user.is_authenticated(): raise PermissionDenied
	if user.profile.is_admin: return True
	if user.profile.is_staff: return True
	raise PermissionDenied

def volunteers_only(user):
	if not user.is_authenticated(): raise PermissionDenied 
	if user.profile.is_admin: return True
	if user.profile.is_volunteer: return True
	raise PermissionDenied

def users_only(user):
	if not user.is_authenticated(): raise PermissionDenied 
	if user.profile.is_admin: return True
	if user.profile.is_user: return True
	raise PermissionDenied
