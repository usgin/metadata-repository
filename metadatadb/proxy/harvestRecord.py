from django.http import HttpResponseNotAllowed, HttpResponse
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
    
    """
    decode_data_dict function is to identify 
        if the given dictionary can be decoded with the listed formats  
    """
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
            return HttpResponse('Cannot decode the data to ' + ', '.join(encodings) + '!')
    
    """
    parseCSV function is to read csv file,
        and return a list of records
    """
    
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
    
    ids = []
    files = req.FILES.getlist('file')
    
    for f in files:
        data = ""
        """
        If the format of the uploaded file is CSV, read the file using parseCSV function.
        Otherwise, read the file content as a string.
        """
        if uploadFormat == 'csv':
            data = parseCSV(csv.reader(f))
            if type(data) != list:
                return data
        else:
            data = f.read()       
        
        """
        Construct the data dictionary for the proxy request,
            and determine if the dictionary can be converted to a json object
        """
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
            """
            Keep Django database update with CouchDB
            """
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
        else:
            return response
    
    context = {'newResources': ids}    
    return render(req, 'repository/upload-results.jade', context)
  
        