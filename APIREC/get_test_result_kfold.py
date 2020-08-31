import os,time,math,sys,json,re,string,json
#from pythonparser1 import parse_file
from get_dataflow import get_current_dataflow2

class ShowProcess():
    i = 0
    max_steps = 0
    max_arrow = 50
    infoDone = 'done'

    def __init__(self, max_steps, infoDone = 'Done'):
        self.max_steps = max_steps
        self.i = 0
        self.infoDone = infoDone

    def show_process(self, i=None):
        if i is not None:
            self.i = i
        else:
            self.i += 1
        num_arrow = int(self.i * self.max_arrow / self.max_steps)
        num_line = self.max_arrow - num_arrow
        percent = self.i * 100.0 / self.max_steps
        process_bar = '[' + '>' * num_arrow + '-' * num_line + ']'\
                      + '%.2f' % percent + '%' + '\r'
        sys.stdout.write(process_bar)
        sys.stdout.flush()
        if self.i >= self.max_steps:
            self.close()

    def close(self):
        print('')
        print(self.infoDone)
        self.i = 0


def deal_with(c):
	sc=c.split('[')[0].strip()
	operation=node=label=''
	if ':' not in sc:
		ls1=sc.split('#')
		#print sc
		#print ls1
		operation=ls1[0]
		node=ls1[1]
		label='null'
	else:
		ls2=sc.split(':')
		label=ls2[1].strip()
		operation=ls2[0].split('#')[0]
		node=ls2[0].split('#')[1]
	change=operation+'#'+node+'#'+label
	return change

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



def get_tokens(listlines):
	tokens=[]
	for line in listlines:
		if ': ' in line:
			token=line.strip().split(' ')[1]
			tokens.append(token)
	return tokens

'''
def get_distance(dwc,dtc,pre_token,cur_token):
	#print dwc,dtc
	
	#print pre_token
	dwc_tokens=dwc[3]
	dtc_tokens=dtc[3]
	dwc_op=dwc[0]
	#dis=1000000.0
	dwc_token=dwc_tokens[-1]
	dtc_token=dtc_tokens[-1]
	try:
		wp=cur_token.index(dwc_token)
	except Exception:
		try:
			wp=pre_token.index(dwc_token)
		except Exception as err:
			print(err)
			sys.exit(0)
	try:
		cp=cur_token.index(dtc_token)
	except Exception:
		try:
			cp=pre_token.index(dtc_token)
		except Exception as err:
			print(err)
			sys.exit(0)
	dis=abs(wp-cp)+1.0
	#print 'distance',dis
	#print wp,cp,dis
		
	return dis
	

def get_change_score(wcs,tc,defs,flows,pre_token,cur_token):
	#root_path='/root/APIREC/logs/changes2/'
	#file_list=dir_list=[]
	#cfiles=get_file_path(root_path,file_list,dir_list)
	#print 2,cfiles
	c_score=0.0
	lenth=len(wcs)
	cn=tc[0]+'#'+tc[1]+'#'+tc[2]
	for i in range(0,lenth):
		#print i
		cin=wcs[i][0]+'#'+wcs[i][1]+'#'+wcs[i][2]

		co_score=get_sco(cin,cn)
		#print co_score
		w_scope=get_w_scope(wcs[i],tc,defs)
		d_scope=get_d_scope(wcs[i],tc,flows)
		distance=get_distance(wcs[i],tc,pre_token,cur_token)
		#print w_scope,d_scope,distance
		c_score+=float(w_scope*d_scope*co_score/distance)
	#sys.exit(0)
	#print c_score	
	return c_score
'''


def get_cur_tokens():
	tokens=[]
	with open('/root/APIREC/logs/ast_cur.json') as f:
		curlines=f.readlines()

	for cl in curlines:
		ls=cl.strip().split(' ')
		if ': ' in cl and len(ls)>2:
			#print cl
			token=ls[1].strip()
			poss=re.findall('\[[0-9]+\,[0-9]+\]',cl)
			if len(poss)==0:
				continue
			else:
				pos=poss[0]
				tokens.append((token,pos))
	return tokens
	
