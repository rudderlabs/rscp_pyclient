import sys, os, json, requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
from werkzeug.exceptions import HTTPException, abort

if __name__ == '__main__' and __package__ is None:
    package_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.dirname(package_path))
    __package__ = os.path.basename(package_path)

from .utils import save, load, loadHierarchy
from .constants import savedir, getRudderSchemaRetrievalUrl, getRudderWorkspaceUrl, getRudderFilepath

def downloadRudderEndpoint(auth, url, endpoint, filepath):
    """
    Download and save a single rudder endpoint.
    """
    endpointUrl = url + endpoint
    endpointFilepath = filepath + "/" + endpoint
    if endpoint == "workspaceConfig":
        params = {"fetchAll":True}
    else:
        params = None
    result = requests.get(endpointUrl, auth=auth, params=params)
    if result.ok:
        retval = json.loads(result.text)
        save(retval, endpointFilepath)
        return retval
    else:
        abort(result.status_code, "Error retrieving V1 rudder endpoint {0}. Params {1}. Response: {2}".format(
            endpoint,
            params,
            result.text))

rudderstackSchemasFolder = None
rudderstackSchemas={}
rudderstackSchemasLastDownloadTime=None
schemaEndpointsToDownload = ["source-definitions", "destination-definitions"]

def downloadRudderstackSchemas(serverDesc, rudderSchemaRetrievalAuth):
    """
    Download rudderstack source and destination definitions which are commonly applicable across all client workspaces.
    """
    # Load rudder schema from saved files if not already loaded.
    global rudderstackSchemasFolder, rudderstackSchemasLastDownloadTime, rudderstackSchemas
    if rudderstackSchemasFolder == None:
        rudderstackSchemasFolder = getRudderFilepath(serverDesc)

    if rudderstackSchemasLastDownloadTime == None:
        loadHierarchy(rudderstackSchemasFolder, schemaEndpointsToDownload, rudderstackSchemas)
        # Load already saved schemaEndpointsToDownload for the first time.
        for ep in schemaEndpointsToDownload:
            epWithExt = ep + ".json"
            epFilepath = rudderstackSchemasFolder + epWithExt
            if os.path.exists(epFilepath) and os.path.isfile(epFilepath):
                rudderstackSchemasLastDownloadTime = datetime.fromtimestamp(os.path.getmtime(epFilepath))

    # Load rudder schema from server if not already loaded.
    noCatalog = not rudderstackSchemas
    if not noCatalog:
        catalogTooOld = rudderstackSchemasLastDownloadTime-datetime.utcnow() > timedelta(1)
    if noCatalog or catalogTooOld or len(rudderstackSchemas) < len(schemaEndpointsToDownload):
        for schemaEndpoint in schemaEndpointsToDownload:
            rudderstackSchemas[schemaEndpoint] = downloadRudderEndpoint(
                rudderSchemaRetrievalAuth,
                rudderSchemaRetrievalUrl(serverDesc),
                "/" + schemaEndpoint,
                rudderFilepath(serverDesc))

def downloadRudderEndpointV2(headers, url, endpoint, params, filepath):
    """
    Download a RudderStack V2 endpoint and save its contents.
    """
    endpointUrl = url + endpoint
    if filepath is not None:
        endpointFilepath = filepath + "/" + endpoint
    result = requests.get(endpointUrl, headers=headers, params=params)
    if result.ok:
        retval = json.loads(result.text)
        if filepath is not None:
            save(retval, endpointFilepath)
        return retval
    else:
        abort(result.status_code, "Error retrieving V2 rudder endpoint {0}. Params {1}. Response: {2}".format(
            endpoint,
            params,
            result.text))

if __name__ == '__main__':
    # V2 endpoints that are usually downloaded which retrieving any particular Rudderstack workspace.
    endpointsV2ToDownload = ["/destinations", "/sources"]
    #endpointsV2ToDownload = ["workspaceConfig", "destinations", "sources"]
    
    # Additional V1 endpoints to download
    endpointsV1ToDownload = ["/workspaceConfig"]

    # Load Server setup. 
    secrets = load("secrets")
    serverDesc = secrets["isProd"] 

    # Figure out rudder workspace auth to use.
    rudderWorkspaceToken = secrets["rudderWorkspaceToken"]
    rudderWorkspaceAuthHeaders = {"Authorization" : "Bearer {0}".format(rudderWorkspaceToken)}

    # Figure out rudder schema retrieval auth to use.
    rudderSchemaRetrievalToken = secrets["rudderSchemaRetrievalToken"]
    rudderSchemaRetrievalAuth = HTTPBasicAuth(rudderSchemaRetrievalToken, '')

    rudderWorkspaceUrl = getRudderWorkspaceUrl(serverDesc)
    rudderSchemaRetrievalUrl = getRudderSchemaRetrievalUrl(serverDesc)
    rudderFilepath = getRudderFilepath(serverDesc)

    # Download rudder schemas.
    downloadRudderstackSchemas(serverDesc, rudderSchemaRetrievalAuth)

    for endpoint in endpointsV1ToDownload:
        downloadRudderEndpoint(
            rudderSchemaRetrievalAuth,
            rudderSchemaRetrievalUrl,
            endpoint,
            rudderFilepath)

    for endpoint in endpointsV2ToDownload:
        downloadRudderEndpointV2(
            rudderWorkspaceAuthHeaders,
            rudderWorkspaceUrl,
            endpoint,
            None,
            rudderFilepath)
