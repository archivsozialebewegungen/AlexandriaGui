'''
Constants for dependency injection
'''
from injector import BoundKey as Key


MAIN_RUNNER_KEY = Key('main_runner')
MAIN_WINDOWS_KEY = Key('main_windows')

WINDOW_MANAGER_KEY = Key('window_manager')
MESSAGE_BROKER_KEY = Key('message_broker')
SETUP_RUNNER_KEY = Key('setup_runner')

EVENT_WINDOW_PRESENTER_KEY = Key('event_window_presenter')
EVENT_WINDOW_KEY = Key('event_window')
EVENT_WINDOW_BASE_REFERENCES_KEY = Key('event_window_base_references')
EVENT_WINDOW_ADDITIONAL_REFERENCES_KEY = Key('event_window_additional_references')
EVENT_WINDOW_DIALOGS_KEY = Key('event_window_dialogs')
EVENT_WINDOW_POST_PROCESSORS_KEY = Key('event_window_post_processors')

DOCUMENT_WINDOW_PRESENTER_KEY = Key('document_window_presenter')
DOCUMENT_WINDOW_KEY = Key('document_window')
DOCUMENT_WINDOW_BASE_REFERENCES_KEY = Key('document_window_base_references')
DOCUMENT_WINDOW_ADDITIONAL_REFERENCES_KEY = Key('document_window_additional_references')
DOCUMENT_WINDOW_DIALOGS_KEY = Key('document_window_dialogs')
DOCUMENT_WINDOW_POST_PROCESSORS_KEY = Key('document_window_post_processors')
DOCUMENT_TYPE_POST_PROCESSOR_KEY = Key('document_type_post_processor')
JOURNAL_DOCUMENT_TYPE_POST_PROCESSOR_KEY = Key('journal_document_type_post_processor')

# Startup tasks
SETUP_TASKS_KEY = Key('setup_tasks')

CHECK_DATABASE_VERSION_KEY = Key('check_database_version')
LOGIN_KEY = Key('login')
INIT_WINDOWS_KEY = Key('init_windows')
POPULATE_WINDOWS_KEY = Key('populate_windows')

# References

DOCUMENT_EVENT_REFERENCES_FACTORY_KEY = Key('document_event_references_factory')
DOCUMENT_EVENT_REFERENCES_PRESENTER_KEY = Key('document_event_references_presenter')
DOCUMENT_EVENT_REFERENCES_VIEW_CLASS_KEY = Key('document_event_references_view_class')

EVENT_CROSS_REFERENCES_FACTORY_KEY = Key('event_cross_references_factory')
EVENT_CROSS_REFERENCES_PRESENTER_KEY = Key('event_cross_references_presenter')
EVENT_CROSS_REFERENCES_VIEW_CLASS_KEY = Key('event_cross_references_view_class')

EVENT_DOCUMENT_REFERENCES_FACTORY_KEY = Key('event_document_references_factory')
EVENT_DOCUMENT_REFERENCES_PRESENTER_KEY = Key('event_document_references_presenter')
EVENT_DOCUMENT_REFERENCES_VIEW_CLASS_KEY = Key('event_document_references_view_class')

DOCUMENT_FILE_REFERENCES_FACTORY_KEY = Key('document_file_references_factory')
DOCUMENT_FILE_REFERENCES_PRESENTER_KEY = Key('document_file_references_presenter')
DOCUMENT_FILE_REFERENCES_VIEW_CLASS_KEY = Key('document_file_references_view_class')

EVENT_TYPE_REFERENCES_FACTORY_KEY = Key('event_type_references_factory')
EVENT_TYPE_REFERENCES_PRESENTER_KEY = Key('event_type_references_presenter')
EVENT_TYPE_REFERENCES_VIEW_CLASS_KEY = Key('event_type_references_view_class')

# Dialogs

DIALOG_FACTORY_CLASS_KEY = Key('dialog_factory_class')

GENERIC_STRING_EDIT_DIALOG_KEY = Key('generic_string_edit_dialog')
GENERIC_STRING_SELECTION_DIALOG_KEY = Key('generic_string_selection_dialog')
GENERIC_BOOLEAN_SELECTION_DIALOG_KEY = Key('generic_boolean_selection_dialog')
GENERIC_INPUT_DIALOG_PRESENTER = Key('generic_dialog_presenter')

EVENT_SELECTION_DIALOG_PRESENTER_KEY = Key('event_selection_dialog_presenter')
EVENT_SELECTION_DIALOG_KEY = Key('event_selection_dialog')

EVENT_CONFIRMATION_PRESENTER_KEY = Key('event_confirmation')
EVENT_CONFIRMATION_DIALOG_KEY = Key('event_confirmation_dialog')

YEAR_SELECTION_DIALOG_PRESENTER_KEY = Key('year_selection_dialog_presenter')
YEAR_SELECTION_DIALOG_KEY = Key('year_selection_dialog')

DATE_SELECTION_DIALOG_PRESENTER_KEY = Key('date_selection_dialog_presenter')
DATE_SELECTION_DIALOG_KEY = Key('date_selection_dialog')

EVENT_ID_SELECTION_DIALOG_PRESENTER_KEY = Key('event_id_selection_dialog_presenter')
EVENT_ID_SELECTION_DIALOG_KEY = Key('event_id_selection_dialog')

DATERANGE_SELECTION_DIALOG_PRESENTER_KEY = Key('daterange_selection_dialog_presenter')
DATERANGE_SELECTION_DIALOG_KEY = Key('daterange_selection_dialog')

DOCUMENT_FILTER_DIALOG_PRESENTER_KEY = Key('document_filter_dialog_presenter')
DOCUMENT_FILTER_DIALOG_KEY = Key('document_filter_dialog')

EVENT_FILTER_DIALOG_PRESENTER_KEY = Key('event_filter_dialog_presenter')
EVENT_FILTER_DIALOG_KEY = Key('event_filter_dialog')

DOCUMENTID_SELECTION_DIALOG_PRESENTER_KEY = Key('documentid_selection_dialog_presenter')
DOCUMENTID_SELECTION_DIALOG_KEY = Key('documentid_selection_dialog')

FILE_SELECTION_DIALOG_KEY = Key('file_selection_dialog')

LOGIN_DIALOG_FACTORY_KEY = Key('login_dialog_factory')
LOGIN_DIALOG_PRESENTER_KEY = Key('login_dialog_presenter')
LOGIN_DIALOG_KEY = Key('login_dialog')

EVENT_TYPE_SELECTION_PRESENTER_KEY = Key('event_type_selection_dialog_presenter')
EVENT_TYPE_SELECTION_DIALOG_KEY = Key('event_type_selection_dialog')

# Viewers

DOCUMENT_FILE_VIEWERS_KEY = Key('document_file_viewers')
DEFAULT_DOCUMENT_FILE_VIEWER = Key('default_document_file_viewer')

# Plugins

DOCUMENT_MENU_ADDITIONS_KEY = Key('document_menu_entries')
EVENT_MENU_ADDITIONS_KEY = Key('event_menu_entries')