def get_pre_tokens():
	tokens=[]
	with open('/root/APIREC/logs/ast_pre.json') as f:
		lines=f.read()

	alltokens=[]
	
	tokens=lines.split(']\n')
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
			alltokens.append((tok,pos))
	#print(alltokens)
	#sys.exit()
	return alltokens
	
	
'''

def get_token_sco(token,tc):
	#root_path='/root/APIREC/logs/cts/'
	#file_list=dir_list=[]
	#cfiles=get_file_path(root_path,file_list,dir_list)
	#ti_num=1.0
	#cti_num=0.0
	change=tc[0]+'#'+tc[1]+'#'+tc[2]

	if not  token in tokens_count or not token in tokens_no or not change in changes_no:
		return 0.0
	ti_num=tokens_count[token]
	
	change_pos=changes_no[change]
	token_pos=tokens_no[token]
	#print token,tc
	#print change_pos
	#print token_pos
	ctis=[x for x in change_pos if x in token_pos]
	cti_num=len(ctis)
	x=float(ti_num)+1.0
	y=float(cti_num)+1.0
	ret=float(y/x)
	#print token,tc
	#print cti_num,ti_num,ret
	ret=math.log(ret)
	#print ret
	#sys.exit(0)
	return ret

def get_token_w(tp,cposs,defs):
	#print
	tps=tp.split(',')
	try:
		tpa=tp.split(',')[0][1:]
		tpb=tp.split(',')[1][:-1]
		tpa=float(tpa)
		tpb=float(tpb)
	except Exception as err:
		print(err)
		return 0.5
	#print tp,cposs,defs
	#print tpa,tpb
	token_w=0.5
	for fd in defs:
		fp=re.findall('\[[0-9]+\,[0-9]+\]',fd)[0]
		fpa=fp.split(',')[0][1:]
		fpb=fp.split(',')[1][:-1]
		fpa=float(fpa)
		fpb=float(fpb)
		for pos in cposs:
			#print pos
			cpa=pos.split(',')[0][1:]
			cpb=pos.split(',')[1][:-1]
			#print cpa,cpb
			cpa=float(cpa)
			cpb=float(cpb)
			#print cpa,cpb,tpa,tpb,fpa,fpb 
			if cpa>=fpa and cpb<=fpb and tpa>=fpa and tpb <=fpb:
				token_w=1.0
	#print token_w	
	return token_w
	#sys.exit(0)

def get_token_d(token,cname,flows):
	token_d=0.5
	
	#print flows
	for flow in flows:
		if token in flow and cname in flow:
			token_d=1.0
	#print token,cname
	#print token_d
	#sys.exit(0)
	return token_d

def get_token_distance(tp,cposs,pre_token,cur_token):
	
	cps=cposs[-1]
	#print tp,cps
	try:
		wp=cur_token.index(tp)
	except Exception:
		try:
			wp=pre_token.index(tp)
		except Exception as err:
			#return 1000000.0
			print(err)
			sys.exit(0)
	try:
		cp=cur_token.index(cps)
	except Exception:
		try:
			cp=pre_token.index(cps)
		except Exception as err:
			#return 1000000.0
			print(err)
			sys.exit(0)
	dis=abs(wp-cp)+1.0
	#print dis
	#print 'token distance',dis
	return dis
		

def get_token_score(tc,tokens,defs,flows,pre_token,cur_token):
	
	
	#print tokens
	cname=tc[2]
	cposs=tc[3]
	
	#print defs
	t_score=0.0
	#print len(tokens)
	#print tokens
	for token in tokens:
		#print token
		if token[0].strip()=='':
			continue
		#print 1
		token_sco=get_token_sco(token[0],tc)
		#print 2
		token_w=get_token_w(token[1],cposs,defs)
		#print 3
		token_d=get_token_d(token[0],cname,flows)
		#print 4
		distance=get_token_distance(token[1],cposs,pre_token,cur_token)
		t_score+=float(token_w*token_d*token_sco/distance)
	#print t_score
	return t_score
	#sys.exit(0)
'''

