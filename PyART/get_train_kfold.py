
import os,re,sys
import importlib
import time,string
#sys.path.append(os.path.abspath("./targetProj/urllib3"))
import get_dataflow
#sys.path.append(os.path.abspath("./naming"))
#from naming import get_score2
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from nltk.tokenize import word_tokenize



def get_module_funcs(modulename):
	rootmodule=''
	try:
		module=importlib.import_module(modulename)
	except Exception:
		if '.' in modulename:
			index=modulename.find('.')
			rootmodule=modulename[:index]
			os.system('pip3 install '+rootmodule)
		else:
			os.system('pip3 install '+modulename)
		try:
			module=importlib.import_module(modulename)
		except Exception as err:
			print(err)
			return {}
	ms=dir(module)
	#if modulename in stdlib or rootmodule in stdlib:
		#global standard_apis
		#standard_apis.extend(ms)
	return {modulename:ms}

def get_alias_funcs(modulename,alias):
	rootmodule=''
	try:
		module=importlib.import_module(modulename)
	except Exception:
		if '.' in modulename:
			index=modulename.find('.')
			rootmodule=modulename[:index]
			os.system('pip3 install '+rootmodule)
		else:
			os.system('pip3 install '+modulename)
		try:
			module=importlib.import_module(modulename)
		except Exception as err:
			print(err)
			return {}
			
	ms=dir(module)
	#if modulename in stdlib or rootmodule in stdlib:
		#global standard_apis
		#standard_apis.extend(ms)
	return {alias:ms}

	

def GetMiddleStr(content,startStr,endStr):
	startIndex = content.index(startStr)
	if startIndex>=0:
		startIndex += len(startStr)
		endIndex = content.index(endStr)
	return content[startIndex:endIndex]

def get_alias_item(modulename,itname,aliasname):
	rootmodule=''
	submodule=''
	global standard_apis
	try:
		module=importlib.import_module(modulename)
	except Exception:
		try:
			if '.' in modulename:
				index=modulename.find('.')
				rootmodule=modulename[:index]
				os.system('pip3 install '+rootmodule)
			else:
				os.system('pip3 install '+modulename)
			module=importlib.import_module(modulename)
		except Exception:
			try:
				submodule=importlib.import_module(modulename+'.'+itname)
				#if modulename in stdlib or rootmodule in stdlib:					
					#standard_apis.extend(dir(submodule))
				return {aliasname:dir(submodule)}
			except Exception as err:
				print(err)
				return {}
	try:
		item=getattr(module,itname)
		#if modulename in stdlib or rootmodule in stdlib:					
			#standard_apis.extend(dir(item))
		return {aliasname:dir(item)}
	except Exception:
		try:
			submodule=importlib.import_module(modulename+'.'+itname)
			#if modulename in stdlib or rootmodule in stdlib:					
				#standard_apis.extend(dir(submodule))
			return {aliasname:dir(submodule)}
		except Exception as err:
			print(err)
			return {}

def get_item_methods(modulename,itname):
	rootmodule=''
	submodule=''
	global standard_apis
	try:
		module=importlib.import_module(modulename)
	except Exception:
		try:
			if '.' in modulename:
				index=modulename.find('.')
				rootmodule=modulename[:index]
				os.system('pip3 install '+rootmodule)
			else:
				os.system('pip3 install '+modulename)
			module=importlib.import_module(modulename)
		except Exception:
			try:
				submodule=importlib.import_module(modulename+'.'+itname)
				#if modulename in stdlib or rootmodule in stdlib:					
					#standard_apis.extend(dir(submodule))
				return {itname:dir(submodule)}
			except Exception as err:
				print(err)
				return {}
	try:
		item=getattr(module,itname)
		#if modulename in stdlib or rootmodule in stdlib:					
			#standard_apis.extend(dir(item))
		return {itname:dir(item)}
	except Exception:
		try:
			submodule=importlib.import_module(modulename+'.'+itname)
			#if modulename in stdlib or rootmodule in stdlib:					
				#standard_apis.extend(dir(submodule))
			return {itname:dir(submodule)}
		except Exception as err:
			print(err)
			return {}

