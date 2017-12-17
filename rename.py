import os

for filename in os.listdir("from_senti"):
	print(filename)
	os.rename("from_senti/" + filename, "from_senti/" + filename.replace("+results", ""))