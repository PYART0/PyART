import os

def get_file_path(root_path,file_list,dir_list):
	dir_or_files = os.listdir(root_path)
	#print 1,dir_or_files
	for dir_file in dir_or_files:
		dir_file_path = os.path.join(root_path,dir_file)
		if os.path.isdir(dir_file_path):
			dir_list.append(dir_file_path)
			get_file_path(dir_file_path,file_list,dir_list)
		else:
			file_list.append(dir_file_path)
	#print 3,file_list
	return file_list

def get_cts():
	tokens_in_transcion_count={} #N(ti)
	changes_count={} #N(ci)
	changes_no={} #For N(c,ci)
	tokens_in_sctokens_no={} #For N(c,ti),record line number
	root_path='/home/user/apirec1/cts/'
	file_list=dir_list=[]
	cfiles=get_file_path(root_path,file_list,dir_list)
	file_tag=1
	for file in cfiles:
		with open(file) as f:
			lines=f.readlines()
		for i in range(0,len(lines)):
			line=lines[i].strip()
			if line=='':
				continue
			transcion=line.split('__SPLIT_FOR_TOKEN__')[0]
			sctokens=line.split('__SPLIT_FOR_TOKEN__')[1]
			changes=transcion.split('__#AND#__')
			changes=list(set(changes)) #delete re-occour-index
			for change in changes:
				if change.strip()=='':
					continue
				if change in changes_count:
				#if changes_count.has_key(change):
					count=changes_count[change]
					changes_count[change]=count+1
				else:
					changes_count[change]=1
				if change in changes_no:
				#if changes_no.has_key(change):
					lineno=str(file_tag)+'_'+str(i+1)
					nos=changes_no[change]
					nos.append(lineno)
					changes_no[change]=nos
				else:
					nos=[]
					lineno=str(file_tag)+'_'+str(i+1)
					nos.append(lineno)
					changes_no[change]=nos
				if '#null' in change:
					continue
				else:
					token_in_change=change.split('#')[-1]
					if token_in_change in tokens_in_transcion_count:
					#if tokens_in_transcion_count.has_key(token_in_change):
						tcount=tokens_in_transcion_count[token_in_change]
						tokens_in_transcion_count[token_in_change]=tcount+1
					else:
						tokens_in_transcion_count[token_in_change]=1
			tokens=sctokens.split('__#AND#__')
			tokens=list(set(tokens))
			for token in tokens:
				if token.strip()=='':
					continue
				if token in tokens_in_sctokens_no:				
				#if tokens_in_sctokens_no.has_key(token):
					lineno=str(file_tag)+'_'+str(i+1)
					tnos=tokens_in_sctokens_no[token]
					tnos.append(lineno)
					tokens_in_sctokens_no[token]=tnos
				else:
					tnos=[]
					lineno=str(file_tag)+'_'+str(i+1)
					tnos.append(lineno)
					tokens_in_sctokens_no[token]=tnos
		file_tag+=1
	
	print(changes_no)
	print(tokens_in_sctokens_no)
	print(tokens_in_transcion_count)
	print(changes_count)
		
get_cts()







