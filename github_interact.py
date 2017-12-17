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

def parse_commit(commits):
	parsed = []
	for commit in commits:
		tmp = {}
		
		tmp["user_id"] = "-1"
		tmp["message"] = "-1"
		tmp["date"] = "-1"
		
		if commit["committer"]:
			tmp["user_id"] = commit["committer"]["id"]
		
		if commit["commit"]["message"]:
			tmp["message"] = commit["commit"]["message"]
		
		if commit["commit"]["author"]["date"]:
			tmp["date"] = commit["commit"]["author"]["date"]
			
		parsed.append(tmp)
	return parsed

def save_repo_commits(repo, output_loc):
	completed_repos = os.listdir("commit_statements")
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
	for i in range(1,num_pages):
		if(i%int(num_pages/20) == 0):
			print("page " + str(i) + " of " + str(num_pages))
		tail = "?client_id=7295f7c92c892216de7b&client_secret=388edda4532c9499dbe16b78f876e76883e54fc8&page=" + str(i)
		r = requests.get('https://api.github.com/repos/' + repo + '/commits' + tail)
		requests_left = int(r.headers["X-RateLimit-Remaining"])
		if requests_left < 10:
			print("sleeping for 1 hour: " + str(datetime.datetime.now().time()))
			time.sleep(3600)
		
		if(r.ok):
			commits = json.loads(r.text or r.content)
			parsed_commits.append(parse_commit(commits))
	
	output_file.write(json.dumps(parsed_commits, indent=4, sort_keys=True))
	
def get_repo_stars():
	star_list = {}
	output_file = open("stars.txt", "w")
	lists = ["c", "java", "c++", "ruby", "python", "main"]
	for l in lists:
		repo_list = get_repo_list(l)
		for repo in repo_list:
			print(repo)
			r = requests.get('https://api.github.com/repos/' + repo + '?client_id=7295f7c92c892216de7b&client_secret=388edda4532c9499dbe16b78f876e76883e54fc8')
			r_json = json.loads(r.text)
			star_list[repo.replace("/","_")] = r_json["stargazers_count"]
			
	output_file.write(json.dumps(star_list, indent=4, sort_keys=True))
			
def run():
	authenticate()
	output_dir = "commit_statements/"
	lists = ["c", "java", "c++", "ruby", "python", "main"]
	for l in lists:
		repo_list = get_repo_list(l)
		for repo in repo_list:
			try:
				save_repo_commits(repo, output_dir)
			except:
				print(repo + " did not finish")
				continue
	
if __name__ == "__main__":
	#run()
	get_repo_stars()