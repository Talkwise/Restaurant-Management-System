from .models import * 


def global_context(request):
    
    return {'restaurant': Configuration.objects.first()}
