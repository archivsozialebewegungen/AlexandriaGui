'''
Created on 13.12.2015

@author: michael
'''
import os
from time import sleep

from acceptance.AcceptanceTestUtils import BaseAcceptanceTest, AcceptanceTestRunner, \
    set_date, set_date_range, create_test_file
from alexandriabase.domain import AlexDate, EventTypeIdentifier
from tkgui.MainWindows import BaseWindow, EventWindow
from tkgui.WindowManager import FILTER_DIALOG, GOTO_DIALOG, DATE_RANGE_DIALOG


class BasicFunctionalityTest(BaseAcceptanceTest):

    def test_suite(self):

        # Navigation
        print("\nChecking navigation")
        print("===================")
        self.check_initial_records_shown()
        self.check_goto_last_event()      
        self.check_goto_last_document()
        self.check_goto_first_event()
        self.check_goto_first_document()
        self.check_goto_next_event()
        self.check_goto_next_document()
        self.check_goto_previous_event()
        self.check_goto_previous_document()
        self.check_goto_event()
        self.check_goto_document()
        
        # Filtering
        print("\nChecking filtering")
        print("==================")
        self.check_filtering_events()
        self.check_filtering_events_with_empty_selection()
        self.check_filtering_documents()
        self.check_filtering_documents_with_empty_selection()
        
        # References
        print("\nChecking event cross references")
        print("================================")

        self.check_event_cross_reference_goto()
        self.check_event_cross_reference_new()
        self.check_event_cross_reference_delete()
        
        print("\nChecking event type references")
        print("===============================")

        self.check_event_type_reference_new()
        self.check_event_type_reference_delete()

        print("\nChecking event document references")
        print("==================================")

        self.check_event_document_reference_new()
        self.check_event_document_reference_goto()
        self.check_event_document_reference_delete()

        print("\nChecking document event references")
        print("==================================")

        self.check_document_event_reference_new()
        self.check_document_event_reference_goto()
        self.check_document_event_reference_delete()
        
        print("\nChecking document file references")
        print("==================================")
        
        self.check_document_file_new()
        self.check_document_file_replace()
        self.check_document_file_show()
        self.check_document_file_delete()
        
        # Save
        print("\nChecking saving")
        print("===============")

        self.check_save_event()
        self.check_save_document()
        
        # Create new
        print("\nChecking creation")
        print("=================")

        self.check_create_event()
        self.check_create_document()
        
        # Deleting
        print("\nChecking deleting")
        print("=================")

        self.check_deleting_event()
        self.check_deleting_of_document()
        
        # Quit
        print("\nChecking quit")
        print("=============")

        self.check_quit_works()
        self.success = True
    
    def check_initial_records_shown(self):
        print("Checking the windows show the inital records...", end='')
        self.assert_that_event_is(1940000001)
        self.assert_that_document_is(1)
        self.assert_that_document_description_is("Erstes Dokument")
        print("OK")
        
    def check_goto_last_event(self):
        print("Checking going to last event works...", end='')
        self.event_window_presenter.goto_last()
        self.assert_that_event_is(1961050101)
        self.assert_that_event_description_is("Viertes Ereignis")
        print("OK")
    
    def check_goto_last_document(self):
        print("Checking going to last document works...", end='')
        self.document_window_presenter.goto_last()
        self.assert_that_document_is(14)
        self.assert_that_document_description_is("Siebtes Dokument")  
        print("OK")

    def check_goto_first_event(self):
        print("Checking going to first event works...", end='')
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1940000001)
        self.assert_that_event_description_is("Erstes Ereignis")
        print("OK")

    def check_goto_first_document(self):
        print("Checking going to first document works...", end='')
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(1)
        self.assert_that_document_description_is("Erstes Dokument")  
        print("OK")

    def check_goto_next_event(self):
        print("Checking going to next event works...", end='')
        self.event_window_presenter.goto_last()
        # Wrap arount
        self.event_window_presenter.goto_next()
        self.assert_that_event_is(1940000001)
        self.assert_that_event_description_is("Erstes Ereignis")
        self.event_window_presenter.goto_next()
        self.assert_that_event_is(1950000001)
        self.assert_that_event_description_is("Zweites Ereignis")
        print("OK")

    def check_goto_next_document(self):
        print("Checking going to next document works...", end='')
        self.document_window_presenter.goto_last()
        # Wrap around
        self.document_window_presenter.goto_next()
        self.assert_that_document_is(1)
        self.assert_that_document_description_is("Erstes Dokument")  
        self.document_window_presenter.goto_next()
        self.assert_that_document_is(4)
        self.assert_that_document_description_is("Zweites Dokument")  
        print("OK")

    def check_goto_previous_event(self):
        print("Checking going to previous event works...", end='')
        self.event_window_presenter.goto_first()
        # Wrap arount
        self.event_window_presenter.goto_previous()
        self.assert_that_event_is(1961050101)
        self.assert_that_event_description_is("Viertes Ereignis")
        self.event_window_presenter.goto_previous()
        self.assert_that_event_is(1960013001)
        self.assert_that_event_description_is("Drittes Ereignis")
        print("OK")
        
    def check_goto_previous_document(self):
        print("Checking going to previous document works...", end='')
        self.document_window_presenter.goto_first()
        # Wrap around
        self.document_window_presenter.goto_previous()
        self.assert_that_document_is(14)
        self.assert_that_document_description_is("Siebtes Dokument")  
        self.document_window_presenter.goto_previous()
        self.assert_that_document_is(13)
        self.assert_that_document_description_is("Sechstes Dokument: äöüß")  
        print("OK")

    def check_goto_event(self):
        print("Checking going to nearest selected event works...", end='')
        dialog = self.event_window.dialogs[GOTO_DIALOG]

        self.start_dialog(self.event_window._activate_record_dialog)
        set_date(dialog, AlexDate(1960, 1, 1))
        self.close_dialog(dialog)
        
        self.assert_that_event_is(1960013001)
        print("OK")

    def check_goto_document(self):
        print("Checking going to nearest selected document works...", end='')
        dialog = self.document_window.dialogs[GOTO_DIALOG]

        self.start_dialog(self.document_window._activate_record_dialog)
        dialog.input = 7
        self.close_dialog(dialog)

        self.assert_that_document_is(8)
        print("OK")

    def check_filtering_events(self):
        print("Checking filtering events works...", end='')
        dialog = self.event_window.dialogs[FILTER_DIALOG]

        self.start_dialog(self.event_window._toggle_filter)
        dialog.earliest_date = AlexDate(1961, 1, 1)
        self.close_dialog(dialog)
        
        self.assert_that_event_is(1961050101)
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1961050101)

        # Turn filtering off
        self.event_window._toggle_filter()

        self.assert_that_event_is(1961050101)
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1940000001)

        print("OK")
        
    def check_filtering_events_with_empty_selection(self):
        print("Checking filtering events works even if nothing is selected...", end='')
        dialog = self.event_window.dialogs[FILTER_DIALOG]

        self.start_dialog(self.event_window._toggle_filter)
        dialog.earliest_date = AlexDate(1980, 1, 1)
        self.close_dialog(dialog)
        
        self.assert_no_event()
        self.event_window_presenter.goto_first()
        self.assert_no_event()
        
        # Turn filtering off
        self.event_window._toggle_filter()

        self.assert_no_event()
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1940000001)

        print("OK")

    def check_filtering_documents(self):
        print("Checking filtering documents works...", end='')
        dialog = self.document_window.dialogs[FILTER_DIALOG]

        self.start_dialog(self.document_window._toggle_filter)
        dialog.search_term_entries[0].set("Zweites")
        self.close_dialog(dialog)
        
        self.assert_that_document_is(4)
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(4)
        self.document_window_presenter.goto_last()
        self.assert_that_document_is(4)

        # Turn filtering off
        self.document_window._toggle_filter()

        self.assert_that_document_is(4)
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(1)
        self.document_window_presenter.goto_last()
        self.assert_that_document_is(14)

        print("OK")

    def check_filtering_documents_with_empty_selection(self):
        print("Checking filtering documents works even if nothing is selected...", end='')
        dialog = self.document_window.dialogs[FILTER_DIALOG]

        self.start_dialog(self.document_window._toggle_filter)
        dialog.search_term_entries[0].set("no match")
        self.close_dialog(dialog)

        self.assert_no_document()
        self.document_window_presenter.goto_first()
        self.assert_no_document()
        
        # Turn filtering off
        self.document_window._toggle_filter()

        self.assert_no_document()
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(1)

        print("OK")

    def check_event_cross_reference_goto(self):
        print("Checking goto event cross reference...", end='')
        reference= self.event_window.references[0]
        
        self.event_window_presenter.goto_first()
        
        self.assert_that_event_is(1940000001)

        reference.presenter.goto_event()
        
        self.assert_that_event_is(1950000001)
        
        print("OK")
        
    def check_event_cross_reference_new(self):
        print("Checking create new event cross reference...", end='')
        reference= self.event_window.references[0]
        dialog = reference.event_selection_dialog
        
        self.event_window_presenter.goto_first()

        self.assertEquals(len(reference.items), 2)        

        self.start_dialog(reference._select_new_cross_reference)
        dialog.presenter.view.date_entry.set(AlexDate(1961,5,1))
        dialog.presenter.update_event_list()
        dialog.presenter.view.event_list_box.set(dialog.presenter.view.event_list[0])
        dialog.presenter.ok_action()
        self.wait()

        self.assertEquals(len(reference.items), 3)
                
        print("OK")

    def check_event_cross_reference_delete(self):
        print("Checking delete event cross reference...", end='')
        reference= self.event_window.references[0]
        dialog = reference.deletion_dialog
        
        self.event_window_presenter.goto_first()

        self.assertEquals(len(reference.items), 3)
        
        reference.listbox.set(self.get_event(1961050101))       

        self.start_dialog(reference._delete_cross_reference)
        dialog.presenter.yes_action()
        
        self.assertEquals(len(reference.items), 2)
                
        print("OK")

    def check_event_document_reference_new(self):

        print("Checking new document event reference...", end='')
        reference = self.event_window.references[2]
        dialog = reference.documentid_selection_dialog
        self.document_window.presenter.goto_first()
        self.event_window.presenter.goto_last()
        original_references = len(reference.listbox.get_items())

        self.start_dialog(reference._get_new_document_id)
        
        # Verify we got the correct document id from the document window
        self.assertEquals(dialog.entry.get(), '1')
        dialog.presenter.ok_action()
        
        self.assertEquals(original_references + 1,
                          len(reference.listbox.get_items()))
        self.document_window.presenter.goto_last()
        self.document_window.presenter.goto_first()
        self.assertEquals(original_references + 1,
                          len(reference.listbox.get_items()))
        
        print("OK")

    def check_event_document_reference_goto(self):

        print("Checking goto document event reference...", end='')
        
        reference = self.event_window.references[2]
        self.document_window.presenter.goto_last()
        self.event_window.presenter.goto_last()
        self.assertEquals(1, len(reference.listbox.get_items()))
        self.assert_that_document_is(14)
        # Select new reference from previous test
        reference.listbox.set(reference.listbox.get_items()[-1])
        # "Press" goto
        reference.presenter.change_document()
        
        self.assert_that_document_is(1)

        print("OK")
        
    def check_event_document_reference_delete(self):

        print("Checking goto document event reference...", end='')
        
        reference = self.event_window.references[2]
        dialog = reference.deletion_dialog
        
        self.event_window.presenter.goto_last()
        original_references = len(reference.listbox.get_items())

        # Select new reference from previous test
        reference.listbox.set(reference.listbox.get_items()[-1])
        # "Press" the delete button and confirm in dialog
        self.start_dialog(reference._remove_document_reference)
        dialog.presenter.yes_action()

        self.assertEquals(original_references - 1,
                          len(reference.listbox.get_items()))
        self.event_window.presenter.goto_first()
        self.event_window.presenter.goto_last()
        self.assertEquals(original_references - 1,
                          len(reference.listbox.get_items()))
        print("OK")

    def check_event_type_reference_new(self):
        print("Checking create new event type reference...", end='')
        reference= self.event_window.references[1]
        dialog = reference.event_type_selection_dialog
        
        self.event_window_presenter.goto_first()

        self.assertEquals(len(reference.items), 2)        

        self.start_dialog(reference._get_new_event_type)
        dialog.presenter.set_tree()
        dialog.tree_widget.set(EventTypeIdentifier(3,2))
        dialog.presenter.ok_action()
        self.wait()

        self.assertEquals(len(reference.items), 3)
                
        print("OK")

    def check_event_type_reference_delete(self):
        
        print("Checking deleting event type reference...", end='')
        reference = self.event_window.references[1]
        dialog = reference.deletion_dialog

        self.event_window_presenter.goto_first()

        self.assertEquals(len(reference.items), 3)
        
        items = reference.listbox.get_items()
        identifier = EventTypeIdentifier(3,2)
        for item in items:
            if item.id == identifier:
                reference.listbox.set(item)   

        self.start_dialog(reference._remove_event_type_reference)
        dialog.presenter.yes_action()

        self.assertEquals(len(reference.items), 2)
                
        print("OK")
        
    def check_document_event_reference_new(self):

        print("Checking new document event reference...", end='')
        reference = self.document_window.references[0]
        dialog = reference.event_selection_dialog
        self.document_window.presenter.goto_first()
        original_references = len(reference.listbox.get_items())

        self.event_window.presenter.goto_last()
        self.start_dialog(reference._get_reference_event)
        
        # Verify we got the correct event from the event window
        self.assertEquals(dialog.date_entry.get(), AlexDate(1961, 5, 1))
        # "go to" page 2
        dialog.presenter.update_event_list()        
        # Select the event and close dialog
        event = dialog.event_list_box.get_items()[0]
        dialog.event_list_box.set(event)
        dialog.presenter.ok_action()
        
        self.assertEquals(original_references + 1,
                          len(reference.listbox.get_items()))
        self.document_window.presenter.goto_last()
        self.document_window.presenter.goto_first()
        self.assertEquals(original_references + 1,
                          len(reference.listbox.get_items()))
        
        print("OK")

    def check_document_event_reference_goto(self):

        print("Checking goto document event reference...", end='')
        
        reference = self.document_window.references[0]
        self.document_window.presenter.goto_first()
        self.event_window.presenter.goto_first()
        self.assertEquals(2, len(reference.listbox.get_items()))
        self.assert_that_event_is(1940000001)
        
        # Select new reference from previous test
        reference.listbox.set(reference.listbox.get_items()[-1])
        # "Press" goto
        reference.presenter.change_event()
        
        self.assert_that_event_is(1961050101)

        print("OK")
        
    def check_document_event_reference_delete(self):

        print("Checking goto document event reference...", end='')
        
        reference = self.document_window.references[0]
        dialog = reference.deletion_dialog
        
        self.document_window.presenter.goto_first()
        original_references = len(reference.listbox.get_items())

        # Select new reference from previous test
        reference.listbox.set(reference.listbox.get_items()[-1])
        # "Press" the delete button
        self.start_dialog(reference._remove_event_reference)
        dialog.presenter.yes_action()

        self.assertEquals(original_references - 1,
                          len(reference.listbox.get_items()))
        self.document_window.presenter.goto_last()
        self.document_window.presenter.goto_first()
        self.assertEquals(original_references - 1,
                          len(reference.listbox.get_items()))
        print("OK")

    def check_document_file_new(self):
        
        print("Checking adding new document file reference...", end='')
        reference= self.document_window.references[1]
        
        # precheck
        self.document_window.presenter.goto_first()
        self.assertEquals(3, len(reference.listbox.get_items()))
        input_file = create_test_file("testfile1")
        target_file = os.path.join(self.env.document_txt_dir, "00000015.txt")
        self.assertTrue(os.path.isfile(input_file))
        self.assertFalse(os.path.isfile(target_file))
        
        # doit
        reference._add_file_callback(input_file)
        
        # recheck
        self.assertFalse(os.path.isfile(input_file))
        self.assertTrue(os.path.isfile(target_file))
        self.document_window.presenter.goto_last()
        self.document_window.presenter.goto_first()
        self.assertEquals(4, len(reference.listbox.get_items()))

        print("OK")

    def check_document_file_replace(self):
        
        print("Checking replacing document file reference...", end='')
        reference= self.document_window.references[1]
        
        # precheck
        self.document_window.presenter.goto_first()
        self.assertEquals(4, len(reference.listbox.get_items()))
        input_file = create_test_file("testfile2")
        target_file = os.path.join(self.env.document_txt_dir, "00000015.txt")
        self.assertTrue(os.path.isfile(input_file))
        self.assertTrue(os.path.isfile(target_file))
        content = open(target_file, "r").read()
        self.assertTrue(-1 == content.find("testfile2"))
        
        # doit
        reference.listbox.set(reference.listbox.get_items()[-1])
        reference._replace_file_callback(input_file)
        
        # recheck
        self.assertFalse(os.path.isfile(input_file))
        self.assertTrue(os.path.isfile(target_file))
        content = open(target_file, "r").read()
        self.assertFalse(-1 == content.find("testfile2"))
        self.document_window.presenter.goto_last()
        self.document_window.presenter.goto_first()
        self.assertEquals(4, len(reference.listbox.get_items()))

        print("OK")

    def check_document_file_show(self):
        
        print("Checking showing document file reference...", end='')
        reference= self.document_window.references[1]
        viewer = reference.viewers['tif']
        self.document_window.presenter.goto_first()
        
        reference.listbox.set(reference.listbox.get_items()[0])
        reference.presenter.show_file()
        sleep(1) # Just to see the viewer; this timing is not necessary
        viewer.window.withdraw()
        
        print("OK")

    def check_document_file_delete(self):
        
        print("Checking deleting document file reference...", end='')
        reference= self.document_window.references[1]
        dialog = reference.deletion_dialog
        
        # precheck
        self.document_window.presenter.goto_first()
        self.assertEquals(4, len(reference.listbox.get_items()))
        target_file = os.path.join(self.env.document_txt_dir, "00000015.txt")
        self.assertTrue(os.path.isfile(target_file))
        
        # doit
        reference.listbox.set(reference.listbox.get_items()[-1])
        self.start_dialog(reference._remove_file)
        dialog.presenter.yes_action()
        
        # recheck
        self.assertFalse(os.path.isfile(target_file))
        self.document_window.presenter.goto_last()
        self.document_window.presenter.goto_first()
        self.assertEquals(3, len(reference.listbox.get_items()))

        print("OK")

    def check_save_event(self):
        print("Checking saving of event works...", end='')
        self.event_window_presenter.goto_first()
        self.event_window._description_widget.set("First event with new description")
        event = self.get_event(1940000001)
        self.assertEquals("Erstes Ereignis", event.description)
        self.event_window_presenter.goto_next()
        event = self.get_event(1940000001)
        self.assertEquals("First event with new description", event.description)
        print("OK")
        
    def check_save_document(self):
        print("Checking saving of document works...", end='')
        self.document_window_presenter.goto_first()
        self.document_window._description_widget.set("First document with new description")
        document = self.get_document(1)
        self.assertEquals("Erstes Dokument", document.description)
        self.document_window_presenter.goto_next()
        document = self.get_document(1)
        self.assertEquals("First document with new description", document.description)
        print("OK")

    def check_create_event(self):
        print("Checking creation of event works...", end='')

        dialog = self.event_window.dialogs[DATE_RANGE_DIALOG]

        self.start_dialog(self.event_window._create_new)
        set_date_range(dialog, AlexDate(1941), AlexDate(1942))
        self.close_dialog(dialog)

        self.event_window._description_widget.set("Completely new event.")
        self.event_window_presenter.goto_first()
        self.event_window_presenter.goto_next()
        
        event = self.event_window.entity
        self.assertEquals(1941000001, event.id)
        self.assertEquals("Completely new event.", event.description)
                
        print("OK")
        
    def check_create_document(self):
        print("Checking creating of new document works...", end='')
        self.document_window_presenter.goto_last()
        next_id = self.document_window.entity.id + 1
        self.document_window_presenter.create_new()
        self.document_window._description_widget.set("Completely new document.")
        self.assert_no_such_document(next_id)
        self.document_window_presenter.goto_next()
        self.assert_that_document_is(1)
        document = self.get_document(next_id)
        self.assertEquals(next_id, document.id)
        self.assertEquals("Completely new document.", document.description)
        self.document_window_presenter.goto_last()
        self.assertEquals(next_id, self.document_window.entity.id)
        self.assertEquals("Completely new document.", self.document_window.entity.description)
        print("OK")

    def check_deleting_event(self):
        print("Checking deleting of event works...", end='')
        self.event_window_presenter.goto_last()
        self.event_window_presenter.delete()
        self.assert_that_event_is(1960013001)
        self.assert_that_event_description_is("Drittes Ereignis")
        self.assert_no_such_event(1961050101)

        print("OK")
        
    def check_deleting_of_document(self):
        print("Checking deleting of document works...", end='')
        self.assertTrue(os.path.isfile(self.env.file_paths[1]))
        self.assertTrue(os.path.isfile(self.env.file_paths[2]))
        self.assertTrue(os.path.isfile(self.env.file_paths[3]))

        self.document_window_presenter.goto_first()
        self.document_window_presenter.delete()

        self.assertFalse(os.path.isfile(self.env.file_paths[1]))
        self.assertFalse(os.path.isfile(self.env.file_paths[2]))
        self.assertFalse(os.path.isfile(self.env.file_paths[3]))
        
        self.assert_no_such_document(1)
        self.assert_no_such_document_file_info(1)
        self.assert_no_such_document_file_info(2)
        self.assert_no_such_document_file_info(3)
        print("OK")

    def check_quit_works(self):
        print("Checking quit works...", end='')
        self.event_window_presenter.quit()
        print("OK")

        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    test = BasicFunctionalityTest()
    test_runner = AcceptanceTestRunner(test)
    test_runner.run()