def deal_with_current_module(modulename,file,names):
	#current_file='/home/user/PyART/targetProj/abu/abupy/TLineBu/ABuTLExecute.py'
	current_file=file
	layer=0
	for c in modulename:
		if c=='.':
			layer+=1
		else:
			break
	#print(layer)
	ls7=current_file.split('/')
	newdirs=ls7[:(0-layer)]
	newdir=''
	for d in newdirs:
		newdir+=d+'/'
	realdir=newdir
	#print(realdir)
	newdir=newdir+'end'
	rootdir=GetMiddleStr(newdir,root_path,'/end')
	if modulename=='.':
		rootmodule=re.sub('/','.',rootdir)
	else:
		rootmodule=re.sub('/','.',rootdir)+'.'+modulename[layer:]
	#print("Note!",rootmodule)
	ret={}
	for n in names:
		x=get_item_methods(rootmodule,n)
		ret.update(x)
	return ret

def get_real_module(modulename,file):
	current_file=file
	layer=0
	for c in modulename:
		if c=='.':
			layer+=1
		else:
			break
	#print(layer)
	ls7=current_file.split('/')
	newdirs=ls7[:(0-layer)]
	newdir=''
	for d in newdirs:
		newdir+=d+'/'
	realdir=newdir
	#print(realdir)
	newdir=newdir+'end'
	rootdir=GetMiddleStr(newdir,root_path,'/end')
	if modulename=='.':
		rootmodule=re.sub('/','.',rootdir)
	else:
		rootmodule=re.sub('/','.',rootdir)+'.'+modulename[layer:]
	#print("Note!",rootmodule)
	return rootmodule



def get_module_methods(file):
	modulemethods=[]
	all_candidates={}
	with open(file) as f:
		lines=f.readlines()
	for line in lines:
		line=line.strip()
		#in most cases, we choose to get all fuctions of the module imported directly using inspect
		#maybe need all classes and all methods of the classes in the module
		if re.match('import [a-zA-Z0-9\.\_\,\s]+$',line) and ' as ' not in line:
			#print(1,line)
			modulename=line.split('import')[-1].strip()
			if ',' not in modulename:
				x1=get_module_funcs(modulename)
				all_candidates.update(x1)
			else:
				ls3=modulename.split(',')
				#global all_candidates
				for j in ls3:
					itemname=j.strip()
					x2=get_module_funcs(itemname)
					
					all_candidates.update(x2)
		#should choose another example
		elif re.match('import [a-zA-Z0-9\.\_\,]+ as [a-zA-Z0-9\.\_\,\s]+$',line):
			#print(2,line)
			if ',' not in line:
				modulename=GetMiddleStr(line,'import',' as ').strip()
				alias=line.split(' as ')[-1].strip()
				#print(modulename,alias)
				x3=get_alias_funcs(modulename,alias)
				#global all_candidates
				all_candidates.update(x3)
			#many combing methods, checked by ','
			else:
				body=line.split('import')[-1].strip()
				#print("multias:",body)
				mas=body.split(',')
				#print(mas)
				for ma in mas:
					if ' as ' in ma:
						ls4=ma.split(' as ')
						maname=ls4[0].strip()
						aliasname=ls4[1].strip()
						#print(maname,aliasname)
						x4=get_alias_funcs(maname,aliasname)
						#global all_candidates
						all_candidates.update(x4)
					else:
						maname=ma.strip()
						#print(maname)
						x5=get_module_funcs(maname)
						#global all_candidates
						all_candidates.update(x5)
						
					
		elif re.match('from [a-zA-Z0-9\.\_]+ import [a-zA-Z0-9\_\.\*\,\s]+$',line) and 'as' not in line:
			#print(3,line)
			modulename=GetMiddleStr(line,'from','import').strip()
			itemname=line.split('import')[-1].strip()
			names=[]
			if ',' in itemname:
				ns=itemname.split(',')
				for n in ns:
					names.append(n.strip())
			else:
				names.append(itemname)
			#print(modulename,names)
			if modulename.startswith('.'):
				#print(modulename)
				#print(file)
				x6=deal_with_current_module(modulename,file,names)
				#global all_candidates
				all_candidates.update(x6)
				continue
			'''
			firmname=modulename.split('.')[0]
			if firmname==curmodule:
				print("current module:",modulename)
				deal_with_current_module(modulename,names)
				continue
				#need other ops get all methods defined in modules
				#try1:copy the current proj to root path
			'''
			for n in names:
				x7=get_item_methods(modulename,n)
				#global all_candidates
				all_candidates.update(x7)
				
		elif re.match('from [a-zA-Z0-9\.\_]+ import [a-zA-Z0-9\_\.\*\,]+ as [a-zA-Z0-9\_\.\*\,\s]+$',line):
			#print(4,line)
			modulename=GetMiddleStr(line,'from','import').strip()
			if modulename.startswith('.'):
				#print(modulename)
				#print(4,file)
				modulename=get_real_module(modulename,file)
				#continue
				#print(modulename)
				#need other ops to change the modulename as absmodule
			itemname=line.split('import')[-1]
			#print(modulename,itemname)
			if ',' not in itemname:
				lsx=itemname.split(' as ')
				if len(lsx)<2:
					continue
				itname=lsx[0].strip()
				aliasname=lsx[1].strip()
				x8=get_alias_item(modulename,itname,aliasname)
				#global all_candidates
				all_candidates.update(x8)
			else:
				ls5=itemname.split(',')
				for it in ls5:
					if ' as ' not in it:
						itname=it.strip()
						x9=get_item_methods(modulename,itname)
						#global all_candidates
						all_candidates.update(x9)
					else:
						itname=it.split(' as ')[0].strip()
						aliasname=it.split(' as ')[1].strip()
						x10=get_alias_item(modulename,itname,aliasname)
						#global all_candidates
						all_candidates.update(x10)
			#pass
		#else:
			#print('SyntaxError: invalid syntax')
	#print(all_candidates)
	return all_candidates


