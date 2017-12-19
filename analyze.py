import os
import json

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import wilcoxon, spearmanr, norm
from datetime import datetime

def get_senti_score(pos, neg):
	if pos == 1 and neg == -1:
		return 0
	elif pos < abs(neg):
		return neg
	else:
		return pos

def compare_languages():
	print("****LANGUAGE COMPARISON****")
	languages = ["c", "java", "c++", "ruby", "python"]
	stats = []
	raw_scores = []
	for l in languages:
		l_stats = {}
		l_stats["language"] = l
		scores = []
		repo_list_file = open("repo_lists/" + l + ".txt", "r")
		repos = repo_list_file.read().splitlines()
		num_commits = 0
		for repo in repos:
			message_file = open("from_senti/" + repo.replace("/", "_") + ".txt", "r")
			messages = message_file.read().splitlines()
			for message in messages:
				splt = message.split("\t")
				neg = int(splt[-1])
				pos = int(splt[-2])
				
				scores.append(get_senti_score(pos,neg))
					
				num_commits += 1
		
		l_stats["std"] = np.std(scores)
		l_stats["mean"] = np.mean(scores)
		l_stats["num_commits"] = num_commits
		raw_scores.append(scores)
		stats.append(l_stats)
	
	

			
	output_f = open("analysis/language.txt", "w")
	output_f.write(json.dumps(stats, indent=4, sort_keys=True))
	
	return stats

def time_comparison():
	print("****TIME OF DAY COMPARISON****")
	hour_scores = [[] for i in range(24)]
	weekday_scores = [[] for i in range(7)]
	time_buckets = [[] for i in range(4)]
	
	for filename in os.listdir("from_senti"):
		print(filename)
		senti_file = open("from_senti/" + filename)
		senti_lines = senti_file.read().splitlines()
		base_commits = json.load(open("parsed_commits/" + filename))
		
		for i, commit in enumerate(base_commits):
			splt = senti_lines[i].split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			date = datetime.strptime(commit["date"],  "%Y-%m-%dT%H:%M:%SZ")
			
			hour = date.hour
			day = date.weekday()
			
			score = get_senti_score(pos,neg)
			
			weekday_scores[day].append(score)
			hour_scores[hour].append(score)
			
	
	day_stats = []
	
	
	days_enum = ["mon", "tues", "wed", "thurs", "fri", "sat", "sun"]
	for i, day_scores in enumerate(weekday_scores):
		tmp = {}
		tmp["day"] = days_enum[i]
		tmp["mean"] = np.mean(day_scores)
		tmp["std"] = np.std(day_scores)
		tmp["num_commits"] = len(day_scores)
		day_stats.append(tmp)
		

	for i in range(0, len(weekday_scores)):
		for j in range(i+1, len(weekday_scores)):
			tmp = {}
			tmp["comparison"] = days_enum[i] + " to " + days_enum[j]
			day_1 = weekday_scores[i]
			day_2 = weekday_scores[j]
			
			if len(day_1) < len(day_2):
				day_2 = day_2[:len(day_1)]
			else:
				day_1 = day_1[:len(day_2)]
				
			wilcox = wilcoxon(day_1, day_2, correction = True)
			tmp["rank_test"] = wilcox
			if(wilcox[1] < .002): #If different then show it
				day_stats.append(tmp)
		
	output_f = open("analysis/day_of_week.txt", "w")
	output_f.write(json.dumps(day_stats, indent=4, sort_keys=True))
	
	
	time_buckets[3] = hour_scores[23]
	for i in range(6,12):
		time_buckets[0] = time_buckets[0] + hour_scores[i]
		
	for i in range(12,18):
		time_buckets[1] = time_buckets[1] + hour_scores[i]
		
	for i in range(18,24):
		time_buckets[2] = time_buckets[2] + hour_scores[i]
		
	for i in range(0,6):
		time_buckets[3] = time_buckets[3] + hour_scores[i]
	
	hour_stats = []
	buckets = ["morning", "afternoon", "evening", "night"]
	for i, bucket in enumerate(time_buckets):
		tmp = {}
		tmp["bucket"] = buckets[i]
		tmp["mean"] = np.mean(bucket)
		tmp["std"] = np.std(bucket)
		tmp["num_commits"] = len(bucket)
		hour_stats.append(tmp)
	
	output_f = open("analysis/time_of_day.txt", "w")
	output_f.write(json.dumps(hour_stats, indent=4, sort_keys=True))
	
