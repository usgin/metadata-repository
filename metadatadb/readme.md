# Un-authorized urls 

All the functions created by Genhan are saved in `anauthFunc.py`

> DELETE request to *metadata/unauth/deleteUnpublishRecords*

The above request is to delete all the unpublished records in Django and their related records in CouchDB

> DELETE request to *metadata/unauth/deleteCouchExtraRecords*

The above request is to delete all extra CouchDB records which do not exist in Django