def get_caller(rec):
	nrec=re.sub('\(.*\)','',rec)
	pindex=nrec.rfind('.')
	return nrec[:pindex]

def check(newcontext):
	ls=newcontext.split('\n')
	i=0
	for i in range(len(ls)-1,-1,-1):
		if ls[i].strip().startswith('def'):
			break
	nc=''
	for j in range(i,len(ls)):
		nc+=ls[j]+'\n'
	#nc=newcontext
	#print(nc)
	nc=re.sub('\'[\\\[\]\(\)\{\}A-Za-z0-9_\,\:]+\'','',nc)
	nc=re.sub('\"[\\\[\]\(\)\{\}A-Za-z0-9_\,\:]+\"','',nc)
	#TODO:cannot deal with multiple problems,need help
	lk=nc.count('(')
	rk=nc.count(')')
	ll=nc.count('[')
	rl=nc.count(']')
	ld=nc.count('{')
	rd=nc.count('}')
	kc=lk-rk
	lc=ll-rl
	dc=ld-rd
	addc=''
	#print(kc,lc,dc)
	if kc==lc==dc==0:
		return newcontext
	else:
		ks=''
		#print(nc)
		for i in range(0,len(nc)):
			c=nc[i]
			if re.match('[\(\)\[\]\{\}]',c):
				ks+=c				
		#print(ks)
		while('{}' in ks or '[]' in ks or '()' in ks):
			while '()' in ks:
				ks=re.sub('\[\]','',ks)
				ks=re.sub('\{\}','',ks)
				ks=re.sub('\(\)','',ks)
			while '[]' in ks:
				ks=re.sub('\{\}','',ks)
				ks=re.sub('\(\)','',ks)
				ks=re.sub('\[\]','',ks)
			while '{}' in ks:
				ks=re.sub('\[\]','',ks)
				ks=re.sub('\(\)','',ks)
				ks=re.sub('\{\}','',ks)
		#print(ks)
		for i in range(len(ks)-1,-1,-1):
			if ks[i]=='(':
				addc+=')'
			elif ks[i]=='[':
				addc+=']'
			else:
				addc+='}'
		#print(newcontext)
		#sys.exit(0)
		#x=re.sub('return ','',newcontext+addc)
		return newcontext+addc
		