def project_users(repo):
	commits = open("parsed_commits/" + repo + ".txt", "r")
	commits = json.load(commits)
	users = set()
			
	for commit in commits:
		users.add(commit["user_id"])
	
	return users
	
def project_duration(repo):
	commits = open("parsed_commits/" + repo + ".txt", "r")
	commits = json.load(commits)
	
	last = datetime.strptime(commits[0]["date"],  "%Y-%m-%dT%H:%M:%SZ")
	first = datetime.strptime(commits[-1]["date"],  "%Y-%m-%dT%H:%M:%SZ")
	
	return last.timestamp() - first.timestamp()
	
def project_specific():
	print("****PROJECT SPECIFIC COMPARISON****")
	project_scores = []
	project_details = json.load(open("repoDetails.txt"))

	score_means = []
	stars = []
	for filename in os.listdir("from_senti"):
		tmp = {}
		tmp["project"] = filename[:-4]
		senti_file = open("from_senti/" + filename)
		senti_lines = senti_file.read().splitlines()
		
		scores = []
		for commit in senti_lines:
			splt = commit.split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			scores.append(get_senti_score(pos, neg))
			
		for p in project_details:
			if p["repo_name"] == filename[:-4]:
				tmp["stars"] = p["stars"]
				stars.append(p["stars"])
				break
			
		users = project_users(filename[:-4])
		tmp["num_commits"] = len(scores)
		tmp["mean"] = np.mean(scores)
		tmp["std"] = np.std(scores)
		tmp["num_users"] = len(users)
		tmp["project_duration"] = project_duration(filename[:-4])
		
		
		score_means.append(np.mean(scores))
		
		project_scores.append(tmp)
		
	
	output_f = open("analysis/project_specific.txt", "w")
	output_f.write(json.dumps(project_scores, indent=4, sort_keys=True))
	
	correlation = spearmanr(score_means, stars)
	
	plt.scatter(stars, score_means)
	z = np.polyfit(stars, score_means, 1)
	plt.xlabel("Number of Stars")
	plt.ylabel("Average Sentiment")
	#plt.show()
	
	sum = 0
	for p in project_scores:
		if p["num_commits"] > 731910/55:
			print("above average")
			sum = sum + p["num_commits"]
		
	print(sum)
	#print(correlation)
	
def commit_distribution():

	y = []
	for filename in os.listdir("from_senti/"):
		with open("from_senti/" + filename) as f:
			for i, l in enumerate(f):
				pass
		y.append(i)
	
	
	y = np.sort(y)
	
	print(y)
	x = np.linspace(1, len(y), len(y))
	plt.plot(x,y)
	plt.savefig("analysis/commitDistribution.png")
	plt.clf()
	
def sentiment_over_time(repo):
	print("****TIME OF DAY COMPARISON****")
	
	senti_file = open("from_senti/" + repo + ".txt")

	senti_lines = senti_file.read().splitlines()
	base_commits = json.load(open("parsed_commits/" + filename))
	
	num_commits = 0
	for commit in base_commits:
		num_commits = num_commits + 1 
	
	scores = []
	for i, commit in enumerate(base_commits):
		splt = senti_lines[i].split("\t")
		neg = int(splt[-1])
		pos = int(splt[-2])
		
		date = datetime.strptime(commit["date"],  "%Y-%m-%dT%H:%M:%SZ")
		
		hour = date.hour
		day = date.weekday()
		
		score = get_senti_score(pos,neg)
		scores.append(score)
	
	score_avgs = []
	for i in range(0, len(scores), len(scores)/100):
		chunk = scores[i:i + len(scores)/100]
		score_avgs = sum(chunk)/len(chunk)
	
def project_productivity():
	print("project overall")
	data = open("analysis/project_specific.txt")
	data = json.load(data)
	
	x = []
	y = []
	
	for project in data:
		velocity = project["num_commits"]/project["project_duration"] * 1000000 / project["num_users"]
		x.append(project["mean"])
		y.append(velocity)
		
	plt.scatter(x,y)
	plt.xlabel("average sentiment")
	plt.ylabel("Velocity")
	plt.savefig("analysis/velocity.png")
	plt.clf()
	
	correlation = spearmanr(x, y)
	
	print(correlation)
	
	
