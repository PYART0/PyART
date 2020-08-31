#['match', 'insert-tree', 'delete-tree', 'insert-node', 'delete-node', 'move-tree', 'update-node']

import os,sys,json

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
	
def GetMiddleStr(content,startStr,endStr):
	startIndex = content.index(startStr)
	if startIndex>=0:
		startIndex += len(startStr)
		endIndex = content.index(endStr)
	return content[startIndex:endIndex]
	
#TODO:Extract candidates
def deal_insert_tree(c):
	#print(c)
	ret=[]
	ret1=[]
	try:
		change=GetMiddleStr(c,'---\n',']\nto\n').strip()
	except Exception as err:
		print(err)
		print(c)
		return []
	#print(change)
	cs=change.split(']\n')
	#print(cs)
	for ic in cs:
		ic=ic.strip()
		if ic=='':
			continue
		pindex=ic.rfind(' [')
		pos=ic[pindex+1:]+']'
		#print(pos)
		preinfo=ic[:pindex]
		if ': ' in preinfo:
			findex=preinfo.find(': ')
			node=preinfo[:findex]
			label=preinfo[findex+2:].strip()
		else:
			node=preinfo.strip()
			label='null'
		#print(node,label)
		ret.append(('add',node,label))
		ret1.append((('add',node,label),pos))
	calls=[]
	attrloads=[]
	attrs=[]
	for cs in ret1:
	#print(cs[0])
		if cs[0][1]=='Call':
			calls.append(cs)
		elif cs[0][1]=='AttributeLoad':
			attrloads.append(cs)
		elif cs[0][1]=='attr':
			attrs.append(cs)
	if len(calls)>0 and len(attrloads)>0 and len(attrs)>0:
		global candidates
		for attr in attrs:
			candidates.add(attr[0][2])
	return ret
	#sys.exit(0)
	
def deal_move_tree(c):
	#print(c)
	ret=[]
	try:
		change=GetMiddleStr(c,'---\n',']\nto\n').strip()
	except Exception as err:
		print(err)
		print(c)
		return []
	#print(change)
	cs=change.split(']\n')
	#print(cs)
	for ic in cs:
		ic=ic.strip()
		if ic=='':
			continue
		pindex=ic.rfind(' [')
		pos=ic[pindex+1:]+']'
		#print(pos)
		preinfo=ic[:pindex]
		if ': ' in preinfo:
			findex=preinfo.find(': ')
			node=preinfo[:findex]
			label=preinfo[findex+2:].strip()
		else:
			node=preinfo.strip()
			label='null'
		#print(node,label)
		ret.append(('move',node,label))
	#print(ret)
	return ret
	

def deal_delete_tree(c):
	#print(c)
	ret=[]
	change=c.split('---\n')[1].strip()[:-1]
	#print(change)
	#sys.exit()
	cs=change.split(']\n')
	for ic in cs:
		ic=ic.strip()
		if ic=='':
			continue
		pindex=ic.rfind(' [')
		pos=ic[pindex+1:]+']'
		#print(pos)
		preinfo=ic[:pindex]
		if ': ' in preinfo:
			findex=preinfo.find(': ')
			node=preinfo[:findex]
			label=preinfo[findex+2:].strip()
		else:
			node=preinfo.strip()
			label='null'
		#print(node,label)
		ret.append(('delete',node,label))
	#print(ret)
	#sys.exit()
	return ret
	
def deal_delete_node(c):
	#print(c)
	ret=[]
	change=c.split('---\n')[1].strip()
	#print(change)
	#sys.exit()
	ic=change
	pindex=ic.rfind(' [')
	pos=ic[pindex+1:]
	#print(pos)
	preinfo=ic[:pindex]
	if ': ' in preinfo:
		findex=preinfo.find(': ')
		node=preinfo[:findex]
		label=preinfo[findex+2:].strip()
	else:
		node=preinfo.strip()
		label='null'
	ret.append(('delete',node,label))
	#print(ret)
	return ret
	
	
def deal_insert_node(c):
	#print(c)
	ret=[]
	try:
		change=GetMiddleStr(c,'---\n',']\nto\n')
	except Exception as err:
		print(err)
		print(c)
		return []
	ic=change.strip()+']'
	pindex=ic.rfind(' [')
	pos=ic[pindex+1:]
	#print(pos)
	preinfo=ic[:pindex]
	if ': ' in preinfo:
		findex=preinfo.find(': ')
		node=preinfo[:findex]
		label=preinfo[findex+2:].strip()
	else:
		node=preinfo.strip()
		label='null'
	ret.append(('add',node,label))
	#print(ret)
	return ret

