import json 

test = '{"Weight": 70.0}'
test = json.loads(test)

print(test['Weight']) # 70.0