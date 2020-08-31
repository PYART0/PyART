import os


def get_file_path(root_path,file_list,dir_list):
	global ret_list
	dir_or_files = os.listdir(root_path)
	for dir_file in dir_or_files:
		dir_file_path = os.path.join(root_path,dir_file)
		if os.path.isdir(dir_file_path):
			dir_list.append(dir_file_path)
			get_file_path(dir_file_path,file_list,dir_list)
		elif dir_file_path.endswith('.py') and not dir_file_path.endswith('tmp.py'):
			#print(dir_file_path)
			ret_list.append(dir_file_path)
			file_list.append(dir_file_path)
	

projs=os.listdir('data/')
print(projs)
filenums=0
slocs=0

filePath='data/'

for proj in projs:
	CURRENT_PROJ=proj
		
	root_path = filePath+CURRENT_PROJ
	print('LOAD-PROJ:',root_path)
	file_list = dir_list = []
	ret_list=[]
	get_file_path(root_path,file_list,dir_list)
	print(ret_list)
	for file in ret_list:
		filenums+=1
		with open(file) as f:
			lines=f.readlines()
		slocs+=len(lines)
	print(filenums)
	print(slocs)
	



