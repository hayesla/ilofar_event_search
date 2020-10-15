import pandas as pd 
from get_ilofar_files import get_ilofar_data

data = pd.read_csv("lofar_flare_event_candidates.csv")

download_success = []
for t in pd.to_datetime(data['event_starttime']):
	print(t)
	try:
		get_ilofar_data(t, path='./bst_files/')
		download_success.append('success')
	except:
		download_success.append('error')
