from django.contrib.auth.decorators import login_required, user_passes_test


def staff_user_required(view_func, redirect_field_name='index'):
    staff_user_login_required = user_passes_test(lambda user: user.is_staff)
    return login_required(staff_user_login_required(view_func))