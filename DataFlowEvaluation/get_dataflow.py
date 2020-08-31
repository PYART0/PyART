import os
import re
import sys, time
import numpy as np

final=''#global vars to save results of op
fresult=''#global vars to save results of for
fcall=''#global vars to save results of call

def check(newcontext):
	nc=newcontext
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
	while kc>0:
		nc+=')'
		kc-=1
	while lc>0:
		nc+=']'
		lc-=1
	while dc>0:
		nc+='}'
		dc-=1
	'''
	if tryflag==1:
		i=0
		for i in range(0,len(trycache)):
			if trycache[i]!=' ':
				break
		nc=nc+'\n'+trycache[:i]+'except Exception:\n'+trycache[:i]+'	'+'pass'
	'''
	return nc

def recheck(l):
	line=l
	line=re.sub('return ','',line)
	line=re.sub('\[\'.*\'\]','',line)
	line=re.sub('\[\".*\"\]','',line)
	line=re.sub('\(\'.*\'\)','',line)
	line=re.sub('\(\".*\"\)','',line)
	line=re.sub('\[[0-9\.\-\s\:]+\]','',line)
	line=re.sub('\([0-9\.\-\s\:]+\)','',line)
	line=re.sub('\{[0-9\.\-\s\:]+\}','',line)
	line=re.sub('\[.*[\+\:]+.*\]','',line)
	line=re.sub('\+\=','=',line)
	#line=re.sub(' ','',line)
	line=re.sub('r\'.*\'\,*\s*','',line)
	line=re.sub('b\'.*\'\,*\s*','',line)
	line=re.sub('rb\'.*\'\,*\s*','',line)
	line=re.sub('f\'.*\'\,*\s*','',line)
	line=re.sub('\'.*\'\,*\s*','',line)
	line=re.sub('\".*\"\,*\s*','',line)
	line=re.sub('r\".*\"\,*\s*','',line)
	line=re.sub('b\".*\"\,*\s*','',line)
	line=re.sub('rb\".*\"\,*\s*','',line)
	line=re.sub('f\".*\"\,*\s*','',line)
	line=re.sub('\(\)','',line)
	line=re.sub('\{\}','',line)
	line=re.sub('\[\]','',line)
	#line=recheck(line)
	line=line.strip()
	return line	

def del_arg_op(op):
	starti=endi=0
	for i in range(0,len(op)):
		if op[i]=='(':
			starti=i
		elif op[i]==')':
			endi=i
	return op[:starti]+'-->'+op[starti+1:endi]+op[endi+1:len(op)]


def dealarg_for(ty):
	#print "yes!"
	starti=endi=0
	left=right=0
	ret=''
	for i in range(0,len(ty)):
		if ty[i]=='(':
			if left==right:
				starti=i
				left=left+1
			else:
				left=left+1
		elif ty[i]==')':
				if left==right+1:
					endi=i
					right=right+1
						#print left,right,starti,endi
					if starti+1<endi:
						#print "okkk",y[starti+1:endi]+" --> "+y[:starti]
						
						#print "here!",ty,starti+1,endi,left,right
						ret=ret+ty[:starti]+"-->"+ty[starti+1:endi]
						#print ret
						break
				else:
					right=right+1
	#ret=ret[:-3]
	return ret+ty[(endi+1):len(ty)]

def dealarg_call(ty):
	#print "yes!" 
	starti=endi=0
	left=right=0
	ret=''
	for i in range(0,len(ty)):
		if ty[i]=='(':
			if left==right:
				starti=i
				left=left+1
			else:
				left=left+1
		elif ty[i]==')':
				if left==right+1:
					endi=i
					right=right+1
						#print left,right,starti,endi
					if starti+1<endi:
						#print "okkk",y[starti+1:endi]+" --> "+y[:starti]
						
						#print "here!",ty,starti+1,endi,left,right
						ret=ret+ty[:starti]+"-->"+ty[starti+1:endi]+ty[endi+1:len(ty)]
						#print ret
						break
				else:
					right=right+1
	#ret=ret[:-3]
	if ret=='':
		return ty
	else:
		return ret



def dealarg(ty):
	starti=endi=0
	for i in range(0,len(ty)):
		if ty[i]=='(':
			starti=i
			break
	i=len(ty)-1
	while(i>0):
		if ty[i]==')':
			endi=i
			break
		i=i-1
	return ty[:starti]+"-->"+ty[starti+1:endi]+ty[endi+1:len(ty)]

#apart from consdering data-flow relationship, also consider which var is more relevant to target api, so the order of list is inverse to arg.

def dealist(ty):
	starti=endi=0
	for i in range(0,len(ty)):
		if ty[i]=='[':
			starti=i
			break
	i=len(ty)-1
	while(i>0):
		if ty[i]==']':
			endi=i
			break
		i=i-1
	return ty[:starti]+'-->'+ty[starti+1:endi]

def deallist(ty):
	#print "yes"
	starti=endi=0
	for i in range(0,len(ty)):
		if ty[i]=='[':
			starti=i
		elif ty[i]==']':
			endi=i
	return ty[:starti]+"-->"+ty[starti+1:endi]

def del_multi_arg(ty):
	si=ei=0
	for i in range(0,len(ty)):
		if ty[i]=='(':
			si=i
			break
	i=len(ty)-1
	while(i>-1):
		if ty[i]==')':
			ei=i
			break
		i=i-1
	args=ty[si+1:ei]
	#print "args:",args
	larg=args.split(',')
	sarg=''
	for arg in larg:
		if '=' in arg:
			lr=arg.split('=')
			sarg=sarg+lr[1]+'-->'+lr[0]+'|'
		else:
			sarg=sarg+arg+'|'
	sarg=sarg[:-1]
	return sarg+'-->'+ty[:si]
	


