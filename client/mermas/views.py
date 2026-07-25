from django.shortcuts import render
from django.views import generic
import requests

# Create your views here.

class ListMermas(generic.View):
    template_name = 'mermas/list_merma.html'
    context = {}
    url_base = 'http://127.0.0.1:8000/api/mermas/registro/list/'
    response = None
    
    def get(self, request):
        self.response = requests.get(url=self.url_base).json()
        self.context = {
            "mermas": self.response
        }
        return render(request, self.template_name, self.context)