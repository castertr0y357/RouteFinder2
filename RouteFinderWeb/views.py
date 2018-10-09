from django.shortcuts import render, get_object_or_404
from django.views import View

# Create your views here.


class MainView(View):
    template_name = 'RouteFinderWeb/index.html'
    mystring = "Hello, world"

    def get(self, request):
        context = {'mystring': self.mystring}
        return render(request, self.template_name, context=context)


"""def homepage(request):
    return HttpResponse("Hello, world.  You are at the Routefinder index.")"""
