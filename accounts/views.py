from custom import views
from django.contrib.auth.models import User
from .forms import UserUpdateForm


class AccountUpdateView(views.CustomUpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/update_form.html'

    # Evita que se deba pasar el id en la url
    def get_object(self, queryset=None):
        return self.request.user
