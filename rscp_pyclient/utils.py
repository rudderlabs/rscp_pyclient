import os, json
import copy

fileext = ".json"

def sanitize(jsonObj):
    sensitiveKeys = ["writeKey", "write_keys"]
    def _sanitize(jsonObjCopy):
        if isinstance(jsonObjCopy, dict):
            for sensitiveKey in sensitiveKeys:
                if sensitiveKey in jsonObjCopy:
                    del jsonObjCopy[sensitiveKey]
        elif isinstance(jsonObjCopy, list):
            for childObjCopy in jsonObjCopy:
                _sanitize(childObjCopy)

    jsonObjCopy = copy.deepcopy(jsonObj)    
    _sanitize(jsonObjCopy)
    return jsonObjCopy

def save(jsonObj, filepath):
    """
    Given a JSON object, saves it at the filepath specified. Appends file extension automatically.
    """
    dirname = os.path.dirname(filepath)
    os.makedirs(dirname, exist_ok=True)
    with open(filepath + fileext, "w") as fp:
        json.dump(sanitize(jsonObj), fp, indent=2)

def load(filepath):
    """
    Given a filepath, loads the JSON object contained at the filepath specified. Appends file extension to filepath automatically.
    """
    with open(filepath + fileext, "r") as fp:
        return json.load(fp)

def loadHierarchy(basepath, endpoints, retval={}):
    """
    Given a base folder path and end points saved with it, the method downloads all the JSON obects saved corresponding to endpoints passed.
    Returns a dictionary mapping endpoints to JSON saved at the said endpoint.
    The endpoint may correspond to either a file or a folder.
    """
    basepath = basepath.replace("//", "/")
    for subdir, dirs, files in os.walk(basepath):
        subdir = (subdir + "/").replace("//", "/")
        for filename in files:
            if filename.endswith(fileext):
                filename = filename[0:len(filename)-len(fileext)]
                filepath = subdir + filename
                if any([(filepath == basepath + ep) or (filepath.startswith(basepath + ep + "/")) for ep in endpoints]):
                    key = filepath[len(basepath):]
                    if filepath.endswith(fileext):
                        filepath = fileext[0:len(filepath)-len(fileext)]
                    filepath = subdir + filename
                    retval[key] = load(filepath)
    return retval
