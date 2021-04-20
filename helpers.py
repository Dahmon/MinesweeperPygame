import pickle

def readOrCreatePickle(path, default):
	try:
		foo = pickle.load(open(path, "rb"))
	except Exception:
		foo = default
		pickle.dump(foo, open(path, "wb"))
	return foo

def listToString(list):
	return '[ ' + ', '.join([str(item) for item in list]) + ' ]'