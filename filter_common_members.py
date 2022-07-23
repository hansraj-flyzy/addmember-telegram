import os
import json

with open('config.json', 'r', encoding='utf-8') as f:
	config = json.loads(f.read())

# group target
group_target_id = config['group_target']
# group source
group_source_id = config['group_source']

print('target group: '+str(group_target_id))
print('source group: '+str(group_source_id))