def project_productivity_weekly():
	print("project weekly")
	data = open("analysis/project_specific.txt")
	data = json.load(data)
	
	x = []
	y = []
	
	weekly_velocity = []
	weekly_sentiment = []
	for project in data:
		project_scores = []
		project_times = []
		
		senti_file = open("from_senti_non_abandoned/" + project["project"] + ".txt", "r")
		sentis = senti_file.read().splitlines()
		
		for senti in sentis:
			splt = senti.split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			project_scores.append(get_senti_score(pos,neg))
		
		commit_file = open("non_abandoned/" + project["project"] + ".txt", "r")
		commits = json.load(commit_file)
		commits.reverse()
		project_scores.reverse()
		for commit in commits:
			project_times.append(datetime.strptime(commit["date"],  "%Y-%m-%dT%H:%M:%SZ").timestamp())
		
		
		num_users = project["num_users"]		
		start_time = project_times[0]
		curr_time = project_times[0]
		num_commits = 0
		tmp_sentiment = []
		for i, commit in enumerate(commits):
			curr_time = datetime.strptime(commit["date"],  "%Y-%m-%dT%H:%M:%SZ").timestamp()
			num_commits += 1
			tmp_sentiment.append(project_scores[i])
			if curr_time > start_time + 604800:
				weekly_sentiment.append(sum(tmp_sentiment)/len(tmp_sentiment))
				weekly_velocity.append(num_commits/num_users/50)

				num_commits = 0
				tmp_sentiment = []
				start_time = curr_time
	
	x = []
	y = []
	for i in range(0, len(weekly_sentiment)):
		if weekly_velocity[i] < 3:
			x.append(weekly_sentiment[i])
			y.append(weekly_velocity[i])
	
	plt.scatter(x,y,s=10)
	plt.xlabel("average weekly sentiment")
	plt.ylabel("Velocity")
	plt.savefig("analysis/velocity_weekly.png")
	plt.clf()
	
	correlation = spearmanr(x, y)
	print(correlation)


def user_productivity():
	print("user productivity")
	data = open("analysis/project_specific.txt")
	data = json.load(data)
	
	x = []
	y = []
	
	user_velocity = []
	weekly_sentiment = []
	
	users = {}
	for project in data:
		project_scores = []
		
		senti_file = open("from_senti/" + project["project"] + ".txt", "r")
		sentis = senti_file.read().splitlines()
		
		scores = []
		for senti in sentis:
			splt = senti.split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			scores.append(get_senti_score(pos,neg))
		
		commit_file = open("parsed_commits/" + project["project"] + ".txt", "r")
		commits = json.load(commit_file)
		for i, commit in enumerate(commits):
			user = str(commit["user_id"])
			time = datetime.strptime(commit["date"],  "%Y-%m-%dT%H:%M:%SZ").timestamp()
			score = scores[i]
			data = [time, score]
			if not user in users.keys():
				users[user] = [data]
			else:
				users[user].append(data)

	for key, data in users.items():
		if len(data) <= 20:
			continue
		
		duration = data[0][0] - data[-1][0]
		velocity = len(data)/duration * 100
		scores = [d[1] for d in data]
		avg_score = sum(scores)/len(data)
		
		if velocity < .0001 or velocity > .3:
			continue
		
		x.append(avg_score)
		y.append(velocity)
	
	
	plt.scatter(x,y,s=10)
	plt.xlabel("user average sentiment")
	plt.ylabel("Velocity")
	plt.savefig("analysis/user_sentiment.png")
	plt.clf()
	
	correlation = spearmanr(x, y)
	print(correlation)
	
def work_distribution():
	print("work distribution")
	data = open("analysis/project_specific.txt")
	data = json.load(data)
	
	x = []
	y = []
	
	user_velocity = []
	weekly_sentiment = []
	
	for project in data:
		users = {}
		
		senti_file = open("from_senti/" + project["project"] + ".txt", "r")
		sentis = senti_file.read().splitlines()
		
		scores = []
		for senti in sentis:
			splt = senti.split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			scores.append(get_senti_score(pos,neg))
		
		commit_file = open("parsed_commits/" + project["project"] + ".txt", "r")
		commits = json.load(commit_file)
		for i, commit in enumerate(commits):
			user = str(commit["user_id"])
			time = datetime.strptime(commit["date"],  "%Y-%m-%dT%H:%M:%SZ").timestamp()
			score = scores[i]
			data = [time, score]
			if not user in users.keys():
				users[user] = [data]
			else:
				users[user].append(data)
	
		total_commits = len(commits)
		for key, data in users.items():
			if len(data) <= 20:
				continue
			
			scores = [d[1] for d in data]
			avg_score = sum(scores)/len(data)

			user_commits = len(scores)
			
			
			
			x.append(avg_score)
			y.append(user_commits/total_commits * 100)
	
	
	plt.scatter(x,y,s=10)
	plt.xlabel("user average sentiment")
	plt.ylabel("Percent of Work")
	plt.savefig("analysis/workload_distribution.png")
	plt.clf()
	
	correlation = spearmanr(x, y)
	print(correlation)
	
