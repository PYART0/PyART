import json

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

'''
apirecfile='apirec_cornice_results.json'

with open(apirecfile) as f:
	apirecrets=json.load(f)
	
ranks=[]

for k,v in apirecrets.items():
	for i in v:
		ranks.append(int(i.split('#')[1]))
'''

ranks=[100, 100, 2, 2, 100, 2, 1, 195, 44, 100, 1, 100, 5, 100, 11, 100, 3, 6, 2, 100, 4, 3, 3, 100, 2, 20, 100, 2, 1, 100, 100, 189, 3, 100, 5, 173, 11, 100, 12, 2, 10, 7, 8, 2, 1, 361, 100, 1, 100, 100, 4, 100, 100, 1, 100, 163, 330, 100, 100, 167, 100, 7, 2, 100, 100, 327, 104, 100, 100, 100, 83, 6, 100, 43, 18, 100, 35, 100, 100, 31, 1, 100, 35, 3, 6, 100, 100, 100, 2, 100, 100, 100, 1, 2, 4, 1, 100, 2, 9, 100, 100, 100, 100, 100, 100, 232, 100, 100, 10, 3, 100, 8, 1, 100, 100, 22, 100, 100, 100, 100, 1, 100, 609, 610, 1, 11, 4, 2, 100, 100, 100, 6, 217, 1, 3, 9, 1, 1, 100, 545, 100, 100, 18, 54, 100, 100, 100, 100, 100, 428, 100, 100, 100, 1, 100, 5, 79, 1, 18, 325, 275, 234, 10, 1, 7, 100, 1, 2, 1, 343, 12, 100, 590, 84, 100, 328, 422, 100, 425, 348, 1, 1, 100, 1, 1, 8, 352, 1, 1, 100, 100, 100, 8, 100, 1, 2, 1, 100, 341, 1, 10, 1, 186, 1, 292, 229, 100, 100, 100, 100, 214, 2, 156, 2, 215, 197, 232, 223, 199, 225, 2, 100, 112, 100, 314, 186, 1, 100, 100, 100, 100, 157, 100, 100, 100, 100, 100, 69, 57, 100, 100, 154, 100, 155, 100, 9, 100, 213, 30, 1, 3, 100, 100, 1, 100, 2, 193, 100, 100, 100, 1, 207, 271, 9, 100, 1, 48, 100, 303, 100, 100, 100, 100, 11, 100, 100, 61, 100, 100, 83, 100, 100, 1, 100, 100, 232, 100, 100, 100, 1, 37, 81, 71, 6, 91, 100, 100, 100, 100, 100, 163, 100, 100, 100, 100, 100, 100, 100, 100, 100, 2, 1, 100, 279, 100]
get_results(ranks)
