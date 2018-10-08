from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic


# Create your views here.


"""class IndexView(generic.View):
    def homePage(self, request):
        return HttpResponse("Hello, world")"""


def homepage(request):
    return HttpResponse("Hello, world.  You are at the Routefinder index.")
