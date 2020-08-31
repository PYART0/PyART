

file='httpbin/helpers.py'


with open('/home/user/PyART/dataflows/results/httpbin/all-bindings.txt') as f:
	lines=f.readlines()

nos=set()

for line in lines:
	if not file in line:
		continue
	ls=line.strip().split(' ')
	no=ls[0]
	nos.add(no)
print(len(nos))

with open('/home/user/PyART/dataflows/results/httpbin/all-constraints.txt') as f:
	blines=f.readlines()

lno=0
lnos=[]
num=0
for line in blines:
	lno+=1
	for no in nos:
		if no in line:
			nodes=line.strip().split(' ')
			tmpnode=''
			flag=0
			
			for node in nodes:
				#print(node)
				node=node.split(']')[1][:-1]
				if tmpnode=='':
					tmpnode=node
				elif node!=tmpnode:
					flag=1
				#print(node)
				if node!=no:
					if not lno in lnos and flag==1:
						#print(no)
						print(line.strip())
						lnos.append(lno)
						num+=1
				#if flag==1:
					#print(line.strip())
					#num+=1
print(num)
	

