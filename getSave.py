import pickle

def get(filename):
    """retrieves list from file"""
    theList = []
    with open(filename, "rb") as fp:
        theList = pickle.load(fp)
    return theList

def save(theList, filename):
    """saves list to file"""
    with open(filename, "wb") as fp:
        pickle.dump(theList, fp)
