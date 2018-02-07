'''
Created on 02.04.2016

@author: michael
'''
import unittest
from alexandriabase.domain import DocumentType, Document
from alexandriabase.services import DocumentTypeService
from unittest.mock import MagicMock
from alexpresenters.MainWindowPresenters import DocumentTypePostProcessor,\
    JournalDocTypePostProcessor

class DocumentTypePostProcessorTest(unittest.TestCase):
    
    def setUp(self):
        doc_type = DocumentType(1)
        doc_type.description = "Flyer"
        document_type_service = MagicMock(spec=DocumentTypeService)
        document_type_service.get_document_type_dict = MagicMock(return_value={'FLYER': doc_type})
        self.post_processor = DocumentTypePostProcessor(document_type_service)

    def testFlyer(self):
        
        descriptions = ('Flyer: Irgendein Flyer',
                        '  Flyer: Irgendein Flyer',
                        ' Flyer  :Irgendein Flyer',
                        'Flyer:Irgendein Flyer',
                        'Flyer  :\tIrgendein Flyer')
        
        for description in descriptions:
            with self.subTest(description=description):
                entity = Document(4711)
                entity.description = description
                entity = self.post_processor.run(entity)
                self.assertTrue(entity.document_type != None)
                self.assertEqual('Flyer', entity.document_type.description)
                self.assertEqual('Irgendein Flyer', entity.description)

        

class JournalPostProcessorTest(unittest.TestCase):
    

    def setUp(self):
        doc_type = DocumentType(13)
        doc_type.description = "Zeitungsartikel"
        document_type_service = MagicMock(spec=DocumentTypeService)
        document_type_service.get_by_id = MagicMock(return_value=doc_type)
        self.post_processor = JournalDocTypePostProcessor(document_type_service)

    def testJournalArticle(self):
        
        descriptions = ('Stadtzeitung vom 23.4.1975. Irgend ein Text',
                        'Stadtzeitung vom 23. April 1975. Irgend ein Text',
                        'B.Z., 3. April 2014: Noch ein Text')
        
        for description in descriptions:
            with self.subTest(description=description):
                entity = Document(4711)
                entity.description = description
                entity = self.post_processor.run(entity)
                self.assertTrue(entity.document_type != None)
                self.assertEqual('Zeitungsartikel', entity.document_type.description)
        
    def testNoOverwriting(self):
        
        description ='Stadtzeitung vom 23.4.1975. Irgend ein Text'
        flyer_doc_type = DocumentType(2)
        flyer_doc_type.description = "Flyer"

        entity = Document(4711)
        entity.document_type = flyer_doc_type
        entity.description = description
        entity = self.post_processor.run(entity)
        self.assertTrue(entity.document_type != None)
        self.assertEqual('Flyer', entity.document_type.description)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()