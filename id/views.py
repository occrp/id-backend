from registration.views import RegistrationView
from settings.settings import REGISTRATION_OPEN, REGISTRATION_CLOSED_URL, REGISTRATION_SUCCESS_URL

class ProfileRegistrationView(RegistrationView):
    """
    Profile registration view.
    as per http://django-registration.readthedocs.org/en/latest/views.html
    """

    disallowed_url = REGISTRATION_CLOSED_URL
    success_url = REGISTRATION_SUCCESS_URL
                                                                                                                                                                                                                        
                                                                                                                                                                                                                           
    def registration_allowed(self, request):                                                                                                                                                                               
        """                                                                                                                                                                                                           
        Simple as that -- and controlled from settings                                                                                                                                                                                           
        """
        return REGISTRATION_OPEN
                                                                                                                                                                                                                           
    def register(self, request, form):                                                                                                                                                                                     
        """
        Implement user-registration logic here. Access to both the                                                                                                                                                         
        request and the full cleaned_data of the registration form is                                                                                                                                                      
        available here.                                                                                                                                                                                                    
                                                                                                                                                                                                                           
        """
        return form.save()