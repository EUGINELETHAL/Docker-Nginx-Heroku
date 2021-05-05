from django.db.models import Q
from django.views.generic import TemplateView, ListView
from django.contrib.postgres.search import SearchVector,TrigramSimilarity


from .models import City


class HomePageView(ListView):
    template_name = 'home.html'
    model = City.objects.all()
    
    def get_queryset(self):
    	object_list= City.objects.all()
    	return object_list

class SearchResultsView(ListView):
    model = City
    template_name = 'search_results.html'
    
    
    def get_queryset(self): 
        query = self.request.GET.get('q')
        object_list1= City.objects.annotate(similarity=TrigramSimilarity('name', query),).filter(similarity__gt=0.1).order_by('-similarity')
        object_list2=City.objects.annotate(similarity=TrigramSimilarity('state', query),).filter(similarity__gt=0.1).order_by('-similarity')
        object_list= object_list1|object_list2   # merge querysets
        return object_list
        
