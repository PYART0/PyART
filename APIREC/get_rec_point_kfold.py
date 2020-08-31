import os,time,math,sys,json,re,string,json
from pythonparser1 import parse_file
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

'''
changes_count={} #N(ci)
changes_no={} #For N(c,ci)
'''

def get_sco(cin,cn):
	if not cin in changes_count or not cin in changes_no or not cn in changes_no:
		return 0.0

	ci_num=changes_count[cin]
	ci_pos=changes_no[cin]
	c_pos=changes_no[cn]
	ccis=[x for x in ci_pos if x in c_pos]
	cci_num=len(ccis)
	x=float(ci_num)+1.0
	y=float(cci_num)+1.0
	ret=float(y/x)
	#print wc,tc
	#print cci_num,ci_num,ret
	ret=math.log(ret)
	#sys.exit(0)
	#print ret
	return ret


def in_same_method(cipa,cipb,cpa,cpb,defs):
	#tree=parse_file(wprefile)
	#sys.exit(0)
	iret=0
	for df in defs:
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
	#sys.exit(0)
	#print iret
	return iret

def get_w_scope(wcommit,tc,defs):
	ciposs=wcommit[3]
	cposs=tc[3]
	#print wcommit,tc
	#print defs
	#print ciposs,cposs
	ws=0.5
	for cip in ciposs:
		for cp in cposs:
			cipa=cip.split(',')[0][1:]
			cpa=cp.split(',')[0][1:]
			cipb=cip.split(',')[1][:-1]
			cpb=cp.split(',')[1][:-1]
			#print cipa,ci
			if in_same_method(cipa,cipb,cpa,cpb,defs)==1:
				ws=1.0
	#print ws
	#sys.exit(0)
	return ws

def get_d_scope(dcommit,dc,flows):
	ds=0.5
	#print dcommit,dc
	ciname=dcommit[2]
	if ciname=='null':
		#print ciname
		#sys.exit(-1)
		return ds
	cname=dc[2]
	
	#print flows
	#print cname,ciname
	for flow in flows:
		if cname in flow and ciname in flow:
			ds=1.0
	#print ds
	#sys.exit(0)
	return ds

def get_tokens(listlines):
	tokens=[]
	for line in listlines:
		if ': ' in line:
			token=line.strip().split(' ')[1]
			tokens.append(token)
	return tokens

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
			print err
			sys.exit(0)
	try:
		cp=cur_token.index(dtc_token)
	except Exception:
		try:
			cp=pre_token.index(dtc_token)
		except Exception as err:
			print err
			sys.exit(0)
	dis=abs(wp-cp)+1.0
	#print 'distance',dis
	#print wp,cp,dis
		
	return dis
	

def get_change_score(wcs,tc,defs,flows,pre_token,cur_token):
	#root_path='/home/user/APIREC/changes2/'
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

def get_cur_tokens():
	tokens=[]
	with open('/home/user/APIREC/ast_cur.json') as f:
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
'''
tokens_in_transcion_count={} #N(ti)
changes_count={} #N(ci)
changes_no={} #For N(c,ci)
tokens_in_sctokens_no={} #For N(c,ti),record line number
'''

def get_token_sco(token,tc):
	#root_path='/home/user/APIREC/cts/'
	#file_list=dir_list=[]
	#cfiles=get_file_path(root_path,file_list,dir_list)
	#ti_num=1.0
	#cti_num=0.0
	change=tc[0]+'#'+tc[1]+'#'+tc[2]

	if not  token in tokens_in_transcion_count or not token in tokens_in_sctokens_no or not change in changes_no:
		return 0.0
	ti_num=tokens_in_transcion_count[token]
	
	change_pos=changes_no[change]
	token_pos=tokens_in_sctokens_no[token]
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
		print err
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
			print err
			sys.exit(0)
	try:
		cp=cur_token.index(cps)
	except Exception:
		try:
			cp=pre_token.index(cps)
		except Exception as err:
			#return 1000000.0
			print err
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
		'''
		if not token[0] in tokens_in_transcion_count:
			continue
		if not token[0] in tokens_in_sctokens_no:
			continue
		'''
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
	#print("Top-k:",top1,top2,top3,top4,top5,top10,top20,len(arr))
	print("Top-k:",tp1,tp2,tp3,tp4,tp5,tp10,tp20)

def get_candidates():
	cans=[]
	for key in changes_count.keys():
		if 'insert-node#attr#' in key:
			label=key.split('#')[-1]
			cans.append(label)
	return cans	

def get_time(tis):
	ti=0.0
	for t in tis:
		ti+=t
	st=float(ti/len(tis))
	print "Avg.time: ",st