def get_type(finalc,file):
	global id
	lindex=file.rfind('/')
	tmp=file[:lindex]+'/tmp.py'
	#tmp2='tmp'+file[lindex:-3]+str(id)+'.py'
	#print(tmp2)
	id+=1
	with open(tmp,'w+') as f:
		f.write(finalc)


	os.system('pytype '+tmp+' > log1.txt')
	with open('log1.txt') as f:
		lines=f.readlines()
	vtype='None'
	for line in lines:
		if '[reveal-type]' in line:
			tp=line.split(':')[1]
			vtype=re.sub('\[reveal\-type\]','',tp)
			vtype=vtype.strip()
			#print(vtype)
			break
		#if '[python-compiler-error]' in line:
			#print(tmp)
			#sys.exit()
	global Nonenum,Anynum,OKnum
	if vtype=='None':
		#print(tmp)
		#sys.exit()
		Nonenum+=1
	elif vtype=='Any' or vtype=='nothing':
		Anynum+=1
	else:
		OKnum+=1
		#print(tmp)
		#sys.exit()
		
	return vtype


def get_bank(line):
	ip=0
	for ip in range(0,len(line)):
		if line[ip]!=' ':
			break
	return (line[:ip],ip)

def check_try(code,trycache):
	#print(trycache)
	ret=code
	#l=sorted(trycache)
	#print(l)
	for i in range(len(trycache)-1,-1,-1):
		ret+='\n'+trycache[i][0]+'except Exception:\n'+trycache[i][0]+'	'+'pass'
	return ret



def get_item_funcs(rootmodule,module,item):
	try:
		module1=importlib.import_module(module)
	except Exception:
		try:
			os.system('pip3 install '+rootmodule)
			module1=importlib.import_module(module)
		except Exception:
			try:
				submodule=importlib.import_module(module+'.'+item)
				return {item:dir(submodule)}
			except Exception as err:
				print(err)
				return {}
	try:
		it=getattr(module1,item)
		return {item:dir(it)}
	except Exception:
		try:
			submodule=importlib.import_module(module+'.'+item)
			return {item:dir(submodule)}
		except Exception as err:
			print(err)
			return {}

def count_all_apis():
	#TODO:count all apis,including module_apis,builtin_apis,proj_apis
	ret=[]
	for k,v in module_apis.items():
		for f in v:
			if (not f.startswith('__')) and (not re.match('[A-Z0-9]+',f)) and (not f in ret):
				ret.append(f)
	#print(ret)
	with open('trainJson/'+CURRENT_PROJ+'.json') as f:
		lines=f.readlines()
	#global current_apis
	for line in lines:
		line=line.strip()
		index=line.rfind('.')
		item=line[index+1:]
		if (not item.startswith('__')) and (not item in ret):
			ret.append(item)
			#current_apis.append(item)
	#global standard_apis
	with open('builtin.txt') as f2:
		l2=f2.readlines()
	for line2 in l2:
		it=line2.strip()
		if not it in ret:
			ret.append(it)
			#standard_apis.append(it)

	return {'all_apis':ret}


def get_all_apis():
	return all_apis

def get_curr_apis(ft,file):
	#print('Note! ',ft,file)
	tmp_file=re.sub(root_path,'',file)
	rmodule=re.sub('\/','.',tmp_file)
	rmodule=rmodule[:-3]
	#print("Note!",rmodule)
	ret=get_item_methods(rmodule,ft)
	#print('Note! ',ret)
	return ret	



def get_typeshed_apis(ft):
	ret=[]
	ft=ft.strip()
	ft=re.sub('\[.*\]','',ft)
	with open('typeshed.txt') as f:
		lines=f.readlines()
	s1='.'+ft+'.'
	s2=ft+'.'
	for line in lines:
		if s1 in line or line.startswith(s2):
			#print('Find typeshed: '+line.strip())
			s3=line.strip()
			index=s3.rfind('.')
			s4=s3[index+1:]
			if not s4 in ret:
				ret.append(s4)
	return ret

