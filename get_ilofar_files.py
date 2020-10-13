import urllib
from bs4 import BeautifulSoup
from pathlib import Path


def find_ilofar_data(date):
	"""
	Function to find I-LOFAR BST data and return list of available files.

	Parameters
	----------
	date : `datetime.datetime`, astropy.time.Time


	Returns
	-------
	list : list of available BST files


	"""
	baseurl = "https://data.lofar.ie/{:s}/bst/kbt/rcu357_1beam/".format(date.strftime("%Y/%m/%d"))
	file_urls = []
	try: 
		opn = urllib.request.urlopen(baseurl)
		try:
			soup = BeautifulSoup(opn, "html.parser")
			for link in soup.find_all("a"):
				href = link.get("href")
				if href.endswith("00X.dat"): # or href.endswith("00Y.dat"):
					file_urls.append(urllib.parse.urljoin(baseurl, href))
		except:
			print("no bst files")
	except:
		print("page doesn't exist")
	return file_urls


def get_ilofar_data(date, path="./"):
	"""
	Function to download the available ILOFAR BST files.

	Parameters
	----------
	date : datetime.datetime, astropy.time.Time

	Example
	-------
	>>> get_ilofar_data(parse_time("2017-09-10"), path="./bst_files/")
		'download success'
	"""

	files = find_ilofar_data(date)
	if len(files)<0:
		return 

	for f in files:
		urllib.request.urlretrieve(f, Path(path).joinpath(f.split("/")[-1]))

	if Path(path).joinpath(f.split("/")[-1]).exists():
		print("download success")