def normal_from_data():
	non_abandoned_scores = []
	for filename in os.listdir("from_senti_non_abandoned/"):
		print(filename)
		senti_file = open("from_senti_non_abandoned/" + filename)
		senti_lines = senti_file.read().splitlines()
		base_commits = json.load(open("non_abandoned/" + filename))
		
		for i, commit in enumerate(base_commits):
			splt = senti_lines[i].split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			non_abandoned_scores.append(get_senti_score(pos, neg))
	
	data = non_abandoned_scores

	# Fit a normal distribution to the data:
	mu, std = norm.fit(data)

	# Plot the histogram.
	plt.hist(data, bins=7, normed=True, alpha=0.0, color='g')

	# Plot the PDF.
	xmin, xmax = plt.xlim()
	x = np.linspace(xmin, xmax, 200)
	p = norm.pdf(x, mu, std)
	plt.plot(x, p, 'k', linewidth=2)
	plt.xlabel("Sentiment")
	title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
	plt.title(title)
	
def normal_from_data_abandoned():
	non_abandoned_scores = []
	for filename in os.listdir("from_senti"):
		print(filename)
		senti_file = open("from_senti/" + filename)
		senti_lines = senti_file.read().splitlines()
		base_commits = json.load(open("abandoned/" + filename))
		
		for i, commit in enumerate(base_commits):
			splt = senti_lines[i].split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			non_abandoned_scores.append(get_senti_score(pos, neg))
	
	data = non_abandoned_scores

	# Fit a normal distribution to the data:
	mu, std = norm.fit(data)

	# Plot the histogram.
	plt.hist(data, bins=7, normed=True, alpha=0.0, color='g')

	# Plot the PDF.
	xmin, xmax = plt.xlim()
	x = np.linspace(xmin, xmax, 200)
	p = norm.pdf(x, mu, std)
	plt.plot(x, p, 'r', linewidth=2)
	title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
	plt.title(title)
	plt.savefig("analysis/normal_non_abandoned.png")
	plt.show()
	
def project_abandon_over_time():
	print("abandon percentile")
	data = open("analysis/project_specific.txt")
	data = json.load(data)
	
	x = []
	y = []
	
	weekly_velocity = []
	weekly_sentiment = []
	for project in data:
		project_scores = []
		project_times = []
		
		senti_file = open("from_senti_non_abandoned/" + project["project"] + ".txt", "r")
		sentis = senti_file.read().splitlines()
		
		for senti in sentis:
			splt = senti.split("\t")
			neg = int(splt[-1])
			pos = int(splt[-2])
			
			project_scores.append(get_senti_score(pos,neg))
		if len(project_scores) < 90:
			continue
		commit_file = open("non_abandoned/" + project["project"] + ".txt", "r")
		commits = json.load(commit_file)
		commits.reverse()
		project_scores.reverse()

		project_percent_sentiment = []
		for i, score in enumerate(project_scores):
			if i%int(len(project_scores)/50) == 0:
				project_percent_sentiment.append(score)

				
		weekly_sentiment.append(project_percent_sentiment)

	x = np.linspace(1,48,48)
	y = []
	for i in range(0, 48):
		tmp = [sent[i] for sent in weekly_sentiment]
		y.append(sum(tmp)/len(tmp))
	
	plt.scatter(x,y,s=10)
	plt.xlabel("average weekly sentiment")
	plt.ylabel("Velocity")
	plt.savefig("analysis/abandon_percentile.png")
	plt.clf()
	
	correlation = spearmanr(x, y)
	print(correlation)	
	
if __name__ == "__main__":
	#compare_languages()
	#time_comparison()
	normal_from_data()
	normal_from_data_abandoned()