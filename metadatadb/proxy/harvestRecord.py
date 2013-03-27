from django.http import HttpResponseNotAllowed, HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from metadatadb.proxy import proxyRequest
from registry.tracking import track_resource
import json, csv

@login_required
def harvestRecord(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    kwargs = {
        'path': '/metadata/harvest/',
        'method': req.method,
        'body': req.body,
        'headers': { 'Content-Type': 'application/json' }          
    }
    response = proxyRequest(**kwargs)
    if response.status_code == 200:
        # Track the newly created resources
        content = json.loads(response.content)
        for res in content:
            loc = res.strip('/').split('/')
            kwargs = {
                'user': req.user,
                'resourceId': loc.pop(),
                'content': json.loads(proxyRequest(res, 'GET').content)          
            }
            track_resource(**kwargs)
    return response

@login_required
def uploadRecord(req):
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    collections = req.POST['collection'].split(',')
    uploadFormat = req.POST['uploadFormat']

    def decode_data_dict(data_dict):
        encodings = ["ascii", "utf8", "cp1252"]
        jDict = None
        for encoding in encodings:
            try:
                jDict = json.dumps(data_dict, encoding=encoding)
                break
            except:
                continue
    
        if jDict:
            return jDict
        else:
            return HttpResponse('Cannot decode csv data!')
    
    def parseCSV(rows):
        requiredFields = [
          'title', 'description', 'publication_date', 'north_bounding_latitude',
          'south_bounding_latitude', 'east_bounding_longitude', 'west_bounding_longitude',
          'metadata_contact_org_name', 'metadata_contact_email', 'originator_contact_org_name',
          'originator_contact_person_name', 'originator_contact_position_name', 'originator_contact_email',
          'originator_contact_phone', 'metadata_uuid', 'metadata_date'
        ]
        isTitleRow = True
        fields = []
        data = []
        for row in rows:
            if isTitleRow:
                for rf in requiredFields:
                    if rf not in row:
                        return HttpResponse('Your uploaded CSV lost ' + rf + ' field!')
                for f in row:
                    fields.append(f)
                isTitleRow = False
            else:
                if len(row) != len(fields):
                    return HttpResponse('Data have extra fields which cannot be identified!')
                else:
                    record = {}
                    for i, val in enumerate(row):
                        record[fields[i]] = val
                    data.append(record)
        return data
    
    data = ""
    if uploadFormat == 'csv':
        data = parseCSV(csv.reader(req.FILES['file']))
        if type(data) != list:
            return data
    else:
        data = req.FILES['file'].read()       
        
    bodyDict = {
        "destinationCollections": collections,
        "format": uploadFormat,
        "data": data
    }
    
    jBodyDict = decode_data_dict(bodyDict)
    
    kwargs = {
        'path': '/metadata/upload/',
        'method': req.method,
        'body': jBodyDict,
        'headers': { 'Content-Type': 'application/json' }          
    }
    response = proxyRequest(**kwargs)
    
    if response.status_code == 200:
        ids = []
        # Track the newly created resources
        content = json.loads(response.content)
        for res in content:
            loc = res.strip('/').split('/')
            meta_id = loc.pop()
            kwargs = {
                'user': req.user,
                'resourceId': meta_id,
                'content': json.loads(proxyRequest(res, 'GET').content)          
            }
            track_resource(**kwargs)
            ids.append(meta_id)
            
        context = {'newResources': ids}    
        return render(req, 'repository/upload-results.jade', context)

  
        