def get_results(arr):
	print(arr)
	top1=0
	top2=0
	top3=0
	top4=0
	top5=0
	top10=0
	top20=0
	for i in range(0,len(arr)):
		if arr[i]==1:
			top1+=1
			top2+=1
			top3+=1
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==2:
			top2+=1
			top3+=1
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==3:
			top3+=1
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==4:
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==5:
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]<=10:
			top10+=1
			top20+=1
		elif arr[i]<=20:
			top20+=1
	top1=float(top1)
	top2=float(top2)
	top3=float(top3)
	top4=float(top4)
	top5=float(top5)
	top10=float(top10)
	top20=float(top20)
	lenth=float(len(arr))
	tp1=float(top1/lenth)
	tp2=float(top2/lenth)
	tp3=float(top3/lenth)
	tp4=float(top4/lenth)
	tp5=float(top5/lenth)
	tp10=float(top10/lenth)
	tp20=float(top20/lenth)
	rlen=len(arr)
	maps=0.0
	for i in range(0,rlen):
		maps+=float(1.0/float(arr[i]))
	maps=float(maps/float(rlen))
	#print("Top-k:",top1,top2,top3,top4,top5,top10,top20,len(arr))
	print("Top-k+mrr:",tp1,tp2,tp3,tp4,tp5,tp10,tp20,maps)

#TODO:
def get_candidates():
	cans=[]
	canfile='/root/APIREC/cts/candidates1.txt'
	with open(canfile) as fi:
		cans=json.load(fi)
	#print(type(cans))
	return cans	

def get_time(tis):
	ti=0.0
	for t in tis:
		ti+=t
	st=float(ti/len(tis))
	print("Avg.time: ",st)

def get_cts():
	global tokens_count,changes_count,changes_no,tokens_no
	root_path='/root/APIREC/cts/cts/'
	file_list=dir_list=[]
	cfiles=get_file_path(root_path,file_list,dir_list)
	file_tag=1
	print(cfiles)
	for file in cfiles:
		with open(file) as f:
			alllines=f.readlines()
		
		for i in range(0,len(alllines)):
			#if ''
			iline=alllines[i].strip()
			if iline=='':
				continue
			#print(iline)
			transcion=iline.split('===&&&===')[0]
			sctokens=iline.split('===&&&===')[1]
			#print(transcion)
			#print(sctokens)
			transcion=json.loads(transcion)
			sctokens=json.loads(sctokens)
			#print(type(transcion))
			#print(sctokens)
			#sys.exit()
			for change in transcion:
				change=tuple(change)
				#print(change)
				#change=changex[0]
				#print(change)
				#sys.exit()
				if change in changes_count:
				#if changes_count.has_key(change):
					count=changes_count[change]
					changes_count[change]=count+1
				else:
					changes_count[change]=1
				
				#sys.exit()
				if change in changes_no:
				#if changes_no.has_key(change):
					lineno=str(file_tag)+'_'+str(i+1)
					nos=changes_no[change]
					nos.add(lineno)
					changes_no[change]=nos
				else:
					nos=set()
					lineno=str(file_tag)+'_'+str(i+1)
					nos.add(lineno)
					changes_no[change]=nos
			#print(changes_count)
			#print(changes_no)
			#sys.exit()
			#print(sctokens)
			for token in sctokens:
				if token.strip()=='':
					continue
				if token in tokens_no:				
				#if tokens_no.has_key(token):
					lineno=str(file_tag)+'_'+str(i+1)
					tnos=tokens_no[token]
					tnos.add(lineno)
					tokens_no[token]=tnos
				else:
					tnos=set()
					lineno=str(file_tag)+'_'+str(i+1)
					tnos.add(lineno)
					tokens_no[token]=tnos
			
				if token in tokens_count:
					#if tokens_count.has_key(token_in_change):
					tcount=tokens_count[token]
					tokens_count[token]=tcount+1
				else:
					tokens_count[token]=1
			#print(tokens_no)
			#print(tokens_count)
			#sys.exit()		
		file_tag+=1
	
		#sys.exit()	
		'''
			try:
				transcion=line.split('__SPLIT_FOR_TOKEN__')[0]
				sctokens=line.split('__SPLIT_FOR_TOKEN__')[1]
			except Exception:
				continue
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

					
			tokens=sctokens.split('__#AND#__')
			tokens=list(set(tokens))
			for token in tokens:
				if token.strip()=='':
					continue
				if token in tokens_no:				
				#if tokens_no.has_key(token):
					lineno=str(file_tag)+'_'+str(i+1)
					tnos=tokens_no[token]
					tnos.append(lineno)
					tokens_no[token]=tnos
				else:
					tnos=[]
					lineno=str(file_tag)+'_'+str(i+1)
					tnos.append(lineno)
					tokens_no[token]=tnos
				if token in tokens_count:
					#if tokens_count.has_key(token_in_change):
					tcount=tokens_count[token]
					tokens_count[token]=tcount+1
				else:
					tokens_count[token]=1

		
		file_tag+=1
	'''
		




