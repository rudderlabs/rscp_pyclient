import sys, os, json, requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException, abort

if __name__ == '__main__' and __package__ is None:
    package_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.dirname(package_path))
    __package__ = os.path.basename(package_path)

from .utils import save, load, loadHierarchy
from .constants import segmentUrl, savedir

def downloadSegmentEndpoint(absEndpointUrl, headers, filepath):
    """
    Download and save a single segment endpoint.
    """
    retval = requests.get(absEndpointUrl, headers=headers)
    if retval.ok:
        save(json.loads(retval.text), filepath)

def downloadSegmentListEndpoint(baseUrl, endPoint, headers, resultDict, filepath):
    """
    Download and save a list-like segment endpoint, and also download all elements in the encapsulated list that it points to.
    """
    key = os.path.basename(endPoint)
    endPointExt = "/" + endPoint
    endPointUrl = baseUrl + endPointExt
    endPointFilepath = filepath + endPointExt
    nextPageToken=None
    accumulatedList = []
    while True:
        params={}
        if nextPageToken != None:
            params["page_token"] = nextPageToken
        listResult = requests.get(endPointUrl, headers=headers, params=params)
        if not listResult.ok:
            abort(listResult.status_code, "Error quering segment REST API. Response: {0}".format(listResult.text))
        elementGroupObj = json.loads(listResult.text)
        accumulatedList.extend(elementGroupObj[key])
        for element in elementGroupObj[key]:
            if element is str:
                elementExt = "/" + element
                downloadSegmentEndpoint(endPointUrl + elementExt, headers, endPointFilepath + elementExt)
        nextPageToken=elementGroupObj.get("next_page_token")
        print("Cur Count of ", endPoint, " is ", len(accumulatedList), nextPageToken)
        if nextPageToken == "" or nextPageToken == None:
            break
        else:
            sys.stdout.flush()
    resultDict[endPoint] = accumulatedList
    save(accumulatedList, endPointFilepath)
    return accumulatedList

def downloadSegmentListEndpoints(segmentEndpoints, segmentHeaders, resultDict, segmentFilepath):
    """
    Download and saves a collection of list-like and non-list-like segment endpoint. When downloading list-like endpoints, we also download elements in the encapsulated list.
    Also, some list-like endpoints(e.g. workspaces) also point to other subordinate endpoints(like sources and destinations of a workspace). We download and save them all. 
    """
    i = 0
    while i < len(segmentEndpoints):
        endPoint = segmentEndpoints[i]
        accumulatedList = downloadSegmentListEndpoint(segmentUrl, endPoint, segmentHeaders, resultDict, segmentFilepath)
        insertionPos = i
        if endPoint == "workspaces":
            for workspace in accumulatedList:
                insertionPos += 1
                segmentEndpoints.insert(insertionPos, workspace["name"] + "/sources")
        if endPoint.startswith("workspaces") and endPoint.endswith("sources"):
            for workspaceSource in accumulatedList:
                insertionPos += 1
                segmentEndpoints.insert(insertionPos, workspaceSource["name"] + "/destinations")
        i += 1

# Segment catalog contains segment items which apply across all segment workspaces. For example catalog sources and catalog destinations. 

# Folder in which to save segment catalog elements.
segmentCatalogFolder = "{0}/{1}/".format(savedir, "SegmentConfig")

# Dictionary containing all the downloaded segment catalog elements. Populated by the function downloadSchemaCatalog.
segmentCatalog={}

# Last time that we downloaded segment catalog elements. When it is too long back, we download again. 
segmentCatalogLastDownloadTime=None

# List of endpoints from where the entire segment catalog can be downloaded.
segmentCatalogEndpoints = ["catalog/sources", "catalog/destinations"]

def downloadSchemaCatalog(segmentHeaders):
    """
    Method to download segment catalog.
    Segment catalog contains segment items which apply across all segment workspaces. For example catalog sources and catalog destinations. 
    """
    # Load catalog from saved files if not already loaded.
    global segmentCatalogLastDownloadTime, segmentCatalog
    if segmentCatalogLastDownloadTime == None:
        loadHierarchy(segmentCatalogFolder, segmentCatalogEndpoints, segmentCatalog)
        # Load already saved segmentCatalogEndpoints for the first time.
        for ep in segmentCatalogEndpoints:
            epWithExt = ep + ".json"
            epFilepath = segmentCatalogFolder + epWithExt
            if os.path.exists(epFilepath) and os.path.isfile(epFilepath):
                segmentCatalogLastDownloadTime = datetime.fromtimestamp(os.path.getmtime(epFilepath))

    # Load catalog from server if not already loaded.
    if segmentCatalogLastDownloadTime != None:
        catalogTooOld = segmentCatalogLastDownloadTime-datetime.utcnow() > timedelta(1)
    if not segmentCatalog or catalogTooOld or len(segmentCatalog) < len(segmentCatalogEndpoints):
        downloadSegmentListEndpoints(segmentCatalogEndpoints, segmentHeaders, segmentCatalog, segmentCatalogFolder)
        LastLastDownloadTime = datetime.utcnow()

def downloadSegmentAll(segmentToken):
    """
    Given a segment token, this method downloads all the segment workspaces. Segment catalog elements are also downloaded if absent or too old. 
    """
    segmentHeaders = {"Authorization" : "Bearer {}".format(segmentToken)}

    downloadSchemaCatalog(segmentHeaders)

    curTime = datetime.utcnow();
    segmentWorkspaceFolder = "{0}/{1:%Y-%m-%d}-SegmentConfig-{2}/".format(savedir, curTime, segmentToken[0:5])

    segmentWorkspace = {}
    segmentWorkspaceEndpoints = ["workspaces"]
    downloadSegmentListEndpoints(segmentWorkspaceEndpoints, segmentHeaders, segmentWorkspace, segmentWorkspaceFolder)

    return segmentWorkspaceFolder, segmentWorkspace

if __name__ == '__main__':
    secrets = load("secrets")
    downloadSegmentAll(secrets["segmentToken"])
