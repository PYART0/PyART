import os,time,sys
import json
	


rootdir='/home/user/APIREC/traindata/'
projs=os.listdir(rootdir)

for proj in projs:
	CURRENT_PROJ=proj
	
	#os.chdir(rootdir+proj)
	#os.system('git log -p --reverse --  \'*.py\' > /home/user/APIREC/logs/'+proj+'_log.txt')
	#os.system('mkdir /home/user/APIREC/logs/token_'+proj)


	with open('/home/user/APIREC/logs/'+CURRENT_PROJ+'_log.txt','r') as f:
		lines=f.readlines()

	commit=''
	kind=''
	filea=''
	fileb=''
	num=0
	idd=0
	commit_cs=''
	error=0
	success=0
	candidates=[]
	tnum=0
	count=0



	os.system('rm -rf Tmp/*')


	typecs=[]
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
				os.chdir('/home/user/APIREC/traindata/'+CURRENT_PROJ)
				os.system('git reset --hard '+gcommit)
			else:
				#os.system('rm -r Tmp')
				#os.system('mkdir train_Tmp/'+str(num))
				os.system('cp -r /home/user/APIREC/traindata/'+CURRENT_PROJ+' /home/user/APIREC/Tmp/')
				#os.system('cp -r traindata/+CURRENT_PROJ+' train_Tmp/'+str(num))
				os.chdir('/home/user/APIREC/traindata/'+CURRENT_PROJ)
				os.system('git reset --hard '+gcommit)


		elif 'index' in line and len(ls)==3:
			kind=line
		elif '--- a' in line and kind!='':
			filea=ls[1][1:-1]
		elif '--- /' in line:
			filea=ls[1][:-1]
		elif '+++ b' in line and kind!='':
			fileb=ls[1][1:-1]
			print(num)
			print(fileb)
			print(filea)
			if num > 1:
				#os.chdir('gumtree/dist/build/distributions/gumtree-2.1.3-SNAPSHOT/bin')
				#os.system('ls')
				#print num
				#print commit,kind,filea,fileb
				os.system('gumtree textdiff /home/user/APIREC/traindata/'+CURRENT_PROJ+fileb+' /home/user/APIREC/Tmp/'+CURRENT_PROJ+filea+' > /home/user/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))

				with open('/home/user/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd)) as f:
					lines=f.read()


				whole_cs=[]
				lines=lines.strip()
				if lines=='':
					os.system('rm /home/user/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))
					error+=1
					print(error,success)
					#sys.exit()
					continue
				else:
					success+=1
					print(error,success)


				
				if "update-" in lines or "delete-" in lines or "insert-" in lines or "move-" in lines:	
					with open('/home/user/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd),'w+') as f:
						f.write(lines)
				else:
					kind=filea=fileb=''
					print('no change')
					os.system('rm /home/user/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))
					continue

				os.system('gumtree parse /home/user/APIREC/traindata/'+CURRENT_PROJ+fileb+' > /home/user/APIREC/logs/token_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd)+'_pre.json')
				os.system('gumtree parse /home/user/APIREC/Tmp/'+CURRENT_PROJ+filea+' > /home/user/APIREC/logs/token_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd)+'_cur.json')
				#print('/home/user/APIREC/logs/log_'+CURRENT_PROJ+'/'+str(num)+'_'+str(idd))
				
				idd =idd+1
			kind=filea=fileb=''

