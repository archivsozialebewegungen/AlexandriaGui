'''
Created on 28.03.2016

@author: michael
'''
import re
import gettext
from injector import inject
from alexandriabase import baseinjectorkeys
gettext.bindtextdomain('alexandria', 'locale')
gettext.textdomain('alexandria')
_ = gettext.gettext

class DocumentTypePostProcessor(object):

    @inject(document_type_service=baseinjectorkeys.DOCUMENT_TYPE_SERVICE_KEY)    
    def __init__(self, document_type_service):
        self.type_dict = document_type_service.get_document_type_dict()
        self.doctype_re = self.build_doctype_re()
        
    def build_doctype_re(self):
        pattern = r"^\s*(%s)\s*:\s*(.*)" % '|'.join(self.type_dict.keys())
        return re.compile(pattern, re.IGNORECASE)
    
    def run(self, entity):
        
        matcher = self.doctype_re.match(entity.description)
        if matcher:
            entity.description = matcher.group(2)
            entity.document_type = self.type_dict[matcher.group(1).upper()]
        return entity

class JournalDocTypePostProcessor(object):

    @inject(document_type_service=baseinjectorkeys.DOCUMENT_TYPE_SERVICE_KEY)    
    def __init__(self, document_type_service):
        self.doc_type = document_type_service.get_by_id(13)
        month_pattern = _(r"\s*(\d{1,2}\.|January|February|March|April|May|" +
            r"June|July|August|September|October|November|December|" +
            r"Jan\.|Feb\.|Mar\.|Apr\.|May|Jun\.|Jul\.|Aug\.|Sep\.|Oct\.|Nov\.|Dec\.)\s*")
        delimiter_pattern = _(r"(from|,)\s+")
        self.doctype_re = re.compile(r"^(.{1,30}?" + 
                                     delimiter_pattern + 
                                     r"\d+\." + 
                                     month_pattern 
                                     + r"\d+)", 
                                     re.IGNORECASE)
        
    def run(self, entity):
        
        if entity.document_type != None and entity.document_type.id != 1:
            return entity
        
        matcher = self.doctype_re.match(entity.description)
        if matcher:
            entity.document_type = self.doc_type
        return entity
