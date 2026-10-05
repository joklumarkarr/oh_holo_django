from django.shortcuts import render
from .models import VTuber

# Create your views here.

def index(request):
    vtubers = VTuber.objects.all()
    return render(request, "tracker/index.html", {"vtubers": vtubers})