def addty(ty,i,lsy):
	ret=''
	#print ty,i,lsy
	if len(lsy)==1:
		ret = ty
		#print "ret:",ret,"\n"
		return ret
	else:
		for j in range(0,i):
			ret=ret+lsy[j]+'-->'
		ret=ret+ty+"-->"
		for j in range(i+1,len(lsy)):
			ret=ret+lsy[j]+'-->'
		ret=ret[:-3]
	#print "ret:",ret,"\n"
	return ret

def delop(op):
	lsop=op.split('-->')
	global final
	for i in range(0,len(lsop)):
		ty=lsop[i]
		if re.match('[_a-zA-Z0-9\.\[\]\|]+\(.*\)',ty) and ',' in ty and '=' in ty:
			#print "yes!",ty
			ty=del_multi_arg(ty)
			#print "multi_arg:",ty
			op=addty(ty,i,lsop)
			#print "new op:",op		
			final=op
			delop(op)
		elif ',' in ty:
			ty=re.sub(',','|',ty)
			#print "a|b:",ty
			op=addty(ty,i,lsop)
			#print "new op:",op		
			final=op
			delop(op)
		elif re.match('[_a-zA-Z0-9\.\[\]\|]+\(.*=.*\)',ty):
			ty=del_arg_op(ty)
			#print "call-op:",ty
			op=addty(ty,i,lsop)
			#print "new op:",op		
			final=op
			delop(op)
		elif '=' in ty:
			lr=ty.split('=')
			ty=lr[1]+'-->'+lr[0]
			#print "deal with op:",ty
			op=addty(ty,i,lsop)
			final=op
			#print "new op:",op
			delop(op)
		elif re.match('[_a-zA-Z0-9\.\[\]]+\(.*\)',ty):
			ty=dealarg_for(ty)
			#print "deal with arg:",ty
			op=addty(ty,i,lsop)
			#print "new op:",op			
			final=op
			delop(op)
		elif re.match('[_a-zA-Z0-9\.\[\]]+\[.*\]',ty):
			ty=dealist(ty)
			#print "deal with list:",ty
			op=addty(ty,i,lsop)
			#print "new op:",op			
			final=op
			delop(op)
		elif '.' in ty:
			ty=re.sub('\.','-->',ty)
			#print "deal with point:",ty
			op=addty(ty,i,lsop)
			#print "new op:",op		
			final=op
			delop(op)

def GetMiddleStr(content,startStr,endStr):
	startIndex = content.index(startStr)
	if startIndex>=0:
		startIndex += len(startStr)
		endIndex = content.index(endStr)
	return content[startIndex:endIndex]


def prex(x):
	x=re.sub(' ','',x)
	if re.match('\(.*,.*\)\,[a-zA-Z0-9_\'\"\(\)|]+',x) or re.match('[a-zA-Z0-9_\'\"\(\)|]+\,\(.*,.*\)',x) or re.match('\(.*,.*\)\,\(.*,.*\)',x):
		x=re.sub('[\(\)]+','',x)
		#print "yes:",x
	return x

def dealtuple(ty):
	my=re.sub(' ','',ty)
	my=my[1:-1]
	lsmy=my.split(",")
	ret=''
	for i in lsmy:
		ret=ret+i+"|"
	ret=ret[:-1]
	#print "ret1:",ret
	return ret

def deald(ty):
	return re.sub(',','|',ty)

def dealcall(ty):
	#print "ty:",ty
	#print "re:",re.sub('\.','-->',ty)
	return re.sub('\.','-->',ty)

def rbl(tempy):
	ls=0
	rs=0
	ln=0
	rn=0
	ret=0
	for i in range(0,len(tempy)):
		if tempy[i]=='(':
			ls=i
			ln+=1
		elif tempy[i]==')':
			rs=i
			rn+=1
			if rn>ln:
				ret=1
				return ret
			elif rs<ls:
				ret=1
				return ret
	return ret


def findcircle_call(tempy):
	global fcall
	if tempy.count('(') != tempy.count(')') or rbl(tempy)!=0:
		#global fcall
		fcall=''
		return
	tempy=recheck(tempy)
	ls=tempy.split('-->')
	for i in range(0,len(ls)):
		ty=ls[i]
		#print ty
		ty=re.sub(' ','',ty)
		if ',' in ty:
			#print 'yes!',ty
			ty=re.sub(',','|',ty)
			#print 'later',ty
			tempy=addty(ty,i,ls)			
			fcall=tempy
			#print 2,ty,tempy
			findcircle_call(tempy)
		elif '.' in ty and not re.match('.*\(.*\..*\).*',ty):
			#print "ty1",ty
			ty=re.sub('\.','-->',ty)
			tempy=addty(ty,i,ls)
			#print 3,ty,tempy
			#global final
			fcall=tempy
			findcircle_call(tempy)
		elif re.match('.*[a-zA-Z0-9_]+\(.*[a-zA-Z0-9_\'\"\(\)\|\-\>\:\[\]\,\.]+\).*',ty) and re.match('.*\(.*[a-zA-Z0-9_]+.*\).*',ty):
			ty=re.sub('\(\)','',ty)
			ty=re.sub('\(\[\]\)','',ty)
			if not (re.match('.*[a-zA-Z0-9_]+\(.*[a-zA-Z0-9_\'\"\(\)\|\-\>\:\[\]\,\.]+\).*',ty) and re.match('.*\(.*[a-zA-Z0-9_]+.*\).*',ty)):
				tempy=addty(ty,i,ls)
				final=tempy
				#print "4.1",ty,tempy
				findcircle_call(tempy)
				continue
			#print ty
			ty=dealarg_call(ty)
			tempy=addty(ty,i,ls)
			#print 4,ty,tempy
			#global final
			fcall=tempy
			findcircle_call(tempy)
		elif '.' in ty :
			#print "ty2",ty
			ty=re.sub('\.','-->',ty)
			tempy=addty(ty,i,ls)
			#print 5,ty,tempy
			#global final
			fcall=tempy
			findcircle_call(tempy)
		elif re.match('[a-zA-Z0-9_]+\[[a-zA-Z0-9_]+\]',ty):
			ty=deallist(ty)
			tempy=addty(ty,i,ls)
			fcall=tempy
			#print 6,ty,tempy
			findcircle_call(tempy)
	#return tempy