def deal_update_node(c):
	#print(c)
	ret=[]
	try:
		change=GetMiddleStr(c,'---\n',']\nreplace')
	except Exception as err:
		print(err)
		print(c)
		return []
	ic=change.strip()+']'
	pindex=ic.rfind(' [')
	pos=ic[pindex+1:]
	#print(pos)
	preinfo=ic[:pindex]
	if ': ' in preinfo:
		findex=preinfo.find(': ')
		node=preinfo[:findex]
		label=preinfo[findex+2:].strip()
	else:
		node=preinfo.strip()
		label='null'
	ret.append(('update',node,label))
	#print(ret)
	return ret
	
def find_token_from_file(f):
	print(f)
	index=f.rfind('/')
	fno=f[index+1:]
	prefile='/root/apirecm/logs/token_'+CURRENT_PROJ+'/'+fno+'_pre.json'
	#curfile='/root/apirecm/logs/token_airflow/'+fno+'_cur.json'
	#print(prefile,curfile)

	with open(prefile) as f:
		lines1=f.read()
	#with open(curfile) as fc:
		#lines2=fc.read()
	#print(lines1)
	#print(lines2)
	alltokens=[]
	
	tokens=lines1.split(']\n')
	for token in tokens:
		token=token.strip()+']'
		#print(token)
		pindex=token.rfind(' [')
		pos=token[pindex+1:]
		#print(pos)
		preinfo=token[:pindex]
		if ': ' in preinfo:
			findex=preinfo.find(': ')
			tok=preinfo[findex+2:].strip()
			#print(token)
			#sys.exit()
			alltokens.append(tok)
	'''
	tokens2=lines2.split(']\n')
	for token in tokens2:
		token=token.strip()+']'
		#print(token)
		pindex=token.rfind(' [')
		pos=token[pindex+1:]
		#print(pos)
		preinfo=token[:pindex]
		if ': ' in preinfo:
			findex=preinfo.find(': ')
			tok=preinfo[findex+2:].strip()
			#print(token)
			#sys.exit()
			alltokens.append([(tok,pos)])
	#print(alltokens)
	#sys.exit()
	'''
	return alltokens
	



			
rootdir='/root/apirecm/testdata/'
projs=os.listdir(rootdir)
print(projs)
cans=[]

for proj in projs:
	CURRENT_PROJ=proj
	canfile='/root/apirecm/cts/candidates_'+CURRENT_PROJ+'.txt'
	root_path='/root/apirecm/logs/log_'+CURRENT_PROJ
	file_list=dir_list=[]
	cfiles=get_file_path(root_path,file_list,dir_list)
	#print(cfiles)
	count=0
	candidates=set()
	#allcs=[]
	#allts=[]

	#solved=os.listdir('/root/apirecm/cts/cts_airflow/')
	#print(solved)
	#sys.exit()

	ctsfile='/root/apirecm/cts/cts_'+CURRENT_PROJ

	with open(ctsfile,'w+') as pf:
		pf.write('')

	for file in cfiles:
		#gindex=file.rfind('/')
		#gfno=file[gindex+1:]
		#if gfno in solved:
			#continue
		#ctsfile='/root/apirecm/cts/cts_airflow/'+gfno

		with open(file) as f:
			lines=f.read()
		lines=lines.strip()
		if "update-" in lines or "delete-" in lines or "insert-" in lines or "move-" in lines:	
			with open(file,'w+') as f:
				f.write(lines)
		else:
			os.system('rm '+file)
			continue

		filecs=[]
		changes=lines.split('===')
		for c in changes:
			if 'match\n---\n' in c:
				continue
			elif c.strip()=='':
				continue
			elif 'insert-tree\n---\n' in c:
				itret=deal_insert_tree(c)
				if len(itret)>0:
					filecs.extend(itret)
			elif 'insert-node\n---\n' in c:
				inret=deal_insert_node(c)
				if len(inret)>0:
					filecs.extend(inret)
			elif 'delete-tree\n---\n' in c:
				filecs.extend(deal_delete_tree(c))
			elif 'delete-node\n---\n' in c:
				filecs.extend(deal_delete_node(c))
			elif 'update-node\n---\n' in c:
				upret=deal_update_node(c)
				if len(upret)>0:
					filecs.extend(upret)
			elif 'move-tree\n---\n' in c:
				mtret=deal_move_tree(c)
				if len(mtret)>0:
					filecs.extend(mtret)




		filets=find_token_from_file(file)

		csjson=json.dumps(filecs)
		tsjson=json.dumps(filets)
		
		with open(ctsfile,'a+') as f1:
			f1.write(csjson+'===&&&===')
		with open(ctsfile,'a+') as f2:
			f2.write(tsjson+'\n')

		
		print('END')
		print(candidates)
		cans.extend(list(candidates))
		cans=list(set(cans))
		
	cansx=json.dumps(list(cans))
	with open(canfile,'w+') as f:
		f.write(cansx)	
		
	
	
	
	
	
	
	
	
	
	