def write_list_to_json(list, json_file_name, json_file_save_path):
	jsObj = json.dumps(list)
	with open(json_file_save_path+json_file_name, 'w+') as  f:
		f.write(jsObj)
        
def GetMiddleStr(content,startStr,endStr):
	startIndex = content.index(startStr)
	if startIndex>=0:
		startIndex += len(startStr)
		endIndex = content.index(endStr)
	return content[startIndex:endIndex]
        
        
        
def deal_insert_tree(c):
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
		ret.append((('add',node,label),pos))
	#print(ret)
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
		ret.append((('move',node,label),pos))
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
		ret.append((('delete',node,label),pos))
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
	ret.append((('delete',node,label),pos))
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
	ret.append((('add',node,label),pos))
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
	ret.append((('update',node,label),pos))
	#print(ret)
	return ret
	
def is_recompoint(itcs):
	#print(itcs)
	calls=[]
	attrloads=[]
	attrs=[]
	for cs in itcs:
		#print(cs[0])
		if cs[0][1]=='Call':
			calls.append(cs)
		elif cs[0][1]=='AttributeLoad':
			attrloads.append(cs)
		elif cs[0][1]=='attr':
			attrs.append(cs)
	if len(calls)>0 and len(attrloads)>0 and len(attrs)>0:
		#print(itcs)
		#print(calls)
		#print(attrloads)
		#print(attrs)
		#sys.exit()
		return 1
	else:
		return 0
	#sys.exit()



def get_sco(cin,cn):
	#print(cin,cn)
	#print(changes_count)
	#print(changes_no)
	#sys.exit()
	#with open('/root/APIREC/change_cache.txt') as xf:
		#cacheflow=xf.read()
	#cachedict={}
	#tag=str((cin,cn))
	#if cacheflow.strip()!='':
		#cachedict=json.loads(cacheflow)
		#print(cachedict)
		#if tag in cachedict:
			#ret=float(cachedict[tag])
			#print('yes!',ret)
			#return ret
	xlabel=0
	if not cn in changes_count:
		#print('API not exist!')
		xlabel=1
	if not cin in changes_count:
		#print('CI not exist!')
		xlabel=1
	if xlabel==1:
		return 0.0
	#print('All exist!')
	ci_num=changes_count[cin]
	ci_pos=changes_no[cin]
	c_pos=changes_no[cn]
	ccis=[x for x in ci_pos if x in c_pos]
	cci_num=len(ccis)
	x=float(ci_num)+1.0
	y=float(cci_num)+1.0
	ret=float(y/x)
	ret=math.log(ret)
	#cachedict[tag]=ret
	#print(cachedict)
	#js=json.dumps(cachedict)
	#with open('/root/APIREC/change_cache.txt','w+') as xf:
		#xf.write(js)
	#print(ci_num)
	#print(ci_pos)
	#print(c_pos)
	#print(ccis)
	#print(ret)
	#sys.exit()
	return ret
	
	
