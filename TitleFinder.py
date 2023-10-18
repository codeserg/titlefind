import cv2
import pytesseract
from pdf2image import convert_from_path
import os
import re
import argparse


class TitleFind():
    restrict = r'"\.:?*/\%><|'

    def __init__(self,doctext,savefilename):
        textlower = doctext.lower().replace('\n',' ')
        self.doc_text=" ".join(textlower.split())

        self.doc_name = None
        self.doc_number = None
        self.doc_date = None
        self.pattern_number = None
        self.doc =  None

        with open(savefilename,'w',encoding='UTF-8') as fil:
           fil.write (self.doc_text)


    def replaceforfs(self,init):
        res = init
        for a in self.restrict:
            res = res.replace(a,"_")
        res= res.strip()
        res= res.strip('_')
        return res

    def make(self):
        rusmonth = 'января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря'

        regs = {r'универсальный.*№\s(\d*)\s*от\s*(\d\d\.\d\d\.\d\d\d\d)':('УПД',1),
                r'универсальный.*?№\s*(\d*).*?(\d+\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s\d+)':('УПД',2),
                r'доверенность № (.*)дата выдачи:(.*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря).* г\.) довер':('Доверенность',6),
                }
        
        
        for searchreg,doctype in regs.items():
            find = re.search (searchreg,self.doc_text)
            if not(find is None):            
                #return (doctype, find[1],find[2],str(doctype) + ' № ' + str(find[1]) + ' от ' +str(find[2]))
                self.doc_date = self.replaceforfs(find[2])
                self.doc_name = doctype[0]
                self.doc_number = self.replaceforfs(find[1])
                
                self.pattern_number = doctype[1]
                doctemp =  str(self.doc_name) + ' № ' + str(self.doc_number) + ' от ' +str(self.doc_date)
                self.doc = doctemp[:50]

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str,default='.')
arg=parser.parse_args()
initdir =arg.directory
    
try:    
    os.remove('out.jpg')
except:
    pass


files = os.listdir(initdir)
filespdf = [i for i in files if i[-4:]=='.pdf' or i[-4:]=='.jpg' or i[-4:]=='.jpeg']

for file in filespdf:
    path =initdir+'\\'+file
    
    pages = convert_from_path(path, 200,poppler_path=r'C:\poppler-23.08.0\Library\bin')
    pages[0].save('out.jpg', 'JPEG')
    imgcv=cv2.imread('out.jpg')
    imgcv=cv2.cvtColor(imgcv, cv2.COLOR_BGR2RGB)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    res= pytesseract.image_to_string(imgcv,  lang='rus')
    info = pytesseract.image_to_osd(imgcv,  lang='rus')
    
    trytext= TitleFind(res,initdir+'\\'+file+'.ocr')
    trytext.make()
    print(trytext.pattern_number, initdir+'\\'+file,trytext.doc)    
    
    if not(trytext.doc_name is None):
        fname,ext=os.path.splitext(initdir+'\\'+file)
        newname = trytext.doc+ext
        n=1      
                
        while n<30 and os.path.exists(initdir+'\\'+newname):
            n+=1
            newname= trytext.doc+'('+ str(n)+')'+ext
             
        os.rename(initdir+'\\'+file,initdir+'\\'+newname)
