from django.shortcuts import render_to_response

def upload(req, resourceId):
    return render_to_response('records/upload-file.html', { 'resourceId': resourceId })