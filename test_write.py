import os
import json
import traceback
root_path = os.path.dirname(os.path.abspath(__file__))
def add_user_to_private_users_must_ignore_list(id):
	try:
		print('adding user id '+str(id)+' to private_users_must_ignore.txt')
		with open(root_path + '/private_users_must_ignore.csv', 'a') as g:
			g.write(str(id)+'\r')
			g.close()
	except:
		traceback.print_exc()
		print('something went wrong saving to private_users_must_ignore file')
add_user_to_private_users_must_ignore_list(111)
add_user_to_private_users_must_ignore_list(121)
add_user_to_private_users_must_ignore_list(333)