#inferred type, caller
def get_candidates(ft,caller,file):
	candidates={}
	global if_from_current_proj
	if_from_current_proj=1
	if ft=='module':
		for k,v in module_apis.items():
			if k==caller:
				candidates={caller:v}
				#print(candidates)
				return candidates
		candidates=get_module_funcs(caller)
	elif ft=='str':
		candidates={caller:dir(str)}
	elif re.match('List\[.*\]',ft):
		candidates={caller:dir(list)}
	elif re.match('Dict\[.*\]',ft):
		candidates={caller:dir(dict)}
	elif ft=='set' or re.match('Set\[.*\]',ft):
		candidates={caller:dir(set)}
	elif ft=='bool':
		candidates={caller:dir(bool)}
	elif re.match('Union\[.*\]',ft):
		ft=ft+'end'
		contents=GetMiddleStr(ft,'Union[',']end')
		contents=re.sub('\[.*\]','',contents)
		lss=contents.split(',')
		tmp=[]
		for k in lss:
			#print('Note!!')
			k=k.strip()
			#print(k)
			tpdic=get_candidates(k,caller,file)
			for k,v in tpdic.items():
				tmp.extend(v)
		if_from_current_proj=0
		candidates={caller:tmp}

	#elif re.match('Match\[.*\]',ft):
		#candidates={caller:dir(re.Match)}
	elif '.' in ft:
		index=ft.rfind('.')
		module=ft[:index]
		item=ft[index+1:]
		rindex=ft.find('.')
		rootmodule=ft[:rindex]
		candidates=get_item_funcs(rootmodule,module,item)
	elif ft=='Any' or ft=='None' or ft=='nothing':
		candidates=get_all_apis()
		if_from_current_proj=0
		#print('Note!All types:')
		#print(candidates)
		return candidates
	elif re.match('[a-zA-Z0-9_]+',ft):
		#since in many case, the caller calls funcs defined behind the caller, we copy the original file into python lib to get candidates.
		candidates=get_curr_apis(ft,file)
		#print('Other types: '+ft)
	if len(candidates)==0:
		typeshed_apis=get_typeshed_apis(ft)
		candidates.update({caller:typeshed_apis})
	#else:
		#if_from_current_proj=1
	for k,v in candidates.items():
		dag=[]
		#print('yes')
		#print(v,len(v))
		for j in range(0,len(v)):
			#print(j)
			if not v[j].startswith('__'):
				dag.append(v[j])
		#print("yes")
		#print(dag)
		candidates[k]=dag	
	#print(candidates)
	return candidates


def get_callee(rec):
	nrec=re.sub('\(.*\)','',rec)
	pindex=nrec.rfind('.')
	return nrec[pindex+1:],rec[pindex+1:]

def get_total(w,naming_context,files):
	ret=0.0
	#print(w)
	for fi in files:
		key=w+'##'+fi
		if key in proj_token_count:
			ret+=proj_token_count[key]
	ret+=naming_context.count(w)
	#print(ret)
	#sys.exit(0)
	return ret

def get_conum(w,n,naming_context,files):
	ret=0.0
	for fi in files:
		k1=w+'##'+fi
		k2=n+'##'+fi
		if k1 in proj_token_no and k2 in proj_token_no:
			x1=proj_token_no[k1]
			y1=proj_token_no[k2]
			ctis=[x for x in x1 if x in y1]
			ret+=float(len(ctis))
	return ret

def get_conum_of_line(api,naming_line,naming_context,files):
	del_estr = string.punctuation + string.digits
	replace = " "*len(del_estr)
	tran_tab = str.maketrans(del_estr, replace)
	tmp=naming_line.translate(tran_tab)
	nl=word_tokenize(tmp)
	cs=api.translate(tran_tab)
	wcs=word_tokenize(cs)
	#print(api,wcs,naming_line,nl)
	#sys.exit(0)
	total=0.0
	conum=0.0
	score=0.0
	#print(wcs,nl)
	#TODO:gao fan le !!!!
	for n in nl:
		total=total+get_total(n,naming_context,files)
		#print(1)
		for w in wcs:
			conum+=get_conum(w,n,naming_context,files)
	if total!=0:
		total=float(total)
		conum=float(conum)
		score=float( conum / total )
	return score