def del_call(line):
	#print(line)
	calls=re.findall('[_a-zA-Z0-9\.\[\]\'\"\(\)\{\}\,\:]+\(.*\)',line)
	#print(calls)
	call=''
	if len(calls)>0:
		call=calls[0]
	else:
		return call
	call=re.sub('\(\'.*\'\)','',call)
	call=re.sub('\(\".*\"\)','',call)
	call=re.sub('\[\'.*\'\]','',call)
	call=re.sub('\[\".*\"\]','',call)
	call=re.sub('\(\)','',call)
	call=re.sub('\([0-9]+\)','',call)
	call=re.sub('\[[0-9:\-]+\]','',call)
	call=call.strip()
	call=re.sub(' ','',call)
	call=recheck(call)
	findcircle_call(call)
	#print(fcall,'\n')
	return fcall
	




def findcircle(tempy):
	global fresult

	#print "temp:",tempy
	lsy=tempy.split("-->")
	#print "lsy:",lsy
	for i in range(0,len(lsy)):
		ty=lsy[i]
		ty=ty.strip()
		#print "i:",i,ty
		if re.match(r'\(.*,.*\)',ty):
			#print "matchtuple:",ty
			ty=dealtuple(ty)
			#print "addty"
			tempy=addty(ty,i,lsy)
			fresult=tempy
			#print fresult
			findcircle(tempy)
		elif ',' in ty and '\',\'' not in ty:
			#print "matchmulti"
			#print "2:",ty,i,lsy
			ty=deald(ty)
			tempy=addty(ty,i,lsy)
			#print "yes!",ty,tempy
			fresult=tempy
			#print fresult
			findcircle(tempy)
		elif re.match('.*[a-zA-Z0-9_]+\(.*[a-zA-Z0-9_\'\"\(\)\|\-\>\:]+\).*',ty):
			#print "matcharg:",ty
			ty=dealarg_for(ty)
			#print "addty"
			tempy=addty(ty,i,lsy)
			fresult=tempy
			#print fresult
			#print "1:",ty,i,lsy
			findcircle(tempy)
		elif '.' in ty and '\'\.\'' not in ty:
			#print "matchpoint"			
			ty=dealcall(ty)
			tempy=addty(ty,i,lsy)
			#print "yes!",tempy
			fresult=tempy
			#print fresult
			findcircle(tempy)
		elif re.match('.*\[\'.*\'\].*',ty) or re.match('.*\[\".*\"\].*',ty) or re.match('.*\[[0-9:]+\].*',ty):
			#print "yes:",ty
			tempy=re.sub('\[.*\]','',ty)
			#print "new:",tyy
			fresult=tempy
			#print fresult
			findcircle(tempy)
		#elif re.match('[a-zA-Z0-9_]+',ty):
			#print "result:",tempy,"\n"
			#global fresult
			#print "tempy:",ty,tempy
			#fresult=tempy
			#print lsy
			#if ty==lsy[len(lsy)-1]:
				#break
			#findcircle(tempy)
			#return tempy	
	#fresult=tempy	
	#return tempy




def delfor(line):
	#if re.match('.*\[.*for\s.*\sin\s.*\].*',line):
		#return
	#forp=line.find('for ')
	#print forp
	#print line[forp+4:]
	#ls=line[forp+4:].split(" in ")
	#print ls
	#x=ls[0]
	#if len(ls) < 2:
		#return
	#ls2=ls[1].split(":\n")
	#print ls2
	#y=ls2[0]		
	#print x
	#print y
	ops=re.findall('for\s[_a-zA-Z0-9\.\,\s]+\sin\s[_a-zA-Z0-9\,\.\[\]\(\)\{\}\s]+',line)
	#print(ops)
	s=''
	if len(ops)>0:
		s=ops[0]
		#s=recheck(s)
	else:
		return s
	if s.endswith(','):
		s=s[:-1]
	if (s.endswith(']') and s.count('[')<s.count(']')) or (s.endswith(')') and s.count('(')<s.count(')')) or (s.endswith('}') and s.count('{')<s.count('}')):
		s=s[:-1]
	s=recheck(s)
	if s.strip().endswith('in'):
		return ''
	#print(s)
	try:
		x=GetMiddleStr(s,'for ',' in ')
	except Exception:
		return ''
	#y=GetMiddleStr(line,'in',':')
	x=x.strip()
	y=s.split(' in ')[1].strip()
	#print('x,y')
	#print(x,y)
	#print "x:",x
	#print "START"+"#"+str(num)
	#print(line[:-1])
	y=re.sub(' ','',y)
	x=re.sub(' ','',x)
	x=re.sub('\(\)','',x)
	y=re.sub('\(\)','',y)
	y=re.sub('\[\'.*\'\]','',y)
	y=re.sub('\[\".*\"\]','',y)
	y=re.sub('\(\'.*\'\)','',y)
	y=re.sub('\(\".*\"\)','',y)
	y=re.sub('\[[0-9:]+\]','',y)
	y=re.sub('\([0-9:]+\)','',y)
	y=re.sub('\[.*[\+\:]+.*\]','',y)
	y=re.sub('\+\=','',y)
	y=re.sub('r\'.*\'\,','',y)
	x=re.sub('\[\'.*\'\]','',x)
	x=re.sub('\[\".*\"\]','',x)
	x=re.sub('\(\'.*\'\)','',x)
	x=re.sub('\(\".*\"\)','',x)
	x=re.sub('\[[0-9:]+\]','',x)
	x=re.sub('\([0-9:]+\)','',x)
	x=re.sub('\[.*[\+\:]+.*\]','',x)
	x=re.sub('\+\=','',x)
	x=re.sub('r\'.*\'\,','',x)
	#print(x,y)
	#TODO:meici xu tiao cichu
	y=recheck2(y)
	findcircle(y)
	global fresult
	if fresult=='':
		rety=y
	else:
		rety=fresult
	fresult=''
	x=prex(x)
	findcircle(x)
	if fresult=='':
		retx=x
	else:
		retx=fresult
	
	#print "result:",rety,"-->",retx,"\n"
	fresult=''
	forx=rety+"-->"+retx
	#if forx.count('-->') >10:
		#s="START:\n"+line+rety+"-->"+retx+"\n"+"END\n"
	s2=rety+"-->"+retx+"\n"
	#print(s)
	#print(s2)
	return s2