def get_token_sco(tin,cn):
	#print(tin,cn)
	#print(changes_count)
	#print(changes_no)
	#sys.exit()
	xlabel=0
	if not cn in changes_count:
		#print('API not exist!')
		xlabel=1
	if not tin in tokens_count:
		#print('ti not exist!')
		xlabel=1
	if xlabel==1:
		return 0.0
	#print('All exist!')
	#with open('/root/APIREC/token_cache.txt') as xf:
		#cacheflow=xf.read()
	#cachedict={}
	#tag=str((tin,cn))
	#if cacheflow.strip()!='':
		#cachedict=json.loads(cacheflow)
		#print(cachedict)
		#if tag in cachedict:
			#ret=float(cachedict[tag])
			#print('yes!',ret)
			#return ret
	ti_num=tokens_count[tin]
	ti_pos=tokens_no[tin]
	c_pos=changes_no[cn]
	ctis=[x for x in ti_pos if x in c_pos]
	cti_num=len(ctis)
	x=float(ti_num)+1.0
	y=float(cti_num)+1.0
	ret=float(y/x)
	ret=math.log(ret)
	#cachedict[tag]=ret
	#js=json.dumps(cachedict)
	#with open('/root/APIREC/token_cache.txt','w+') as xf:
		#xf.write(js)
	#print(ci_num)
	#print(ci_pos)
	#print(c_pos)
	#print(ccis)
	#print(ret)
	#sys.exit()
	return ret
	
	
def in_same_method(cipa,cipb,cpa,cpb,defs):
	#tree=parse_file(wprefile)
	#sys.exit(0)
	iret=0
	for df in defs:
		try:
			pos=re.findall('\[[0-9]+\,[0-9]+\]',df)[0]
			#print pos
			pa=pos.split(',')[0][1:]
			pb=pos.split(',')[1][:-1]
			#print cipa,cipb,cpa,cpb
			#print pa,pb
			cpa=float(cpa)
			cpb=float(cpb)
			cipa=float(cipa)
			cipb=float(cipb)
			pa=float(pa)
			pb=float(pb)
			if cpa>=pa and cpb<=pb and cipa>=pa and cipb<=pb:
				iret=1
		except Exception as err:
			print(err)
	#sys.exit(0)
	#print(iret)
	return iret
	
	
	
def get_w_scope(cp,cip,defs):

	ws=0.5
	cipa=cip.split(',')[0][1:]
	cpa=cp.split(',')[0][1:]
	cipb=cip.split(',')[1][:-1]
	cpb=cp.split(',')[1][:-1]
	#print cipa,ci
	if in_same_method(cipa,cipb,cpa,cpb,defs)==1:
		ws=1.0
	return ws
	
	

def get_w_token(cp,cip,defs):

	ws=0.5
	cipa=cip.split(',')[0][1:]
	cpa=cp.split(',')[0][1:]
	cipb=cip.split(',')[1][:-1]
	cpb=cp.split(',')[1][:-1]
	#print cipa,ci
	if in_same_method(cipa,cipb,cpa,cpb,defs)==1:
		ws=1.0
	#print(cp,cip,ws)
	return ws



def get_d_scope(cname,ciname):
	#print('start!')
	#print(cname)
	#print(ciname)
	ds=0.5
	if ciname=='null':
		return ds

	for flow in all_flows:
		if cname in flow and ciname in flow:
			ds=1.0
			#print(all_flows)
			#print(cname)
			#print(ciname)
			#sys.exit()
	return ds
	
def get_d_token(cname,tiname):
	#print('start!')
	#print(cname)
	#print(ciname)
	ds=0.5

	for flow in all_flows:
		if cname in flow and tiname in flow:
			ds=1.0
			#print(flow)
			#print(cname)
			#print(tiname)
			#sys.exit()
	return ds
	

def get_distance(cp,cip):
	
	try:
		cpp=gcur_token.index(cp)
	except Exception:
		try:
			cpp=gpre_token.index(cp)
		except Exception as err:
			print(err)
			sys.exit(0)
	try:
		cipp=gcur_token.index(cip)
	except Exception:
		try:
			cipp=gpre_token.index(cip)
		except Exception as err:
			print(err)
			sys.exit(0)
	dis=abs(cpp-cipp)+1.0
	#print 'distance',dis
	#print(cpp,cipp,dis)
	return dis
	

	