#proj_tokens
#proj_depends
def get_line_scores(aps,naming_line,naming_context,file):
	line_scores={}
	tokens=[]
	fi=re.sub('\.py','',file)
	index=fi.rfind('/')
	curname=fi[index+1:]
	#print(curname)
	files=[]
	for k,v in proj_depends.items():
		if k==file:
			continue
		#print(k)
		flag=0
		for imports in v:
			#print
			if curname in imports:
				#print(imports)
				flag=1
				break
		if flag==0:
			#print(proj_tokens[k])
			#sys.exit(0)
			files.append(k)
	#print(tokens)
	for api in aps:
		if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
			#process_bar.show_process()
			continue
		line_ret=get_conum_of_line(api,naming_line,naming_context,files)
		line_scores[api]=line_ret
	return line_scores

def get_total_infile(w,files):
	ret=0.0
	for fi in files:
		key=w+'##'+fi
		if key in proj_token_count:
			ret+=1.0
	return ret

def get_conum_infile(w,item,files):
	ret=0.0
	for fi in files:
		k1=w+'##'+fi
		k2=item+'##'+fi
		if k1 in proj_token_no and k2 in proj_token_no:
			ret+=1.0
	return ret


def get_conum_of_con(api,naming_context,files):
	code=naming_context.strip()
	lines=code.split('\n')
	del_estr = string.punctuation + string.digits
	replace = " "*len(del_estr)
	tran_tab = str.maketrans(del_estr, replace)
	rets=0.0
	for i in range(0,len(lines)):
		tmp=lines[i].translate(tran_tab)
		nl=word_tokenize(tmp)
		cs=api.translate(tran_tab)
		wcs=word_tokenize(cs)
		total=0.0
		conum=0.0
		for n in nl:
			total+=get_total_infile(n,files)
			for w in wcs:
				conum=conum+get_conum_infile(w,n,files)
		if total!=0:
			total=float(total)
			conum=float(conum)
			score=float( conum / total )
			rets+=float(i+1)*score
	context_ret=float(float(rets) / float(len(lines)+1.0))
	return context_ret

def get_conum_scores(aps,naming_context,file):
	conum_scores={}
	fi=re.sub('\.py','',file)
	index=fi.rfind('/')
	curname=fi[index+1:]
	#print(curname)
	files=[]
	for k,v in proj_depends.items():
		if k==file:
			continue
		#print(k)
		flag=0
		for imports in v:
			#print
			if curname in imports:
				#print(imports)
				flag=1
				break
		if flag==0:
			files.append(k)
	for api in aps:
		if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
			continue
		con_ret=get_conum_of_con(api,naming_context,files)
		conum_scores[api]=con_ret
	return conum_scores
	



