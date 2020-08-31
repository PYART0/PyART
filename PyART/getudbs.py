import os,sys


root_path='testdata/'
dirs=os.listdir(root_path)
print(dirs)



for d in dirs:

	proj=root_path+d
	outputdir='testudb/'+d+'.udb'
	os.system('und create -db '+outputdir+' -languages python add '+proj+' analyze -all')

	print(proj)