'''
co_score=get_sco(cin,cn)
#print co_score
w_scope=get_w_scope(wcs[i],tc,defs)
d_scope=get_d_scope(wcs[i],tc,flows)
distance=get_distance(wcs[i],tc,pre_token,cur_token)
#print w_scope,d_scope,distance
c_score+=float(w_scope*d_scope*co_score/distance)
'''
	
def get_change_score(api,pos,tcs,defs):
	#print(api)
	#print(pos)
	#print(tcs)
	#print(tts)
	#print(defs)
	#sys.exit()
	cscore=0.0
	c=('add','attr',api)
	for ci in tcs:	
		co_score=get_sco(ci[0],c)
		w_score=get_w_scope(pos,ci[1],defs)
		d_score=get_d_scope(api,ci[0][2])
		distance=get_distance(pos,ci[1])
		cscore += w_score*d_score*co_score / distance
	#print(co_score,w_score,d_score,distance)
	#print(cscore)
	#sys.exit()
	return cscore
	
	
def get_token_score(api,pos,tts,defs):
#TODO:
	#print(api)
	#print(pos)
	#print(tcs)
	#print(tts)
	#print(defs)
	#sys.exit()
	tscore=0.0
	c=('add','attr',api)
	for ti in tts:
		tipos=ti[1]
		if not re.match('\[[0-9]+\,[0-9]+\]$',tipos):
			#print('ERROR')
			#print(tipos)
			continue
		co_score=get_token_sco(ti[0],c)
		w_score=get_w_token(pos,ti[1],defs)
		d_score=get_d_token(api,ti[0])
		distance=get_distance(pos,ti[1])
		tscore += w_score*d_score*co_score / distance
	#print(co_score,w_score,d_score,distance)
	#print(tscore)
	#sys.exit()
	return tscore


			
	
def get_rec(target,rec,tcs,tts,defs):
	change_scores={}
	token_scores={}
	if target.startswith('_') or re.match('[A-Z0-9_]+$',target) or target.strip()=='_':
		print('Filed Attribute! Ignore!')
		return
	print(target)
	#sys.exit()
	global allranks

	if not target in candidates:								
		print('OOV')
		allranks.append(100)

	else:
		total_scores={}
		change_scores={}
		token_scores={}
		process_bar = ShowProcess(len(candidates), 'OK')
		for labeli in candidates:
			#print 1
			change_score=get_change_score(labeli,rec[1],tcs,defs)
			change_scores[labeli]=change_score
			token_score=get_token_score(labeli,rec[1],tts,defs)
			token_scores[labeli]=token_score
			process_bar.show_process()
			
		change_scores1=change_scores
		token_scores1=token_scores
		change_scores=sorted(change_scores.items(), key=lambda x: x[1], reverse=True)
		token_scores=sorted(token_scores.items(), key=lambda x: x[1], reverse=True)
		crank=1
		for k in change_scores:
			if k[0]==target:
				break
			else:
				crank+=1
		
		print(crank)		
		trank=1
		for k in token_scores:
			if k[0]==target:
				break
			else:
				trank+=1
		print(trank)

		allranks.append(min(crank,trank))
		get_results(allranks)
		
		
		change_scores1['real_label']=target
		token_scores1['real_label']=target	

		
		global change_scores_total,token_scores_total
		change_scores_total.append(change_scores1)
		token_scores_total.append(token_scores1)
		write_list_to_json(change_scores_total, 'train_change_'+CURRENT_PROJ+'.json', '/root/APIREC/logs/trainJson/')
		write_list_to_json(token_scores_total, 'train_token_'+CURRENT_PROJ+'.json', '/root/APIREC/logs/trainJson/')
		
		
		#print(token_scores)
		
		
		
		