def get_rec_point(file):
	
	with open(file) as f:
		lines=f.readlines()
		#print(lines)

	precode=''
	trynum=0
	trycache=[]
	kflag=0
	lno=0
	#s=''
	comment_flag=0
	calls=[]
	
	for line in lines:
		#print(line)
		lno+=1
		if line.strip().startswith('#'):
			continue
		if re.match('[bru]*\'\'\'$',line.strip()) or re.match('[bru]*\"\"\"$',line.strip()):
			if comment_flag==0:
				comment_flag=1
			else:
				comment_flag=0
			continue
		elif (re.match('[bru]*\'\'\'',line.strip()) or re.match('[bru]*\"\"\"',line.strip())) and (re.match('.*[bru]*\'\'\'$',line.strip()) or re.match('.*[bru]*\"\"\"$',line.strip())):
			continue
		elif re.match('[bru]*\'\'\'',line.strip()) or re.match('[bru]*\"\"\"',line.strip()) or re.match('.*[bru]*\'\'\'$',line.strip()) or re.match('.*[bru]*\"\"\"$',line.strip()):
			if comment_flag==0:
				comment_flag=1
			else:
				comment_flag=0
			continue
		if comment_flag==1:
			continue
			 
		if 'try:' in line:
			trynum+=1
			trycache.append(get_bank(line))
		elif trynum>0 and ('except' in line or 'finally:' in line):
			(bank,lenth)=get_bank(line)
			for i in range(len(trycache)-1,-1,-1):
				if trycache[i][1]==lenth:
					trynum-=1
					del trycache[i]
		
		recobj=re.findall('[a-zA-Z0-9_\.\[\]]+\.[a-zA-Z0-9\_]+\(.*\)',line)
		#print(recobj)
		if len(recobj)==0:
			precode+=line
			continue
			#print(file)
		#print(recobj)
		rec=recobj[0]
		caller=get_caller(rec)
		#print(caller)
		callee,rcallee=get_callee(rec)
		#print(callee)
		if callee.startswith('__') or re.match('[A-Z0-9_]+$',callee) or callee.strip()=='_':
			precode+=line
			continue
		cp=caller+'.'+callee
		if cp in calls:
			precode+=line
			continue
		else:
			calls.append(cp) 

		i=0
		latest_line=line.replace(rcallee,'unknown_api()')
		#print('NOTE!',latest_line)
		
		tpp=precode.strip()
		if tpp.endswith(','):

			newcontext=tpp[:-1]
			finalc=check(newcontext)
			#print(finalc)
			current_context=finalc+'\n'+latest_line

			prelast=precode.strip().split('\n')[-1]
			for i in range(0,len(prelast)):
				if prelast[i]!=' ':
					break
			finalc+='\n'+line[:i-4]+'reveal_type('+caller+')'
			
		elif tpp.endswith('(') or tpp.endswith('{') or tpp.endswith('['):
			
			newcontext=tpp
			finalc=check(newcontext)
			current_context=finalc+'\n'+latest_line
			
			#print(finalc)
			prelast=precode.strip().split('\n')[-1]
			for i in range(0,len(prelast)):
				if prelast[i]!=' ':
					break
			finalc+='\n'+line[:i]+'reveal_type('+caller+')'

		else:
			for i in range(0,len(line)):
				if line[i]!=' ':
					break
			#print(i)
			#print(line)
			newcontext=tpp
			finalc=check(newcontext)
			finalc+='\n'+line[:i]+'reveal_type('+caller+')'
			current_context=precode+latest_line
	
		if len(trycache)>0:
			finalc=check_try(finalc,trycache)
		#print(finalc)
		#print('[Process[1] : Preprocessing # Getting reommendation point, simple type inference, possible API candidates and current incomplete code context.]')
		#print(file+'#'+str(lno)+'#'+caller+'#'+callee)
		#if '.' in caller:
			#ft='Any'
		#else:
		ft=get_type(finalc,file)
		ft=ft.strip()
	
		print(file+'#'+str(lno)+'#'+caller+':'+ft+'#'+callee)
		print(Nonenum,Anynum,OKnum)

		#print(file+'#'+str(lno)+'#'+caller+':'+ft+'#'+callee)

		apis = get_candidates(ft,caller,file)
		aps=[]
		for k,v in apis.items():
			aps.extend(v)
		if len(aps)==0:
			precode+=line
			continue
		#ss=''
		#for ap in aps:
			#ss=ss+ap+','
		#ss=ss[:-1]+'\n'
		#s=caller+':'+ft+'#'+callee+'\n'	


		print(line.strip(),"#API:",callee,"#TYPE:",ft)
		
		if callee in aps:
			print('IOV')
		else:
			print('OOV')
			aps=[]
			aps.append(callee)
		#print(aps)
		



		#print('[Process[2] : Constructing dataflow hints.]')
		current_dataflow=get_dataflow.get_current_dataflow2(current_context,caller)
		#print(maxflow)
		if len(current_dataflow)==0:
			precode+=line
			continue
		maxflow=max(current_dataflow,key=len)
		#print(maxflow)
		
		
		
		
		#print(maxflow,current_dataflow)
		start = time.time()

		dataflow_scores=get_dataflow.get_dataflow_scores(aps,maxflow,current_dataflow,ft,callee)
		tosim_scores=get_dataflow.get_tosim_scores(aps,maxflow,current_dataflow,ft,callee)

		try:
			naming_line=re.sub(rcallee,'',line)
		except Exception:
			precode+=line
			continue

		#print(dataflow_scores)
		#print(tosim_scores)
			

		naming_context=precode
		
		line_scores=get_line_scores(aps,naming_line,naming_context,file)

		conum_scores=get_conum_scores(aps,naming_context,file)
		
		flag=0
		datas=''
		labels=''
		for api in aps:
			if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
				continue
			if api==callee:
				label='1'
			else:
				label='0'
			#apis.append(api)
			datas+=str(dataflow_scores[api])+','+str(tosim_scores[api])+','+str(line_scores[api])+','+str(conum_scores[api])+'\n'
			labels+=label+'\n'

		with open(datakfile,'a+') as f:
			f.write(datas)		
		with open(labelkfile,'a+') as f:
			f.write(labels)	

		precode+=line