def get_cts():
	global tokens_in_transcion_count,changes_count,changes_no,tokens_in_sctokens_no
	root_path='/home/user/APIREC/cts/'
	file_list=dir_list=[]
	cfiles=get_file_path(root_path,file_list,dir_list)
	file_tag=1
	for file in cfiles:
		with open(file) as f:
			alllines=f.read()
		lines=alllines.split('\n')
		#print(file)
		#print(len(lines))

		#global k_fold_len
		#k_fold_len=9*len(lines)/10
		
		for i in range(0,1997):
			#if ''
			line=lines[i].strip()
			if line=='':
				continue
			#print line
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
				if token in tokens_in_transcion_count:
					#if tokens_in_transcion_count.has_key(token_in_change):
					tcount=tokens_in_transcion_count[token]
					tokens_in_transcion_count[token]=tcount+1
				else:
					tokens_in_transcion_count[token]=1


		file_tag+=1
	
	#print(changes_no)
	#print(tokens_in_sctokens_no)
	#print(tokens_in_transcion_count)
	#print(changes_count)	



def write_list_to_json(list, json_file_name, json_file_save_path):

    os.chdir(json_file_save_path)
    with open(json_file_name, 'w+') as  f:
        json.dump(list, f)



CUREENT_PROJ='httpie'
TRAIN_NUM=585


os.system('PATH=/$PATH/://Tmp2')

with open('/home/user/APIREC/log_test/'+CUREENT_PROJ+'_log.txt','r') as f:
	lines=f.readlines()


error=0
success=0
ranks=[]
cranks=[]
tranks=[]
branks=[]
times=[]

tokens_in_transcion_count={} #N(ti)
changes_count={} #N(ci)
changes_no={} #For N(c,ci)
tokens_in_sctokens_no={} #For N(c,ti),record line number

#k_fold_len=0
get_cts()

candidates=get_candidates()
#print candidates
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
change_scores={}
token_scores={}


