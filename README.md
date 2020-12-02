# PyART
This is the dataSet and source code for PyART

Core code of PyART is in PyART/ directory, we give a detailed introduction to the directory.This directory is for a simple demo for PyART in one foldamong k-fold evaluation of within-project API recommendation. An execuable demo is updated in https://github.com/PYART0/PyART-demo.

**Some requirements for PyART**

[If you want to use understand to get Json file]:

vim ~/.bashrc

export PATH="$PATH:/[path]/understand/scitools/bin/linux64"

export STIHOME="/[path]/understand/scitools"

export LD_LIBRARY_PATH="/[path]/understand/scitools/bin/linux64"

[This is not necessary if you donot use understand]

Python3.6+

apt-get install libnss3 libfontconfig gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

python3 -m pip install --upgrade pip

python3 -m pip install pytype sklearn pandas joblib nltk

**To run testing case:**

Python3 aget_test_result.py

**Main introduction**

This doc is for a simple demo for PyART in k-fold evaluation of within-project API recommendation. The main steps are just training (aget_train_kfold.py) and testing (aget_tes_result.py).

**Other core files in demo are as follows:**

builtin.txt: store built-in methods mentioned in Python standard doc.

typeshed.txt: store APIs in typeshed dataset of part of python libs (including standard and 3-party libs)

get_dataflow.py: get dataflow constraints.

trainfile.lm: the trained N-Gram model by the tool SRILM to compute the log possibility score of a given dataflow as one of the feature vector for PyART.

getudbs.py and getJson.pl: these two files are just used to get all APIs defined in the current projects by the tool understand. PyART needs to extract all APIs defined in the current code context. However, in order to reduce effort in the demo, we just use the tool understand to get all APIs defined in the project, and just extract part of corresponding APIs to simulate readl-time scenario in each recommendation point. And this part needs to be re-constructed.


generateclf.py: train recommendation model using training cases based on random forest.

**Other dirs in demo are as follows:**

output/: tmp dir for dataflow extraction

drilm-1.7.2: ngram tool srilm

testdata/:store project

testJson/:store Json file

traincsv/:store .csv files and .pkl files


**Core functions in aget_train_kfold.py and corresponding parameters:**

\_\_main\_\_(CURRENT_PROJ,filePath)// if\_\_name\_\_==”main”

This is the entry of training process, which reads files of a given project named ‘CURRENT_PROJ’ stored in the directory ‘filePath’, and finally outputs extracted training vectors and labels into .csv files in ‘outPath’ directory.

Parameter:

CURRENT_PROJ: project name, such as ‘flask’
filePath:path of training directory,such as ‘testdata/’

get_proj_tokens(iret_list)

The function gets all tokens of all files in the current context and stores them in the hash table for token co-occurrence computation in the latter process.

Parameter:
iret_list: list of training files

dealwith(curfile)

The fuction makes preparations and starts to training.

get_module_methods(curfile)

The function gets all possible APIs that may be imported by ‘import’ statement in the current file.

count_all_apis()

The function counts all possible APIs that may be used in the current file from three aspects: standard lib APIs, 3-party lib APIs and APIs defined in the current context,combined with import information.

get_rec_point(file)

This is the main function that deals with each file, which recognizes each recommendation point in the form of ‘[exp].API()’, makes type inference for ‘[exp]’, collects candidate APIs, constructs feature vector for each candidate, computes possibility scores and finally outputs recommendation lists.

get_type(finalc,file)

The function makes type inference for ‘[exp]’ with the tool pytype.

Parameter:
finalc: the current context that contains the caller ‘[exp]’ after some simple struct completion and check(such as check_try())
file: current file name.

get_line_scores(aps,naming_line,naming_context,file)

The function gets the co-occurrence scores A of candidate APIs and tokens in the current context before the recommendation line. A represents the occurrence number of the tuple (token,API) in existing files (except the current file)

Parameter:
aps: list of candidate apis
naming_line: unused parameter. Should be deleted
naming_context: all code context before the recommendation point in the current file
file: the current file name

get_conum_scores(aps,naming_context,file):

The function gets the co-occurrence scores B of candidate APIs and tokens in the current context before the recommendation line. B represents the number of files that contain the tuple (token,API) in existing files (except the current file).

**Core functions in aget_test_result.py and corresponding parameters:**

\_\_main\_\_(CURRENT_PROJ,filePath)// if \_\_name\_\_==”main”

This is the entry of testing process, which reads files of a given project named ‘CURRENT_PROJ’ stored in the directory ‘filePath’, and finally outputs a ranking recommendation list.

Parameter:

CURRENT_PROJ: project name, such as ‘flask’
filePath: path of training directory,such as ‘testdata/’

[Most functions in aget_test_result.py are the same as those in aget_train_kfold.py ]

**Core functions in get_dataflow.py and corresponding parameters:**

get_current_dataflow2(current_context,caller)
The function extracts all dataflows that related to the caller ‘[exp]’ at the recommendation point.

Parameter:

current_context: current context containing the caller.
caller: caller

get_dataflow_scores(aps,maxflow,current_dataflow,ft,callee)

The function computes possibility scores of all dataflows that constructed by all candidate APIs.

Parameter:

aps: list of candidate APIs
maxflow: the longest flow containing caller
current_dataflow: all flows containing caller
ft: the inferred type of the caller [may be Any or None or nothing]
callee: expected API name, this parameter is not necessary and should be deleted.

get_tosim_scores(aps,maxflow,current_dataflow,ft,callee)

The function computes similarity scores of tokens in maxdataflow and each candidate API in aps

Parameter:
Same as the above


