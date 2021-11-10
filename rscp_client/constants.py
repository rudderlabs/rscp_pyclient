from .utils import load
import os

# Root directory where all config is stored.
savedir = "savedir/"

# Sub directories for saving rudderstack and segment data.
segConfigDir = savedir + "SegmentConfig/"
segWorkspacesDir = segConfigDir + "workspaces/"
rsConfigDir = savedir + "RudderStackConfig/"


def getServerSlug(serverDesc):
    if isinstance(serverDesc, str):
        return ".custom"
    elif serverDesc == True:
        return ""
    elif serverDesc == False:
        return ".dev"

# Use this for retrieval of source and destination definitions.
def getRudderSchemaRetrievalUrl(serverDesc):
    if isinstance(serverDesc, str):
        return serverDesc
    else:
        return 'https://api{0}.rudderlabs.com'.format(getServerSlug(serverDesc))

# Use this for creation and deletion of sources, destinations and connections.
def getRudderWorkspaceUrl(serverDesc):
    if isinstance(serverDesc, str):
        return serverDesc + "/v2"
    else:
        return 'https://api{0}.rudderlabs.com/v2'.format(getServerSlug(serverDesc))

# Folder where Rudder schema information should be saved.
def getRudderFilepath(serverDesc):
    return savedir + "RudderStackConfig{0}/".format(getServerSlug(serverDesc))

# URL for downloading Segment config.
segmentUrl = 'https://platform.segmentapis.com/v1beta'