def finalcheck(s):
	s=re.sub('\*\*','',s)
	s=re.sub('\*args','args',s)
	s=re.sub('[\+\/\*]','|',s)
	s=re.sub('\n','',s)
	if s.count('-->')==1:
		ls=s.split('-->')
		if ls[0]==ls[1]:
			s=''
	return s

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

def recheck2(l):
	line=l
	line=re.sub('return ','',line)
	line=re.sub('\[.*\]','',line)
	line=re.sub('\(.*\)','',line)
	line=re.sub('\{.*\}','',line)
	line=re.sub('\+\=','=',line)
	#line=re.sub(' ','',line)
	line=re.sub('r\'.*\'\,*\s*','',line)
	line=re.sub('b\'.*\'\,*\s*','',line)
	line=re.sub('rb\'.*\'\,*\s*','',line)
	line=re.sub('f\'.*\'\,*\s*','',line)
	line=re.sub('\'.*\'\,*\s*','',line)
	line=re.sub('\".*\"\,*\s*','',line)
	line=re.sub('r\".*\"\,*\s*','',line)
	line=re.sub('b\".*\"\,*\s*','',line)
	line=re.sub('rb\".*\"\,*\s*','',line)
	line=re.sub('f\".*\"\,*\s*','',line)
	#line=recheck(line)
	line=line.strip()
	return line


