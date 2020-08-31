import os,json,sys
import random,time
import numpy as np
from sklearn.model_selection import KFold

DELTA=0.01
GENERATION=1000
BOUND=[0,1]

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
	print("Top-k:",top1,top2,top3,top4,top5,top10,top20,len(arr))
	print("Top-k:",tp1,tp2,tp3,tp4,tp5,tp10,tp20)

def get_map(train_changes,train_tokens,wc):
	#Mactual=[]
	#Plist=[]
	#for change in train_changes:
		#Mactutal.append(change['real_label'])
	#print(Mactual)
	ranks=[]
	length=len(train_changes)
	for i in range(0,length):
		change_score=train_changes[i]
		token_score=train_tokens[i]
		#print(len(change_score))
		#print(len(token_score))
		#print(type(change_score))
		#print(type(token_score))
		#sys.exit()
		#tc=dict(enumerate(change_score))
		#tt=dict(enumerate(token_score))
		#change_score={ index: v for index, v in change_score }
		#token_score={ index: v for index, v in token_score }
		#print(tc)
		#sys.exit(0)
		if change_score['real_label']!=token_score['real_label']:
			print('Arg Error!')
			sys.exit(0)
		real_label=change_score['real_label']
		#Mactual.append(real_label)
		total_scores={}
		for api, cscore in change_score.items():
			if api=='real_label':
				continue
			tscore=token_score[api]
			total_score=wc*float(cscore)+(1.0-wc)*float(tscore)
			total_scores[api]=total_score
		total_scores=sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
		#Plist.append(total_scores[0][0])
	#print(Mactual)
	#print(Plist)
		rank=1
		for k in total_scores:
			if k[0]==real_label:
				break
			else:
				rank+=1
		ranks.append(rank)
	#print(ranks)
	rlen=len(ranks)
	maps=0.0
	for i in range(0,rlen):
		maps+=float(1.0/float(ranks[i]))
	maps=float(maps/float(rlen))
	#print(maps)
	#sys.exit(0)
	#return 0
	get_results(ranks)
	return maps
		


def hillClimbing(train_changes,train_tokens,wc):
	map_x=get_map(train_changes,train_tokens,wc)
	while wc+DELTA<=BOUND[1] and wc+DELTA>=BOUND[0] and get_map(train_changes,train_tokens,wc+DELTA) > get_map(train_changes,train_tokens,wc):
		wc=wc+DELTA
	while wc-DELTA<=BOUND[1] and wc-DELTA>=BOUND[0] and get_map(train_changes,train_tokens,wc-DELTA) > get_map(train_changes,train_tokens,wc):
		wc=wc-DELTA
	return wc,get_map(train_changes,train_tokens,wc)
	


def get_w(train_changes,train_tokens):
	
	highest=[0,-1000]
	wc_ret=0.0
	wcs=[]
	for i in range(GENERATION):
		print('GENERATION START')
		c=random.uniform(0,1)
		wc=round(c,1)
		if wc in wcs:
			continue
		else:
			wcs.append(wc)
		currentValue=hillClimbing(train_changes,train_tokens,wc)
		if currentValue[1] > highest[1]:
			highest[:] = currentValue
		#elif currentValue[1] == highest[1]:
			#break
		print(currentValue)
		print(highest)
	return highest
	





# 1-fold for testing
#def evaluate(test_change_scores,test_token_scores,wc,wt)

changefile='logs/trainJson/train_change_beautifulsoup.json'
tokenfile='logs/trainJson/train_token_beautifulsoup.json'	


def hill_climbing():
	wc=wt=0.5
	maxMAP=0.0
	with open(changefile) as f:
		changes=json.load(f)
	with open(tokenfile) as f1:
		tokens=json.load(f1)
	casenum=len(changes)
	if casenum != len(tokens):
		print('Error about input args.')
		sys.exit(0)
	# k-fold k=3 
	kf = KFold(n_splits=10)
	#print(len(changes))
	#print(len(tokens))
	#print(changes)
	#print(tokens)
	#sys.exit(0)
	#for train_index,test_index in kf.split(changes):
		#print('K-FOLD START')
		#print(len(train_index),len(test_index))
		#train_changes=np.array(changes)[train_index]
		#test_changes=np.array(changes)[test_index]
		#train_tokens=np.array(tokens)[train_index]
		#test_tokens=np.array(tokens)[test_index]
		#print(len(train_changes),len(train_tokens),len(test_changes),len(test_tokens))
	fwc=get_w(changes,tokens)
	print('final',fwc)		
	map_score=get_map(changes,tokens,fwc[0])
		#print('test',map_score)
		#if map_score>maxMAP:
			#maxMAP=map_score
			#wc=fwc[0]
	#print('final wc:',wc)

s=time.time()
hill_climbing()
e=time.time()
print(e-s)
		




