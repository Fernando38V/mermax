from django.shortcuts import render
from django.views import generic
import requests
from django.utils.decorators import method_decorator
from usuarios.decorators import login_required_api
# Create your views here.

@method_decorator(login_required_api, name='dispatch')
class ListMermas(generic.View):
    template_name = 'mermas/list_merma.html'
    context = {}
    url_base = 'http://127.0.0.1:8000/api/mermas/registro/list/'
    response = None
    
    def get(self, request):
        token = request.session.get('api_token')
        headers = {
            'Authorization': f'Token {token}'
        }
        
        response = requests.get(
            url=self.url_base, 
            headers=headers
        )
        
        self.response = response.json()
        
        self.context = {
            "mermas": self.response
        }
        
        return render(request, self.template_name, self.context)
        