from django.shortcuts import render_to_response
from django.db.models import get_model
from django.template import RequestContext

Resource = get_model('registry', 'Resource')

def sitemap(req):
    return render_to_response(
        'repository/sitemap.jade', 
        { 'ids': [ res.metadata_id for res in Resource.objects.all() if res.published ] }, 
        context_instance=RequestContext(req),
        mimetype="text/xml"
    )