import os
import json
import traceback
import datetime
root_path = os.path.dirname(os.path.abspath(__file__))

def logf(msg):
	print(msg)
	now = datetime.datetime.now()
	try:
		with open(root_path + '/logs.txt', 'a') as g:
			g.write(str(now)+'\t'+msg+'\n')
			g.close()
	except:
		traceback.print_exc()
		print('something went wrong saving to log file')

def remove_common(source, target):
	for i in source[:]:
		if i in target:
			source.remove(i)
	return source

logf('\n\n\n-------\nstarted filter_common_members.py')

with open("config.json", "r", encoding="utf-8") as f:
	config = json.loads(f.read())

# group target
group_target_id = config["group_target"]
# group source
group_source_id = config["group_source"]

logf("target group: " + str(group_target_id))
logf("source group: " + str(group_source_id))

accounts = config["accounts"]
folder_session = "session/"

for account in accounts:
	phone = account["phone"]
	path_group_user = (
		root_path + "/data/user/" + phone + "_" + str(group_source_id) + ".json"
	)
	source_group_users = []
	target_group_users = []
	if os.path.isfile(path_group_user):
		with open(path_group_user, encoding="utf-8") as f:
			source_group_users = json.loads(f.read())
	else:
		print("This account with phone " + str(phone) + " is not in source group")
	path_group_user = (
		root_path + "/data/user/" + phone + "_" + str(group_target_id) + ".json"
	)
	if os.path.isfile(path_group_user):
		with open(path_group_user, encoding="utf-8") as f:
			target_group_users = json.loads(f.read())
	else:
		logf("This account with phone " + str(phone) + " is not in target group")

	final_users_to_be_added = remove_common(source_group_users, target_group_users)
	path_file = 'data-filtered/user/' + phone + "_" + str(group_source_id) + '.json'
	with open(
		path_file,
		"w",
		encoding="utf-8",
	) as f:
		json.dump(final_users_to_be_added, f, indent=4, ensure_ascii=False)
