def jsonToTerraformTreeWithIndents(json):
    """
    Input:
        JSON
    Output:
        TerraformTreeWithIndents

    What is TerraformTreeWithIndents?
        Problem Statement:
            You have a text with an inherent hierarchical structure.
            You want to print it with proper indentations while inserting appropriate line breaks.
        Approach:
            We annotate the hierarchical structure with indentation constraints.
            Print it with line breaks as a second step. 
        Inductive Definition:
            Base Case(leaf node):
                It is a 2-tuple.
                First value is an integer representing the indentation it needs.
                Second value is a string.
            Recursion Case 1:
                It is a 2-tuple.
                First value is an integer representing the indentation it needs.
                Second value is a TerraformTreeWithIndents(recursive invocation).
            Recursion Case 2:
                It is a list of child TerraformTreeWithIndents(recursive invocation).
    """
    elementryType = None
    if isinstance(json, str):
        elementryType = "str"
    elif isinstance(json, bool):
        elementryType = "bool"
    elif isinstance(json, int) or isinstance(json, float):
        elementryType = "num"

    if elementryType != None:
        valueStr = "\"{0}\"".format(json) if isinstance(json, str) else str(json)
        if isinstance(json, bool):
            valueStr = valueStr.lower()
        return [(0, "{"), (2, elementryType + " ="), (4, valueStr), (0, "}")]

    if isinstance(json, list):
        if len(json) == 0:
            return [(0, "{"), (2, "objects_list = []"), (0, "}")]
        else:
            retlist = []
            for index, jsonElement in enumerate(json):
                jsonElementTerraformTree = jsonToTerraformTreeWithIndents(jsonElement)
                if index != len(json) - 1:
                    jsonElementTerraformTree = _appendComma(jsonElementTerraformTree)
                retlist.append(jsonElementTerraformTree)
            return [(0, "{"), (2, "objects_list = ["), (4, retlist), (2, "]"), (0, "}")]
    elif isinstance(json, dict):
        if len(json) == 0:
            return [(0, "{"), (2, "object = {}"), (0, "}")]
        else:
            retlist = []
            for index, (jsonKey, jsonValue) in enumerate(json.items()):
                jsonKeyStr = "\"{0}\":".format(jsonKey) if isinstance(jsonKey, str) else str(jsonKey)
                jsonValueTerraformTree = jsonToTerraformTreeWithIndents(jsonValue)
                if index != len(json) - 1:
                    jsonValueTerraformTree = _appendComma(jsonValueTerraformTree)
                if isinstance(jsonValueTerraformTree, list) \
                        and len(jsonValueTerraformTree) >= 1 \
                        and isinstance(jsonValueTerraformTree[0], tuple) \
                        and jsonValueTerraformTree[0][1] == "{" :
                    jsonKeyStr += " {"
                    del jsonValueTerraformTree[0]

                retlist.append([(0, jsonKeyStr), jsonValueTerraformTree])
            
            return [(0, "{"), (2, "object = {"), (4, retlist), (2, "}"), (0, "}")]
    else:
        raise NotImplementedError("Unknown type in json", json)
        import pdb;pdb.set_trace()

def terraformTreeToIndentedTerraformCli(terraformTreeWithIndents, indent="", maxWidth=80):
    """
        Input:
            TerraformTreeWithIndents
        Output:
            2 Tuple
            First value is string representation of the entire tree, while respecting indentation constraints.
            Second value is boolean representing whether the result is single line(true if single line).
    """
    if isinstance(terraformTreeWithIndents, tuple):
        nodeIndent, nodeTree = terraformTreeWithIndents
        if isinstance(nodeTree, list):
            return terraformTreeToIndentedTerraformCli(nodeTree, nodeIndent*" " + indent, maxWidth)
        else:
            return nodeTree, True
    elif isinstance(terraformTreeWithIndents, list):
        childTerraformCliList = []
        isSingleLine = True
        joinedLength = len(indent) + len(terraformTreeWithIndents) - 1
        for childNode in terraformTreeWithIndents:
                childTerraformCli, isChildSingleLine = terraformTreeToIndentedTerraformCli(childNode, indent, maxWidth)
                isSingleLine = isSingleLine and isChildSingleLine
                joinedLength += len(childTerraformCli)
                childTerraformCliList.append(childTerraformCli)
        if len(childTerraformCliList) == 1 or (isSingleLine and joinedLength < maxWidth):
            return " ".join(childTerraformCliList), True
        else:
            for i, childNode in enumerate(terraformTreeWithIndents):
                if isinstance(childNode, tuple):
                    childNodeIndent, childNodeValue = childNode
                    childTerraformCliList[i] = (childNodeIndent * " ") + childTerraformCliList[i]

            return ("\n" + indent).join(childTerraformCliList), False
    else:
        raise NotImplementedError("Unknown object in terraformTreeWithIndents", terraformTreeWithIndents)
        import pdb;pdb.set_trace()

def jsonToIndentedTerraformCli(json):
    terraformTreeWithIndents = jsonToTerraformTreeWithIndents(json)
    terraformCli, isSingleLine = terraformTreeToIndentedTerraformCli(terraformTreeWithIndents)
    return terraformCli

def _appendComma(terraformTreeWithIndents):
    lastTupleNode = terraformTreeWithIndents
    parentToLastTupleNode = None
    while not isinstance(lastTupleNode, tuple):
        assert(isinstance(lastTupleNode, list))
        parentToLastTupleNode = lastTupleNode
        lastTupleNode = lastTupleNode[len(lastTupleNode) - 1]
    indent, strValue = lastTupleNode
    strValue = strValue + ","
    if parentToLastTupleNode == None:
        terraformTreeWithIndents = (indent, strValue)
    else:
        parentToLastTupleNode[len(parentToLastTupleNode) - 1] = (indent, strValue)

    return terraformTreeWithIndents

if __name__ == "__main__":
    testJsons = [
        {
            "trackingID": "UA-908213012-193",
            "doubleClick": True,
            "enhancedLinkAttribution": True,
            "includeSearch": True,
            "dimensions": [
                {
                    "from": "mas.",
                    "to": "3"
                }
            ],
            "metrics": [
                {
                    "from": "kksad1222",
                    "to": "2"
                }
            ],
            "contentGroupings": [
                {
                    "from": "lkjdlkjsdf",
                    "to": "lkjlkjsdf"
                }
            ],
            "enableServerSideIdentify": True,
            "serverSideIdentifyEventCategory": "mnd,msdnf",
            "serverSideIdentifyEventAction": ",mn,m",
            "anonymizeIp": True,
            "enhancedEcommerce": True,
            "nonInteraction": True,
            "sendUserId": True,
            "disableMd5": True
        }, 
        {
            "asaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa":
                "sssssssssssssssssssssssssssssssssssssssssssssssssss"
        },
        [1,2,3],
        { "a" : 2 },
        { "a" : 2, "b" : [ "c", { "d":4, "e":["kjlasldjalsdj", "kljljasldjas"]}]},
        {1:2,3:4,5:6}
    ]
    
    for index, testJson in enumerate(testJsons):
        print("\nFor index {0}, rudder ---->\n{1}\n----------\n".format(index, jsonToIndentedTerraformCli(testJson)))
