import pickle

def get(filename):
    """retrieves object from file"""
    theObject = []
    with open(filename, "rb") as fp:
        theObject = pickle.load(fp)
    return theObject

def save(theObject, filename):
    """saves object to file"""
    with open(filename, "wb") as fp:
        pickle.dump(theObject, fp)