'''
log_token_score=get_token_score(targetc,all_tokens,all_defs,all_flows,gpre_token,gcur_token)
change_score=math.exp(log_change_score)
token_score=math.exp(log_token_score)

wc1=0.8
wt1=0.2
#TODO:Need more ops for the value of wc and wt: hill algorithm
total_score=wc1*change_score+wt1*token_score
'''

	
	
def recommend(itcs,ifilecs,iall_tokens,iall_defs):
	calls=[]
	attrloads=[]
	attrs=[]
	for cs in itcs:
		#print(cs[0])
		if cs[0][1]=='Call':
			calls.append(cs)
		elif cs[0][1]=='AttributeLoad':
			attrloads.append(cs)
		elif cs[0][1]=='attr':
			attrs.append(cs)

	#print(itcs)
	#print(calls)
	#print(attrloads)
	#print(attrs)
	recpoints=[]
	
	for call in calls:
		for attrload in attrloads:
			for attr in attrs:
				tmp=call[1].split(',')
				cpa=int(tmp[0][1:])
				cpb=int(tmp[1][:-1])
				tmp=attrload[1].split(',')
				alpa=int(tmp[0][1:])
				alpb=int(tmp[1][:-1])
				tmp=attr[1].split(',')
				apa=int(tmp[0][1:])
				apb=int(tmp[1][:-1])
				if cpa==alpa==apa and alpb == apb and alpb<cpb:
					#print(cpa,cpb,alpa,alpb,apa,apb)
					#print('Recommendation Point!')
					#print(attr)
					recpoints.append(attr)
	print(recpoints)
	for rec in recpoints:
		tmp=rec[1].split(',')
		apa=int(tmp[0][1:])
		tcs=ifilecs
		target=rec[0][2]
		for cs in itcs:
			try:
				tmp2=cs[1].split(',')
				cpa=int(tmp2[0][1:])
				if cpa <= apa	and cs[0][1]!=target:
					tcs.append(cs)
			except Exception as err:
				print(err)
				continue
		tts=[]
		for ts in iall_tokens:
			#print(ts)
			try:
				tmp3=ts[1].split(',')
				tpa=int(tmp3[0][1:])
				if tpa <=apa:
					tts.append(ts)
			except Exception as err:
				print(err)
				continue		
		#print(tcs)
		#print(tts)
		get_rec(target,rec,tcs,tts,iall_defs)
	#sys.exit()
	
	


CURRENT_PROJ='simplejson'

with open('/root/APIREC/logs/'+CURRENT_PROJ+'_log.txt') as f:
	lines=f.readlines()


error=0
success=0
#ranks=[]
#cranks=[]
#tranks=[]
#branks=[]
#aranks=[]
times=[]
allranks=[]

tokens_count={} #N(ti)
changes_count={} #N(ci)
changes_no={} #For N(c,ci)
tokens_no={} #For N(c,ti),record line number

#k_fold_len=0
get_cts()

candidates=get_candidates()
#print(len(candidates))
#sys.exit(0)

gcommit='' #Commit ID
kind=''
filea=''
fileb=''
num=0
idd=0
whole_cs=[] # All changes in the current commit
all_tokens=[]
all_defs=[]
all_flows=[]
gpre_token=[]
gcur_token=[]
change_scores_total=[]
token_scores_total=[]



results={}
nos=set()
count=0

