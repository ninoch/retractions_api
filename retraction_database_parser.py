import glob
import sys
import pandas as pd 
from html.parser import HTMLParser

folder_name = 'Physics_papers'
if len(sys.argv) > 1:
    folder_name = sys.argv[1]

print ("")
print ("\t >>> Parsing .html files in {}/ <<<".format(folder_name))
print ("")

ret_papers = pd.DataFrame(columns=['title', 'authors', 'journal', 'doi', 'pub_med', 'date', 'ret_dio', 'ret_pub_med', 'ret_date', 'reasons'])

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.num_papers = 0
       	self._reset()

    def _reset(self):
        self.target_item = False
        self.get_reason = False
        self.get_title = False
        self.get_author = False
        self.get_journal = False
        self.get_dio = False
        self.dio_cnt = 0
        self.dio_cnt_cnt = 0

        self.title = None
        self.journal = None
        self.ret_info = [[None, None, None], [None, None, None]]
        self.reasons = []
        self.authors = []

    def _save(self):
    	global ret_papers

    	# print ("#{}".format(self.num_papers))
    	# print ("Title = {}".format(self.title))
    	# print ("Journal = {}".format(self.journal))
    	# print ("DOI = {}".format(self.ret_info))
    	# print ("Reasons = {}".format(self.reasons))
    	# print ("Authors = {}".format(self.authors))
    	# print ("")

    	ret_papers = ret_papers.append({
    		'title': self.title, 
    		'journal': self.journal, 
    		'doi': self.ret_info[0][2], 
    		'pub_med': self.ret_info[0][1], 
    		'date': self.ret_info[0][0],
    		'ret_dio': self.ret_info[1][2], 
    		'ret_pub_med': self.ret_info[1][1], 
    		'ret_date': self.ret_info[1][0], 
    		'reasons': ';'.join(self.reasons),
    		'authors': ';'.join(self.authors)
    		}, ignore_index=True)

    	self._reset()


    def handle_starttag(self, tag, attrs):
        # print ("\t", tag, attrs)
        if (tag == 'tr' and len(attrs) > 0 and attrs[0][1] == 'mainrow'):
            self.num_papers += 1
            self.target_item = True

        elif (self.target_item == True and tag == 'div' and len(attrs) > 0 and attrs[0][1] == 'rReason'):
            self.get_reason = True

        elif (self.target_item == True and tag == 'span' and len(attrs) > 0 and attrs[0][1] == 'rTitleNotIE'):
            self.get_title = True

        elif (self.target_item == True and tag == 'span' and len(attrs) > 0 and attrs[0][1] == 'rJournal'):
            self.get_journal = True

        elif (self.target_item == True and tag == 'a' and len(attrs) > 1 and attrs[1][1] == 'authorLink'):
        	self.get_author = True

        elif (self.target_item == True and tag == 'td' and len(attrs) > 1 and attrs[0][1] == 'border-color:Silver;' and attrs[1][1] == 'smallFont'):
        	self.get_dio = True
        	self.dio_cnt += 1
        	self.dio_cnt_cnt = 0
        elif (self.target_item == True and self.get_dio == True and tag =='br'):            
            self.dio_cnt_cnt += 1

    def handle_endtag(self, tag):
        # print ("\t", tag, "\t end")
        if (tag == 'tr' and self.target_item == True):
            self._save()

        if (tag == 'div' and self.get_reason == True):
            self.get_reason = False

        if (tag == 'span' and self.get_title == True):
        	self.get_title = False

       	if (tag == 'span' and self.get_journal == True):
       		self.get_journal = False

       	if (tag == 'span' and self.get_dio == True):
       		self.get_dio = False

       	if (tag == 'a' and self.get_author == True):
       		self.get_author = False



    def handle_data(self, data):
        # print (data)
        if self.get_reason == True:
            self.reasons.append(data[1:])

        if self.get_author == True:
        	self.authors.append(data)

        if self.get_title == True:
        	self.title = data 

       	if self.get_journal == True:
       		self.journal = data[:-4] 

        if self.get_dio == True:
            if (self.dio_cnt > 1):
                self.ret_info[self.dio_cnt - 2][self.dio_cnt_cnt] = data



for file in list(glob.glob('{}/*.htm'.format(folder_name))):
    f = open(file, "r")
    file_content = f.read()

    parser = MyHTMLParser()
    parser.feed(file_content)

    print ("Number of papers in file {} = {}".format(file, parser.num_papers))

print ("Total number of papers = {}".format(len(ret_papers)))
ret_papers.to_csv('{}.csv'.format(folder_name), index=False)