def get_current_dataflow2(current_context,caller):
	dataflows=[]
	lines=current_context.split('\n')
	#process_bar = ShowProcess(len(lines), 'Start to deal with the file')
	for line in lines:
		if (not caller in line) and (caller!='__all__') :
			continue
		if not ('.' in line and '(' in line):
			continue
		line=line.strip()
		if line == '' or line.endswith('='):
			continue
		#print('NOTE!',line)
		tpline=line
		if line.startswith('#') or line.startswith('def ') or line.startswith('class '):
			continue
		elif 'lambda' in line:
			continue
		elif re.match('.*=\s*[0-9\.\:\-]+',line):
			continue
		line2=re.sub(' ','',line)
		if re.match('.*=\'.*\'.*',line2) or re.match('.*=\".*\".*',line2) or re.match('.*=[0-9\.]+.*',line2) or  re.match('.*=None.*',line2) or re.match('.*=True.*',line2) or re.match('.*=False.*',line2) or "==" in line2 or line2.endswith('='):
			#print('yes!')
			continue
		#print(tpline,line)
		line=re.sub('#.*','',line)
		if '=' in line:
			#print(line)
			#print('yes!')
			line=recheck2(line)
			if line.endswith('='):
				continue
			text = re.compile(r".*[a-zA-Z]$")
			if not text.match(line):
				continue
			ops=re.findall('[_a-zA-Z0-9\.\[\]\"\'\(\)\{\}]+\s*=\s*[_a-zA-Z0-9\.\[\]\"\'\(\)\{\}\*\/\-\%\*\,\=\s\+]+',line)
			if len(ops)==0:
				continue
			line=ops[0]
			line=re.sub('[\+\-\/\*]+','|',line)
			#print('op',tpline,line)
			ls=line.split('=')
			x=ls[0]
			y=ls[1]
			x=re.sub('\.','-->',x)
			y=re.sub('\.','-->',y)
			tf=y+'-->'+x
			#print(tf)
			opps=re.findall('[\(\{\)\}\[\]\'\"]',tf)
			if len(opps)!=0:
				continue
			tf=tf.strip()
			if tf!='' and not tf in dataflows:
				dataflows.append(tf)
		elif re.match('.*for\s.*\sin\s.*',line):
			line=recheck(line)
			#print('FOR_EXPR')
			#print(file,tpline)
			fors=delfor(line)
			#print('FOR DATAFLOW:')
			#print(str(fors),'\n')
			tff=str(fors)
			tff=finalcheck(tff)
			#print('for',tpline)
			#print(tff)
			opps=re.findall('[\(\{\)\}\[\]\'\"]',tff)
			if len(opps)!=0:
				continue
			tff=tff.strip()
			if tff!='' and not tff in dataflows:
				dataflows.append(tff)
			#print(tff)
			#with open('tmp_dataflow/for_expr.txt','a+') as ff:
				#ff.write(file+'#'+str(num)+": "+tpline+'\n'+str(fors)+'\n\n')

		elif re.match('.*[_a-zA-Z0-9\.\[\]\'\"\(\)\{\}\,\:]+\(.*\).*',line) and not line.startswith('def ') and not line.startswith('class '):
			#print(file)
			#print(line,'\n')
			#line=recheck(line)
			#print(line)
			#cas=del_call(line)
			#print('CALL DATAFLOW:')
			#print(cas,'\n')
			#cas=finalcheck(cas)
			calls=re.findall('[_a-zA-Z0-9\.\[\]\'\"\(\)\{\}\,\:]+\(.*\)',line)
			call=''
			if len(calls)>0:
				call=calls[0]
			else:
				continue
			line=recheck2(call)
			line=re.sub('[\+\-\/]+','|',line)
			#print('call',tpline,line)
			cas=re.sub('\.','-->',line)
			#print(cas)
			opps=re.findall('[\(\{\)\}\[\]\'\"]',cas)
			if len(opps)!=0:
				continue
			if not '-->' in cas:
				continue
			cas=cas.strip()
			if cas!='' and not cas in dataflows:
				dataflows.append(cas)
			#print(cas)
			#callflow.append(ls2.strip())
			#with open('tmp_dataflow/call_expr.txt','a+') as fc:
				#fc.write(file+'#'+str(num)+'\n'+line+'\n')	

	#process_bar.show_process()
	newflows=[]
	oldflows=dataflows
	lens=5*len(dataflows)
	used=[0]*lens
	for i in range(0,len(dataflows)):
		#flag=0
		current_flow_end=dataflows[i].split('-->')[-1]
		current_flow_head=dataflows[i].split('-->')[0]
		if current_flow_end==current_flow_head:
			continue
		for j in range(i,len(dataflows)):
			#print(j,len(dataflows))
			current_flow_end=dataflows[i].split('-->')[-1]
			next_flow_head=dataflows[j].split('-->')[0]
			s1=current_flow_end+'|'
			s2='|'+current_flow_end
			s3=next_flow_head+'|'
			s4='|'+next_flow_head
			if current_flow_end == next_flow_head or s1 in next_flow_head or s2 in next_flow_head:
				y=dataflows[j].replace(next_flow_head,'',1)
				#y=re.sub(next_flow_head,'',dataflows[j])
				newflow=dataflows[i]+y
				#print('yes1!')
				#print(i,current_flow_end,next_flow_head,s1,s2)
				#print(next_flow_head)
				#print(dataflows[i])
				#print(dataflows[j])
				#print(y)
				#print(newflow)
				if not newflow in newflows:
					tmp=[i,newflow]
					newflows.append(tmp)
				#if not newflow in dataflows:
					#dataflows.append(newflow)
					#print(newflow)
					#dataflows[i]=newflow
					#print('yes!')
					#print(dataflows[i],' , ',dataflows[j])
					#print(newflow)
					#i=i-1
				#used[j]=1
				#del dataflows[j]
				#j=j-1			
				#flag=1
			elif s3 in current_flow_end or s4 in current_flow_end:
				#x=re.sub(current_flow_end,'',dataflows[i])
				x=dataflows[i].replace(current_flow_end,'')				
				#print('flow_end:',current_flow_end)
				#print('xxxx',x)
				newflow=x+dataflows[j]
				#dataflows[i]=newflow
				#print('yes2!')
				#print(dataflows[i])
				#print(dataflows[j])
				#print(x)
				#print(newflow)
				if not newflow in newflows:
					tmp=[i,newflow]
					newflows.append(tmp)
				#if not newflow in dataflows:
					#dataflows.append(newflow)
					#print(newflow)
					#dataflows[i]=newflow
					#print('yes2!')
					#print(dataflows[i],' , ',dataflows[j])
					#print(newflow)
					#i=i-1
				#used[j]=1
				#del dataflows[j]
				#j=j-1			
				#flag=1
	#print('\n')
	updateflow=[]
	for i in range(0,len(newflows)):
		#flag=0
		pos=newflows[i][0]
		flow=newflows[i][1]
		for j in range(pos+1,len(dataflows)):
			#print(j,len(dataflows))
			current_flow_end=flow.split('-->')[-1]
			next_flow_head=dataflows[j].split('-->')[0]
			s1=current_flow_end+'|'
			s2='|'+current_flow_end
			s3=next_flow_head+'|'
			s4='|'+next_flow_head
			if current_flow_end == next_flow_head or s1 in next_flow_head or s2 in next_flow_head:
				y=dataflows[j].replace(next_flow_head,'',1)
				#y=re.sub(next_flow_head,'',dataflows[j])
				newflow=flow+y
				if not newflow in updateflow:
					#print('yes!',newflow)
					updateflow.append(newflow)
			elif s3 in current_flow_end or s4 in current_flow_end:
				#x=re.sub(current_flow_end,'',dataflows[i])
				x=flow.replace(current_flow_end,'')				
				#print('flow_end:',current_flow_end)
				#print('xxxx',x)
				newflow=x+dataflows[j]
				if not newflow in updateflow:
					#print('yes!',newflow)
					updateflow.append(newflow)
	for i in range(0,len(newflows)):
		flow=newflows[i][1]
		dataflows.append(flow)
	#process_bar.show_process()
	retflow=[]	
	for flow in dataflows:
		if  'unknown_api' in flow:
			retflow.append(flow)
	if caller=='__all__':
		return dataflows
	else:
		return retflow