def dealwith(file):
	print('LOAD-FILE:'+file)
	global module_apis,all_apis
	module_apis=get_module_methods(file)
	all_apis=count_all_apis()
	get_rec_point(file)


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



def get_proj_tokens(iret_list):
	global proj_token_count,proj_token_no,proj_depends
	del_estr = string.punctuation + string.digits
	replace = " "*len(del_estr)
	tran_tab = str.maketrans(del_estr, replace)
	#tmp=lines[i].strip().translate(tran_tab)
	#file_label=0
	for file in iret_list:
		#file_label+=1
		with open(file,encoding='ISO-8859-1') as f:
			lines=f.readlines()
		line_label=0
		for i in range(0,len(lines)):
			line_label+=1
			if lines[i].strip()=='':
				continue
			elif re.sub(' ','',lines[i].strip())=='':
				continue
			elif 'import ' in lines[i]:
				if file in proj_depends:
					imports=proj_depends[file]
				else:
					imports=[]
				imports.append(lines[i])
				proj_depends[file]=imports
	
			tmp=lines[i].strip().translate(tran_tab)
			tokens=word_tokenize(tmp)
			for tk in tokens:
				token=tk+'##'+file
				if token in proj_token_count:
					tcount=proj_token_count[token]
				else:
					tcount=0
				tcount+=lines[i].count(tk)
				proj_token_count[token]=tcount
				if token in proj_token_no:
					no=proj_token_no[token]
				else:
					no=[]
				no.append(line_label)
				proj_token_no[token]=no
				
	#print(proj_token_count,proj_token_no)
	#sys.exit(0)			

				

#with open('types/types.txt','w+') as f:
	#f.write('')


filePath='traindata/'
projs=os.listdir(filePath)
print(projs)
#sys.exit(0)
#sps=os.listdir('trainProJson')
#print(sps)
CURRENT_PROJ=''
Nonenum=Anynum=OKnum=0
for proj in projs:
	CURRENT_PROJ=proj
	#if not CURRENT_PROJ+'.json' in sps:
		#continue
	root_path = filePath+proj
	print('LOAD-PROJ:',root_path)

	datakfile='traincsv-1/'+CURRENT_PROJ+'_train_data.csv'
	labelkfile='traincsv-1/'+CURRENT_PROJ+'_train_label.csv'
	#sys.exit()
	
	file_list = dir_list = []
	ret_list=[]
	get_file_path(root_path,file_list,dir_list)
	#print(ret_list)
	#sys.exit(0)

	#proj_tokens={}
	proj_token_count={}
	proj_token_no={}
	proj_depends={}
	get_proj_tokens(ret_list)
	#print(proj_tokens)
	#sys.exit(0)

	module_apis={}

	id=0
	special_flag=0
	if_from_current_proj=0
	callps=[]

	all_apis={}
	#standard_apis=[]
	#current_apis=[]


	times=[]

	#======MAIN FUNC ENTRY======
	for ifile in ret_list:
		dealwith(ifile)

	#os.system('mv '+filePath+proj+' /home/user/APIREC/solved')
