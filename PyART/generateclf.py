import pandas as pd
import joblib,os,sys
import time
from sklearn.ensemble import RandomForestClassifier

'''
def get_file_path(root_path,file_list,dir_list):
	global ret_list
	dir_or_files = os.listdir(root_path)
	for dir_file in dir_or_files:
		dir_file_path = os.path.join(root_path,dir_file)
		if os.path.isdir(dir_file_path):
			dir_list.append(dir_file_path)
			get_file_path(dir_file_path,file_list,dir_list)
		elif dir_file_path.endswith('.csv'):
			#print(dir_file_path)
			ret_list.append(dir_file_path)
			file_list.append(dir_file_path)


rp2='traincsv/'
ret_list=file_list=dir_list=[]
get_file_path(rp2,file_list,dir_list)
tenfiles=file_list
print(tenfiles)

total_data='f1,f2,f3,f4\n'
total_label='label\n'



for file in tenfiles:
	if '_data' in file:
		#print('yes')
		index=file.rfind('/')
		sf=file[index+1:]
		proj=sf.split('_')[0]
		datafile=file
		labelfile=file[:index+1]+proj+'_label.csv'
		with open(datafile) as f:
			lines=f.read()
		total_data+=lines
		with open(labelfile) as f1:
			lines1=f1.read()
		total_label+=lines1


with open('traincsv/flask_data.csv','w+') as f:
	f.write(total_data)		
with open('traincsv/flask_label.csv','w+') as f:
	f.write(total_label)
'''

start=time.time()
data=pd.read_csv('traincsv/flask_data.csv')
label=pd.read_csv('traincsv/flask_label.csv')
lines=len(data)
trainnum=int(lines/10*9)
train_data=data[:trainnum]
train_label=label[:trainnum]
labels=train_label.values.ravel()
clf=RandomForestClassifier()
clf.fit(train_data,labels)
result=clf.score(train_data,labels)
joblib.dump(clf,'traincsv/flask1.pkl')
print(result)
#sys.exit()
end=time.time()
print(end-start)

