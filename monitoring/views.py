from django.shortcuts import render
from accounts.decorators import role_required
from .models import DataQualityIssue
from .services.run_all import run_all_checks


@role_required("ops", "analyst", staff_only=True)
def issues(request):
    if request.method == "POST":
        run_all_checks()
    rows = DataQualityIssue.objects.all()[:200]
    return render(request, "monitoring/issues.html", {"issues": rows})
