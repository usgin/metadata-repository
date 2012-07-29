from django.http import HttpResponse
from models import Contact
import json

def contacts(req):
    contacts = [ '"' + contact.name + '":' + contact.json for contact in Contact.objects.all() ]
    return HttpResponse('{' + ','.join(contacts) + '}', content_type='application/json')