def get_current_dataflow(current_context,caller):
	dataflows=[]
	lines=current_context.split('\n')
	#process_bar = ShowProcess(len(lines), 'Start to deal with the file')
	for line in lines:
		if (not caller in line) and (caller!='__all__') :
			continue
		if line.strip()=='':
			continue
		#print('NOTE!',line)
		tpline=line.strip()
		line=line.strip()
		if line.startswith('#') or line.startswith('def ') or line.startswith('class '):
			continue
		elif line.endswith('(') or line.endswith('[') or line.endswith('{'):
			line=line[:-1]
		elif 'lambda' in line:
			continue
		elif re.match('.*=\s*[0-9\.]+',line.strip()):
			continue
		line2=re.sub(' ','',line)
		if re.match('.*=\'.*\'.*',line2) or re.match('.*=\".*\".*',line2) or re.match('.*=[0-9\.]+.*',line2) or  re.match('.*=None.*',line2) or re.match('.*=True.*',line2) or re.match('.*=False.*',line2) or re.match('.*=\{\}.*',line2) or re.match('.*=\(\).*',line2) or re.match('.*=\[\].*',line2) or "==" in line2 or line2.endswith('='):
			#print('yes!')
			continue
		line=re.sub('#.*','',line)
		if '=' in line:
			#print(line)
			#print('yes!')
			line=recheck(line)
			if line.endswith('='):
				continue
			if line.endswith(',') or  line.endswith(':') or line.endswith('+') or line.endswith('-') or line.endswith('*') or line.endswith('/'):
				line=line[:-1].strip()
			#print(line)
			ops=re.findall('[_a-zA-Z0-9\.\[\]\"\'\(\)\{\}]+\s*=\s*[_a-zA-Z0-9\.\[\]\"\'\(\)\{\}\*\/\-\%\*\,\=\s\+]+',line)
			#print(ops)
			if len(ops)>0:
				s=ops[0]
				s=recheck(s)
				rs=s.split('=')[1]
				ps=re.findall('[\,\-\+\*\/\%]+',rs)
				if len(ps)==0 and rs.count(' ')>1:
					#print('ignored\n')
					continue
				elif s.endswith(')') and s.count(')')-s.count('(')==1:
					s=s[:-1]
				elif s.endswith(', )'):
					s=s[:-3]+')'
				s=re.sub('\)\,.*$','',s)
				s=check(s)					
				if s.count('(') != s.count(')') or  s.count('[') != s.count(']') or  s.count('{') != s.count('}'):
					#print('ignored\n')
					continue
				else:
					#s=re.sub('\)\,.*$','',s)
					#print(s)
					s=re.sub(' ','',s)
					delop(s)
					#print(file)
					#print(s,final,'\n')
					#print('OP DATAFLOW:')
					#print(final,'\n')
					tf=final
					tf=finalcheck(tf)
					if tf!='' and not tf in dataflows:
						dataflows.append(tf)
					#print(tf)
					#with open('tmp_dataflow/op_expr.txt','a+') as fo:
						#fo.write(file+'#'+str(num)+": "+tpline+'\n'+s+'\n'+final+'\n\n')
		elif re.match('.*for\s.*\sin\s.*',line):
			line=recheck(line)
			#print('FOR_EXPR')
			#print(file,tpline)
			fors=delfor(line)
			#print('FOR DATAFLOW:')
			#print(str(fors),'\n')
			tff=str(fors)
			tff=finalcheck(tff)
			if tff!='' and not tff in dataflows:
				dataflows.append(tff)
			#print(tff)
			#with open('tmp_dataflow/for_expr.txt','a+') as ff:
				#ff.write(file+'#'+str(num)+": "+tpline+'\n'+str(fors)+'\n\n')

		elif re.match('.*[_a-zA-Z0-9\.\[\]\'\"\(\)\{\}\,\:]+\(.*\).*',line) and not line.startswith('def ') and not line.startswith('class '):
			#print(file)
			#print(line,'\n')
			#line=recheck(line)
			#print(line)
			cas=del_call(line)
			#print('CALL DATAFLOW:')
			#print(cas,'\n')
			cas=finalcheck(cas)
			if cas!='' and not cas in dataflows:
				dataflows.append(cas)
			#print(cas)
			#callflow.append(ls2.strip())
			#with open('tmp_dataflow/call_expr.txt','a+') as fc:
				#fc.write(file+'#'+str(num)+'\n'+line+'\n')	
	#process_bar.show_process()
	newflows=[]
	oldflows=dataflows
	lens=5*len(dataflows)
	used=[0]*lens
	for i in range(0,len(dataflows)):
		#flag=0
		current_flow_end=dataflows[i].split('-->')[-1]
		current_flow_head=dataflows[i].split('-->')[0]
		if current_flow_end==current_flow_head:
			continue
		for j in range(i,len(dataflows)):
			#print(j,len(dataflows))
			current_flow_end=dataflows[i].split('-->')[-1]
			next_flow_head=dataflows[j].split('-->')[0]
			s1=current_flow_end+'|'
			s2='|'+current_flow_end
			s3=next_flow_head+'|'
			s4='|'+next_flow_head
			if current_flow_end == next_flow_head or s1 in next_flow_head or s2 in next_flow_head:
				y=dataflows[j].replace(next_flow_head,'',1)
				#y=re.sub(next_flow_head,'',dataflows[j])
				newflow=dataflows[i]+y
				#print('yes1!')
				#print(i,current_flow_end,next_flow_head,s1,s2)
				#print(next_flow_head)
				#print(dataflows[i])
				#print(dataflows[j])
				#print(y)
				#print(newflow)
				if not newflow in newflows:
					tmp=[i,newflow]
					newflows.append(tmp)
				#if not newflow in dataflows:
					#dataflows.append(newflow)
					#print(newflow)
					#dataflows[i]=newflow
					#print('yes!')
					#print(dataflows[i],' , ',dataflows[j])
					#print(newflow)
					#i=i-1
				#used[j]=1
				#del dataflows[j]
				#j=j-1			
				#flag=1
			elif s3 in current_flow_end or s4 in current_flow_end:
				#x=re.sub(current_flow_end,'',dataflows[i])
				x=dataflows[i].replace(current_flow_end,'')				
				#print('flow_end:',current_flow_end)
				#print('xxxx',x)
				newflow=x+dataflows[j]
				#dataflows[i]=newflow
				#print('yes2!')
				#print(dataflows[i])
				#print(dataflows[j])
				#print(x)
				#print(newflow)
				if not newflow in newflows:
					tmp=[i,newflow]
					newflows.append(tmp)
				#if not newflow in dataflows:
					#dataflows.append(newflow)
					#print(newflow)
					#dataflows[i]=newflow
					#print('yes2!')
					#print(dataflows[i],' , ',dataflows[j])
					#print(newflow)
					#i=i-1
				#used[j]=1
				#del dataflows[j]
				#j=j-1			
				#flag=1
		'''
		if flag==0 and used[i]==0:
			if not dataflows[i] in newflows:
				newflows.append(dataflows[i])
		
		if flag==1:
			i=i-1				
		'''
	#print('\n')
	updateflow=[]
	for i in range(0,len(newflows)):
		#flag=0
		pos=newflows[i][0]
		flow=newflows[i][1]
		for j in range(pos+1,len(dataflows)):
			#print(j,len(dataflows))
			current_flow_end=flow.split('-->')[-1]
			next_flow_head=dataflows[j].split('-->')[0]
			s1=current_flow_end+'|'
			s2='|'+current_flow_end
			s3=next_flow_head+'|'
			s4='|'+next_flow_head
			if current_flow_end == next_flow_head or s1 in next_flow_head or s2 in next_flow_head:
				y=dataflows[j].replace(next_flow_head,'',1)
				#y=re.sub(next_flow_head,'',dataflows[j])
				newflow=flow+y
				if not newflow in updateflow:
					#print('yes!',newflow)
					updateflow.append(newflow)
			elif s3 in current_flow_end or s4 in current_flow_end:
				#x=re.sub(current_flow_end,'',dataflows[i])
				x=flow.replace(current_flow_end,'')				
				#print('flow_end:',current_flow_end)
				#print('xxxx',x)
				newflow=x+dataflows[j]
				if not newflow in updateflow:
					#print('yes!',newflow)
					updateflow.append(newflow)
	for i in range(0,len(newflows)):
		flow=newflows[i][1]
		dataflows.append(flow)
	#process_bar.show_process()
	retflow=[]	
	for flow in dataflows:
		if  'unknown_api' in flow:
			retflow.append(flow)
	if caller=='__all__':
		return dataflows
	else:
		return retflow