for line in lines:
	ls=line.split(' ')
	if 'commit' in line and len(ls)==2:
		#if len(whole_cs)>0:
			#print whole_cs
		whole_cs=[]
		gcommit=ls[1]
		num=num+1
		idd=0		
		if num == TRAIN_NUM:
			os.chdir('/home/user/APIREC/trainset/proj/'+CUREENT_PROJ)
			os.system('git reset --hard '+gcommit)
		elif num > TRAIN_NUM:
			#os.system('rm -r /home/user/APIREC/Tmp2')
			os.system('mkdir /home/user/APIREC/Tmp2/'+str(num))
			os.system('cp -r /home/user/APIREC/trainset/proj/'+CUREENT_PROJ+' /home/user/APIREC/Tmp2/'+str(num))
			#os.system('cp -r /home/user/APIREC/trainset/proj/'+CUREENT_PROJ+' /home/user/APIREC/Tmp2')
			os.chdir('/home/user/APIREC/trainset/proj/'+CUREENT_PROJ)
			os.system('git reset --hard '+gcommit)
	elif num < TRAIN_NUM:
		continue
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
			os.chdir('/home/user/APIREC/gumtree/dist/build/distributions/gumtree-2.1.3-SNAPSHOT/bin')
			#os.system('ls')
			#print num
			#print commit,kind,filea,fileb
			os.system('./gumtree'+' '+'diff'+' '+'/home/user/APIREC/trainset/proj/'+CUREENT_PROJ+fileb+' '+'/home/user/APIREC/Tmp2/'+str(num)+'/'+CUREENT_PROJ+filea+' > /home/user/APIREC/log_test/log_'+CUREENT_PROJ+'/'+str(num)+'_'+str(idd))

			whole_cs=[]
			with open('/home/user/APIREC/log_test/log_'+CUREENT_PROJ+'/'+str(num)+'_'+str(idd)) as f:
				lines=f.read()
			if lines.strip()=='':
				os.system('rm /home/user/APIREC/log_test/log_'+CUREENT_PROJ+'/'+str(num)+'_'+str(idd))
				error+=1
			else:
				success+=1
				print error,success
				tagop=0
				c=""
				lines=lines.strip()
				if "insert-node" in lines and "attr:" in lines:
					with open('/home/user/APIREC/log_test/log_'+CUREENT_PROJ+'/'+str(num)+'_'+str(idd),'w+') as f:
						f.write(lines)
				else:
					kind=filea=fileb=''
					continue
				os.system('./gumtree parse '+'/home/user/APIREC/trainset/proj/'+CUREENT_PROJ+fileb+' > /home/user/APIREC/ast_pre.json')
				os.system('./gumtree parse '+'/home/user/APIREC/Tmp2/'+str(num)+'/'+CUREENT_PROJ+filea+' > /home/user/APIREC/ast_cur.json')
				print '/home/user/APIREC/log_test/log_'+CUREENT_PROJ+'/'+str(num)+'_'+str(idd)
				all_tokens=get_cur_tokens()
				with open('/home/user/APIREC/ast_cur.json') as f:
					alines=f.read()
				all_defs=re.findall('FunctionDef: [a-zA-Z0-9_]+ \[[0-9]+\,[0-9]+\]',alines)
				curfile='/home/user/APIREC/Tmp2/'+str(num)+'/'+CUREENT_PROJ+filea
				with open(curfile) as f:
					gprecode=f.read()
				all_flows=get_current_dataflow2(gprecode,'__all__')
				with open('/home/user/APIREC/ast_pre.json') as f:
					glistlines=f.read()
				gpre_token=re.findall('\[[0-9]+\,[0-9]+\]',glistlines)
				with open('/home/user/APIREC/ast_cur.json') as f:
					gcurlines=f.read()
				gcur_token=re.findall('\[[0-9]+\,[0-9]+\]',gcurlines)


				changes=lines.strip().split('===')
				#print changes
				
				for i in range(0,len(changes)):
					if 'match\n' in changes[i]:
						continue
					elif changes[i].strip()=='':
						continue
					elif '\n---\n' in changes[i]:
						op=changes[i].split('\n---\n')[0].strip()
						#print op
						body=changes[i].split('\n---\n')[1].split('[')[0].strip()
						#print body
						if ': ' in body:
							node=body.split(': ')[0].strip()
							real_label=body.split(': ')[1].strip()
							label=real_label
							if node=='attr' and op=='insert-node':
								
								#print whole_cs
								#print changes[i]
								gposs=re.findall('\[[0-9]+\,[0-9]+\]',changes[i])
								total_scores={}
								change_scores={}
								token_scores={}
								avg_scores={}
								#print len(candidates)
								process_bar = ShowProcess(len(candidates), 'OK')
								#print len(whole_cs)
								start = time.time()
								for labeli in candidates:
									targetc=(op,node,labeli,gposs)
									#print 1
									log_change_score=get_change_score(whole_cs,targetc,all_defs,all_flows,gpre_token,gcur_token)
									#print 2
									log_token_score=get_token_score(targetc,all_tokens,all_defs,all_flows,gpre_token,gcur_token)
									change_score=math.exp(log_change_score)
									token_score=math.exp(log_token_score)
									wc=0.35
									wt=0.65
									#TODO:Need more ops for the value of wc and wt: hill algorithm
									total_score=wc*change_score+wt*token_score
									#print 3
									total_scores[labeli]=total_score
									change_scores[labeli]=change_score
									token_scores[labeli]=token_score
									#print total_scores
									process_bar.show_process()
									#print label,total_score
								end = time.time()
								ti=end - start
								#times.append(ti)

								total_scores=sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
								change_scores=sorted(change_scores.items(), key=lambda x: x[1], reverse=True)
								token_scores=sorted(token_scores.items(), key=lambda x: x[1], reverse=True)
								#print len(total_scores)
								
								rank=1
								for k in total_scores:
									if k[0]==real_label:
										break
									else:
										rank+=1
								ranks.append(rank)
								
								#print ranks
								#print len(ranks)
								
								crank=1
								for k in change_scores:
									if k[0]==real_label:
										break
									else:
										crank+=1
								cranks.append(crank)
								#print cranks
								#print len(ranks)
								
								trank=1
								for k in token_scores:
									if k[0]==real_label:
										break
									else:
										trank+=1
								tranks.append(trank)
								#print tranks
								#print len(tranks)
								xr=min(rank,crank,trank)
								if xr>20:
									branks.append(21)
								else:
									branks.append(xr)
									times.append(ti)
								
								print("Execution Time: ", ti)
								#sys.exit(0)
								#get_results(ranks)
								#get_results(cranks)
								#get_results(tranks)
								get_results(branks)
								#print len(change_scores_total)
								#print len(token_scores_total)
								
										
								
						else:
							node=body
							label='null'
						#print node,label
						poss=re.findall('\[[0-9]+\,[0-9]+\]',changes[i])
						#print poss
						whole_cs.append((op,node,label,poss))
				

			
			idd =idd+1
		kind=filea=fileb=''



#get_results(ranks)
get_time(times)
os.system('rm -rf /home/user/APIREC/log_test/log_'+CUREENT_PROJ+'/*')

#write_list_to_json(change_scores_total, 'change_scores_total.json', '/home/user/APIREC/')
#write_list_to_json(token_scores_total, 'token_scores_total.json', '/home/user/APIREC/')


