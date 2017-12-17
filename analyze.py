import os
import json

import numpy as np

from scipy.stats import wilcoxon, spearmanr
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
	
def project_specific():
	print("****PROJECT SPECIFIC COMPARISON****")
	project_scores = []
	stars_json = json.load(open("stars.txt"))

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
			
		tmp["num_commits"] = len(scores)
		tmp["mean"] = np.mean(scores)
		tmp["std"] = np.std(scores)
		tmp["stars"] = stars_json[filename[:-4]]
		
		score_means.append(np.mean(scores))
		stars.append(int(stars_json[filename[:-4]]))
		project_scores.append(tmp)
		
	
	output_f = open("analysis/project_specific.txt", "w")
	output_f.write(json.dumps(project_scores, indent=4, sort_keys=True))
	
	correlation = spearmanr(score_means, stars)
	print(correlation)
	
if __name__ == "__main__":
	#compare_languages()
	#time_comparison()
	project_specific()