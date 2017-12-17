import os
import json

def to_senti():
	for filename in os.listdir("parsed_commits/"):
		print("retreiving messages from " + filename)
		commits = json.load(open("parsed_commits/" + filename))
		output_f = open("for_senti/" + filename, "w")
		
		output_f.write("Useless header\n")
		print(len(commits))
		for commit in commits:
			try:
				output_f.write(commit["message"].replace('\n', ' ').replace("\r", " ") + "\n")
			except:
				output_f.write("message did not translate\n")
				continue
		
		
def fix_format():
	for filename in os.listdir("commit_statements"):
		print("reformatting " + filename)
		commit_segs = json.load(open("commit_statements/" + filename))
		output_f = open("parsed_commits/" + filename, "w")
		
		res = []
		for commit_seg in commit_segs:
			for commit in commit_seg:
					res.append(commit)
					
		output_f.write(json.dumps(res, indent=4, sort_keys=True))

if __name__ == "__main__":
	#fix_format()
	to_senti()