def lcs(X, Y): 
    # find the length of the strings 
    m = len(X) 
    n = len(Y) 

    L = [[None]*(n + 1) for i in range(m + 1)] 
  

    for i in range(m + 1): 
        for j in range(n + 1): 
            if i == 0 or j == 0 : 
                L[i][j] = 0
            elif X[i-1] == Y[j-1]: 
                L[i][j] = L[i-1][j-1]+1
            else: 
                L[i][j] = max(L[i-1][j], L[i][j-1]) 
  
    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1] 
    return L[m][n] 
# end of function lcs 

def get_sim_score(api,token,d):
	lcsn=lcs(api,token)
	lcsn=float(lcsn)
	ret=float((lcsn*2.0) / (float(d)*float(len(api)+len(token))))
	#print(api,token,ret)
	return ret

def get_tosim_score(api,maxflow):
	if ' ' in maxflow:
		flows=maxflow.split(' ')
		for flow in flows:
			if 'unknown_api' in flow:
				mfx=flow
				break
	else:
		mfx=maxflow
	ls=mfx.split('-->')
	apindex=len(ls)
	for k in range(0,len(ls)):
		if 'unknown_api' in ls[k]:
			apindex=k
	
	tosim=0.0
	for i in range(0,len(ls)):
		if i!=apindex:
			sim_score=get_sim_score(api,ls[i],abs(apindex-i))
			tosim+=sim_score
	tosim=float(tosim/float(len(ls)))
	#print(tosim)
	return tosim

def standard(scsk):
	scs=scsk
	data=[]
	for k in scs.keys():
		scs[k]=pow(10,scs[k])
		data.append(scs[k])
	lenth = len(data)
	if lenth==0:
		return scsk
	total = sum(data)
	ave = float(total)/lenth
	tempsum = sum([pow(data[i] - ave,2) for i in range(lenth)])
	tempsum = pow(float(tempsum)/lenth,0.5)
	try:
		for k in scs.keys():
			scs[k] = (scs[k] - ave)/tempsum
			scs[k] = 1 / (1 + np.exp(-scs[k]))
	except Exception:
		return scsk
	return scs

