import re
import os
import json
import time
import datetime
import requests


from requests.auth import HTTPBasicAuth

def authenticate():
	user = "adamschunk"
	pas = "BatteryStaple1994!"
	r = requests.get('https://api.github.com/user', auth=(user, pas))

def get_repo_list(file):	
	repo_file = open("repo_lists/" + file + ".txt", "r")
	return repo_file.read().splitlines()

def parse_commits(commits):
	parsed = []
	for commit in commits:
		tmp = {}
		
		tmp["user_id"] = "-1"
		tmp["username"] = "-1"
		tmp["message"] = "-1"
		tmp["date"] = "-1"
		
		if commit["committer"]:
			tmp["user_id"] = commit["committer"]["id"]
		
		if commit["commit"]["message"]:
			tmp["message"] = commit["commit"]["message"]
		
		if commit["commit"]["author"]["date"]:
			tmp["date"] = commit["commit"]["author"]["date"]
		
		if commit["commit"]["author"]["name"]:
			tmp["username"] = commit["commit"]["author"]["name"]
			
		parsed.append(tmp)
	return parsed

def save_repo_commits(repo, output_loc):
	completed_repos = os.listdir("parsed_commits")
	if (repo.replace("/","_") + ".txt" in completed_repos):
		print(repo + " already finished")
		return
		
	print("saving " + repo)
	output_file = open(output_loc + repo.replace("/","_") + ".txt", "w")
	r = requests.get('https://api.github.com/repos/' + repo + '/commits?client_id=7295f7c92c892216de7b&client_secret=388edda4532c9499dbe16b78f876e76883e54fc8')
	header = r.headers["link"]
	page = re.findall('page=\d{1,}', header)[1]
	num_pages = int(page[page.index("=")+1:])
	
	
	
	parsed_commits = []
	print(num_pages)
	for i in range(1,num_pages):
		#if(i%int(num_pages/20) == 0):
		#	print("page " + str(i) + " of " + str(num_pages))
		tail = "?client_id=7295f7c92c892216de7b&client_secret=388edda4532c9499dbe16b78f876e76883e54fc8&page=" + str(i)
		r = requests.get('https://api.github.com/repos/' + repo + '/commits' + tail)
		requests_left = int(r.headers["X-RateLimit-Remaining"])
		if requests_left < 10:
			print("sleeping for 1 hour: " + str(datetime.datetime.now().time()))
			time.sleep(3600)
		
		if(r.ok):
			commits = json.loads(r.text or r.content)
			tmp = parse_commits(commits)
			for t in tmp:
				parsed_commits.append(t)
	output_file.write(json.dumps(parsed_commits, indent=4, sort_keys=True))
	
def get_repo_data():
	data = []
	output_file = open("repoDetails.txt", "w")
	#lists = ["c", "java", "c++", "ruby", "python", "main"]
	lists = ["all", "abandoned"]
	for l in lists:
		repo_list = get_repo_list(l)
		for repo in repo_list:
			tmp = {}
			print(repo)
			
			r = requests.get('https://api.github.com/repos/' + repo + '?client_id=7295f7c92c892216de7b&client_secret=388edda4532c9499dbe16b78f876e76883e54fc8')
			r_json = json.loads(r.text)
			tmp["repo_name"] = repo.replace("/","_")
			tmp["language"] = r_json["language"]
			tmp["size"] = r_json["size"]
			tmp["stars"] = r_json["stargazers_count"] 
			tmp["abandoned"] = (l == "abandoned")
			
			
			data.append(tmp)
			
	output_file.write(json.dumps(data, indent=4, sort_keys=True))
			
def run():
	authenticate()
	output_dir = "parsed_commits/"
	#lists = ["c", "java", "c++", "ruby", "python", "main", "abandoned"]
	lists = ["abandoned"]
	for l in lists:
		repo_list = get_repo_list(l)
		for repo in repo_list:
			try:
				save_repo_commits(repo, output_dir)
			except:
				print(repo + " did not finish")
				continue

def get_user_locations():
	lists = ["all"]
	locations = set()
	for l in lists:
		repo_list = get_repo_list(l)
		for repo in repo_list:
			commit_file = open("parsed_commits/" + repo.replace("/","_") + ".txt", "r")
			commits = json.load(commit_file)
			users = set()
			
			for commit in commits:
				users.add(commit["user_id"])
			
			for user in users:
			
				r = requests.get('https://api.github.com/users/' + "Eli" + '?client_id=7295f7c92c892216de7b&client_secret=388edda4532c9499dbe16b78f876e76883e54fc8')
				r_json = json.loads(r.text)
				print(r_json)
				if r_json["location"]:
					loc = r_json["location"]
					locations.add(loc)
			
	output_file.write(json.dumps(locations, indent=4, sort_keys=True))
				
if __name__ == "__main__":
	run()
	#get_repo_data() # run this after to set the number of stars.
	#get_user_locations()