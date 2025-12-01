from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import role_required

@login_required
@role_required(allowed_roles=['admin', 'subadmin'])
def admin_dashboard(request):
    # Your view logic
    return render(request, 'admin/dashboard.html')