def get_ngram_scores(flows,apis,callee):
	s=''
	#print(apis)
	#print(flows)
	ngramscore={}
	for flow in flows:
		s=s+flow+'\n'
	with open('/home/user/APIREC/pyart/test.txt','w+') as f:
		f.write(s)
	#print(s)
	#os.chdir('dataflow/')
	os.system('/home/user/APIREC/pyart/srilm-1.7.2/lm/bin/i686-m64/ngram  -ppl /home/user/APIREC/pyart/test.txt  -order 4 -lm /home/user/APIREC/pyart/trainfile.lm -debug 2 > /home/user/APIREC/pyart/output/'+callee+'.ppl')
	with open('/home/user/APIREC/pyart/output/'+callee+'.ppl',encoding='ISO-8859-1') as f:
		lines=f.readlines()
	
	for key in apis:
		flag=0
		for i in range(0,len(lines)):
			kname=lines[i].strip().split(' ')		
			for item in kname:
				if item==key:
					flag=1
					break
			if flag==1:
				#print(lines[i])
				j=i+1
				while 'logprob=' not in lines[j]:
					j=j+1
				score=re.findall('logprob=\s[0-9\-\.]+',lines[j])
				ngramscore[key]=float(score[0][9:])
				break
		if flag==0:
			ngramscore[key]=0.0
	
	#ngramscore=standard(ngramscore)
	#print(ngramscore)
	#ngramscore=sorted(ngramscore.items(), key=lambda x: x[1], reverse=True)
	#print(ngramscore)
	os.system('rm /home/user/APIREC/pyart/output/'+callee+'.ppl')
	#os.chdir('../')
	return ngramscore
	
	
	

def get_ngram_score(apis,current_dataflow,baseflag,basetype,callee):
	flows=[]
	if baseflag==1:
		for api in apis:
			if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
				continue
			#print(api)
			flow=basetype+' '+api
			flows.append(flow)
		#ngram_score=get_basetype_score(flow)
	else:
		#print(current_dataflow)
		#print(apis)
		for flow in current_dataflow:
			for api in apis:
				if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
					continue
				flow1=re.sub('unknown_api',api,flow)
				#print(flow1)
				flow2=re.sub('-->',' ',flow1)
				#print(flow2)
				flows.append(flow2)
	#print(flows,apis,callee)
	dataflow_ngram_scores=get_ngram_scores(flows,apis,callee)
	#print('data1',dataflow_ngram_scores)
	return dataflow_ngram_scores

def get_api_scores(apis,maxflow,current_dataflow,ft,callee):
	dataflow_ngram_score={}
	basetypes=['int','str','float','list','dict','set','tuple','buffer','frozenset','complex','bool','unicode','bytes','bytearray']
	basetype=''
	baseflag=0
	for bt in basetypes:
		if bt==ft:
			#print(bt,api)
			basetype=bt
	if re.match('List\[.*\]',ft):
		#print('list',api)
		basetype='list'	
		ft='list'
	elif re.match('Dict\[.*\]',ft):
		#print('dict',api)
		basetype='dict'
		ft='dict'
	if basetype!='':
		baseflag=1
	dataflow_ngram_scores=get_ngram_score(apis,current_dataflow,baseflag,ft,callee)
	#print("data",dataflow_ngram_scores)
	final_scores={}
	tosim_scores={}
	for api in apis:
		if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
			continue
		tosim_scores[api]=get_tosim_score(api,maxflow)
	tosim_scores=standard(tosim_scores)
		#tosim_scores = sorted(tosim_scores.items(),key = lambda x:x[1],reverse = True)
		#print(tosim_scores)
	#for k in tosim_scores.keys():
		#final_scores[k]=0.5+float(dataflow_ngram_scores[k]+tosim_scores[k])/4.0

	dataflow_ngram_scores=sorted(dataflow_ngram_scores.items(), key=lambda x: x[1], reverse=True)
	tosim_scores = sorted(tosim_scores.items(),key = lambda x:x[1],reverse = True)
	#final_scores= sorted(final_scores.items(),key = lambda x:x[1],reverse = True)
		#print(final_scores)
	print("NGRAM-SCORE: ",dataflow_ngram_scores[:20])
	print("SIMILAR-SCORE: ",tosim_scores[:20])
	#print("ADD-SCORE: ",final_scores[:20])
	#return final_scores
	drank=21
	nrank=21
	if len(dataflow_ngram_scores)<20:
		k=len(dataflow_ngram_scores)
	else:
		k=20
	for i in range(0,k):
		if dataflow_ngram_scores[i][0]==callee:
			drank=i+1
		if tosim_scores[i][0]==callee:
			nrank=i+1
	print(drank,nrank)
	return drank,nrank

def get_dataflow_scores(apis,maxflow,current_dataflow,ft,callee):
	dataflow_ngram_score={}
	basetypes=['int','str','float','list','dict','set','tuple','buffer','frozenset','complex','bool','unicode','bytes','bytearray']
	basetype=''
	baseflag=0
	for bt in basetypes:
		if bt==ft:
			#print(bt,api)
			basetype=bt
	if re.match('List\[.*\]',ft):
		#print('list',api)
		basetype='list'	
		ft='list'
	elif re.match('Dict\[.*\]',ft):
		#print('dict',api)
		basetype='dict'
		ft='dict'
	if basetype!='':
		baseflag=1
	dataflow_ngram_scores=get_ngram_score(apis,current_dataflow,baseflag,ft,callee)
	return dataflow_ngram_scores


def get_tosim_scores(apis,maxflow,current_dataflow,ft,callee):
	tosim_scores={}
	for api in apis:
		if api.startswith('__') or re.match('[A-Z0-9_]+$',api) or api.strip()=='_':
			continue
		tosim_scores[api]=get_tosim_score(api,maxflow)
	#tosim_scores=standard(tosim_scores)
	return tosim_scores




