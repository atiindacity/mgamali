from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    role = request.user.role

    # Optional: Redirect based on role
    if role == "admin":
        return render(request, "dashboard/admin_dashboard.html")
    if role == "store":
        return render(request, "dashboard/store_dashboard.html")
    if role == "collector":
        return render(request, "dashboard/collector_dashboard.html")

    # Default user dashboard
    return render(request, "dashboard/user_dashboard.html")