for line in lines:
	ls=line.split(' ')
	if 'commit' in line and len(ls)==2:
		#if len(whole_cs)>0:
			#print whole_cs
		whole_cs=[]
		gcommit=ls[1]
		num=num+1
		idd=0		
		if num == 1:
			os.chdir('/root/APIREC/testdata/'+CURRENT_PROJ)
			os.system('git reset --hard '+gcommit)
			#os.system('mkdir /root/APIREC/test_Tmp/'+str(num))
			#os.system('cp -r /root/APIREC/logs/testdata/'+CURRENT_PROJ+' /root/APIREC/logs/test_Tmp/'+str(num))
		elif num > 1 :
			#os.system('rm -r /root/APIREC/logs/Tmp2')
			#os.system('mkdir /root/APIREC/logs/test_Tmp/'+str(num))
			#os.system('cp -r /root/APIREC/logs/testdata/'+CURRENT_PROJ+' /root/APIREC/logs/test_Tmp/'+str(num))
			os.system('cp -r /root/APIREC/testdata/'+CURRENT_PROJ+' /root/APIREC/Tmp')
			os.chdir('/root/APIREC/testdata/'+CURRENT_PROJ)
			os.system('git reset --hard '+gcommit)




	elif 'index' in line and len(ls)==3:
		kind=line
	elif '--- a' in line and kind!='':
		filea=ls[1][1:-1]
	elif '--- /' in line:
		filea=ls[1][:-1]
	elif '+++ b' in line and kind!='':
		fileb=ls[1][1:-1]
		#print commit
		if num > 1:
			#os.chdir('/root/APIREC/logs/gumtree/dist/build/distributions/gumtree-2.1.3-SNAPSHOT/bin')
			#os.system('ls')
			#print num
			#print commit,kind,filea,fileb
			os.system('gumtree'+' '+'textdiff'+' '+'/root/APIREC/testdata/'+CURRENT_PROJ+fileb+' '+'/root/APIREC/Tmp/'+CURRENT_PROJ+filea+' > /root/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))

			whole_cs=[]
			with open('/root/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd)) as f:
				lines=f.read()
			if lines.strip()=='':
				os.system('rm /root/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))
				error+=1
			else:
				success+=1
				print(error,success)
				tagop=0
				c=""
				lines=lines.strip()
				if "insert-" in lines and "attr:" in lines:
					with open('/root/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd),'w+') as f:
						f.write(lines)
				else:
					kind=filea=fileb=''
					continue
					
					
				os.system('gumtree parse '+'/root/APIREC/testdata/'+CURRENT_PROJ+fileb+' > /root/APIREC/logs/ast_pre.json')
				os.system('gumtree parse '+'/root/APIREC/Tmp/'+CURRENT_PROJ+filea+' > /root/APIREC/logs/ast_cur.json')
				print('/root/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))
				
				all_tokens=get_pre_tokens()
				
				
				
				with open('/root/APIREC/logs/ast_pre.json') as f:
					alines=f.read()
				all_defs=re.findall('FunctionDef: [a-zA-Z0-9_\-]+ \[[0-9]+\,[0-9]+\]',alines)
				#print(all_defs)
				#sys.exit()
				
				curfile='/root/APIREC/Tmp/'+CURRENT_PROJ+filea
				with open(curfile) as f:
					gprecode=f.read()
					
				all_flows=get_current_dataflow2(gprecode,'__all__')
				#print(all_flows)
				#sys.exit()
				
				
				with open('/root/APIREC/logs/ast_pre.json') as f:
					glistlines=f.read()
				gpre_token=re.findall('\[[0-9]+\,[0-9]+\]',glistlines)
				with open('/root/APIREC/logs/ast_cur.json') as f:
					gcurlines=f.read()
				gcur_token=re.findall('\[[0-9]+\,[0-9]+\]',gcurlines)
				#print(gpre_token)
				#print(gcur_token)

				changes=lines.strip().split('===')

				filecs=[]
				for c in changes:
					if 'match\n---\n' in c:
						continue
					elif c.strip()=='':
						continue
					elif 'insert-tree\n---\n' in c:
						itret=deal_insert_tree(c)
						
						if is_recompoint(itret):
							print(c)
							print('/root/APIREC/testdata/'+CURRENT_PROJ+fileb)
							print('/root/APIREC/Tmp/'+CURRENT_PROJ+filea)
							recommend(itret,filecs,all_tokens,all_defs) 
							
						if len(itret)>0:
							filecs.extend(itret)
							
					elif 'insert-node\n---\n' in c:
						inret=deal_insert_node(c)
						if 'attr:' in c:
							print(c)
							print('/root/APIREC/testdata/'+CURRENT_PROJ+fileb)
							print('/root/APIREC/Tmp/'+CURRENT_PROJ+filea)
							sys.exit()
							#recommend(inret,filecs,all_tokens)
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

			idd =idd+1
		kind=filea=fileb=''





