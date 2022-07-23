import logging
from telethon import sync, TelegramClient, events
from telethon.tl.types import InputPeerChannel
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
import time
import traceback
import datetime
import os
import json

root_path = os.path.dirname(os.path.abspath(__file__))
start_time = datetime.datetime.now()
logging.basicConfig(level=logging.WARNING)

# group object from groups array and id
def get_group_by_id(groups, group_id):
	for group in groups:
		if (group_id == int(group['group_id'])):
			return group
	return None

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

def add_user_to_private_users_must_ignore_list(id):
	try:
		logf('adding user id '+id+' to private_users_must_ignore.txt')
		with open(root_path + '/private_users_must_ignore.csv', 'a') as g:
			g.write(id+'\r\n')
			g.close()
	except:
		traceback.print_exc()
		logf('something went wrong saving to private_users_must_ignore file')

logf('\n\n\n-------\nstarted add_member.py')
logf('root path: '+root_path+'\n')


with open('config.json', 'r', encoding='utf-8') as f:
	config = json.loads(f.read())

# array with accounts[{phone, api_id, api_hash}]
accounts = config['accounts']
logf("Total accounts: " + str(len(accounts))+'\n\n')
folder_session = 'session/'

# group target id
group_target_id = config['group_target']
# group source id
group_source_id = config['group_source']
#date_online_from
from_date_active = '19700101'
if 'from_date_active' in config:
	from_date_active = config['from_date_active']

# list client
clients = []
for index, account in enumerate(accounts):
	api_id = account['api_id']
	api_hash = account['api_hash']
	phone = account['phone']

	client = TelegramClient(folder_session + phone, api_id, api_hash)

	client.connect()

	if client.is_user_authorized():
		logf('account #'+str(index)+' '+phone + ' login success\n\n')
		clients.append({
			'phone': phone,
			'client': client
		})
	else:
		logf('account #'+str(index)+' '+phone + ' login failed\n\n')

filter_clients = []

for my_client in clients:
	phone = my_client['phone']
	path_group = root_path + '/data/group/' + phone + '.json'
	logf('querying group details for client with phone '+phone)
	logf('path: '+path_group)
	if os.path.isfile(path_group):

		with open(path_group, 'r', encoding='utf-8') as f:
			groups = json.loads(f.read())

		current_target_group = get_group_by_id(groups, group_target_id)
		
		if current_target_group:
			group_access_hash = int(current_target_group['access_hash'])
			target_group_entity = InputPeerChannel(group_target_id, group_access_hash)

			path_group_user = root_path + '/data-filtered/user/' + phone + "_" + str(group_source_id) + '.json'
			if os.path.isfile(path_group_user):
				# add target_group_entity key value
				my_client['target_group_entity'] = target_group_entity
				with open(path_group_user, encoding='utf-8') as f:
					my_client['users'] = json.loads(f.read())

				filter_clients.append(my_client)
			else:
				logf('This account with phone ' + str(phone) + ' is not in source group')
		else:
			logf('This account with phone ' + str(phone) + ' is not in target group')
	else:
		logf('This account with phone do not have data. Please run get_data or init_session')

# run
previous_count = 0
count_add = 0

try:
	with open(root_path + '/current_count.txt') as f:
		previous_count = int(f.read())
except Exception as e:
	pass

logf('From index: ' + str(previous_count))
total_client = len(filter_clients)

total_user = filter_clients[0]['users'].__len__()

i = 0
while i < total_user:

	# previous run
	if i < previous_count:
		i += 1
		continue

	# count_add if added 35 user
	if count_add % (35 * total_client) == (35 * total_client - 1):
		msg = 'sleep 15 minute'
		logf(msg)
		time.sleep(15 * 60)
		# time.sleep(2)

	total_client = filter_clients.__len__()
	logf("remain client: " + str(total_client))
	if total_client == 0:
		with open(root_path + '/current_count.txt', 'w') as g:
			g.write(str(i))
			g.close()

		logf('END: accounts is empty')
		break

	current_index = count_add % total_client
	logf("current_index: " + str(current_index))
	current_client = filter_clients[current_index]
	client = current_client['client']
	user = current_client['users'][i]

	if user['date_online'] != 'online' and user['date_online'] < from_date_active:
		i += 1
		logf('User ' + user['user_id'] + ' has time active: ' + user['date_online'] + ' is overdue')
		continue

	target_group_entity = current_client['target_group_entity']

	try:
		logf('checking if user exists in target group')
		logf('Adding member: ' + user['username'] + ' with uid '+user['user_id'])
		user_to_add = InputPeerUser(int(user['user_id']), int(user['access_hash']))
		client(InviteToChannelRequest(target_group_entity, [user_to_add]))
		msg = 'Added member '+ user['username'] + ' with uid '+user['user_id'] +' successfully ;-)'
		logf(msg)
		count_add += 1
		logf('sleep: ' + str(120 / total_client))
		time.sleep(120 / total_client)
		# time.sleep(0.1)

	except PeerFloodError as e:
		traceback.print_exc()
		logf("remove client: " + current_client['phone'])
		msg = "Error Fooling cmnr - PeerFloodError"
		logf(msg)
		client.disconnect()
		filter_clients.remove(current_client)

		# not increate i
		continue
	except UserPrivacyRestrictedError:
		msg = "Error Privacy"
		logf(msg)
		add_user_to_private_users_must_ignore_list(user['user_id'])
		time.sleep(0.2)
	except FloodWaitError as e:
		logf("Error Fooling cmnr - FloodWaitError")
		traceback.print_exc()
		logf("remove client: " + current_client['phone'])
		client.disconnect()
		filter_clients.remove(current_client)
		time.sleep(2)
		continue
	except:
		traceback.print_exc()
		logf("Error other")
		time.sleep(1)
	# break
	logf('\n\n\n')
	i += 1
	with open(root_path + '/current_count.txt', 'w') as g:
		g.write(str(i))
		g.close()
logf("disconnecting")
for cli in clients:
	cli['client'].disconnect()
end_time = datetime.datetime.now()
logf("total: " + str(count_add))
logf("total time: " + str(end_time - start_time))
