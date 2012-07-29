from ui.config import SITE_CONFIG
from django.contrib.sites.models import Site
    
def basics(req):
    result = SITE_CONFIG
    result['domain'] = Site.objects.get_current().domain
    return result