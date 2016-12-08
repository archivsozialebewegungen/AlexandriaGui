'''
Created on 06.11.2015

@author: michael
'''
from alexpresenters.messagebroker import Message

REQ_QUIT = "quit"
REQ_SAVE_ALL = "save_all"

class BaseWindowPresenter:
    
    def __init__(self, message_broker, entity_service, post_processors):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.entity_service = entity_service
        self.post_processors = post_processors
        self.view = None # Will be set by view
        
    def goto_first(self):
        self._change_entity(self.entity_service.get_first(self.view.filter_expression))
    
    def goto_next(self):
        entity = self._save_if_necessary()
        if entity == None or entity.id == None:
            return
        self._change_entity(self.entity_service.get_next(entity, self.view.filter_expression))

    def goto_previous(self):
        entity = self._save_if_necessary()
        if entity == None or entity.id == None:
            return
        self._change_entity(self.entity_service.get_previous(entity, self.view.filter_expression))

    def goto_last(self):
        self._change_entity(self.entity_service.get_last(self.view.filter_expression))
        
    def goto_record(self):
        record_id = self.view.record_id_selection
        if record_id == None:
            return
        new_entity = self.entity_service.get_nearest(record_id, self.view.filter_expression)
        self._change_entity(new_entity)
        
    def toggle_filter(self):
        if isinstance(self.view.filter_expression, type(None)):
            filter_object = self.view.new_filter
            if filter_object ==  None:
                return
            self.view.filter_expression = self.entity_service.create_filter_expression(filter_object)
        else:
            self.view.filter_expression = None
        
    def create_new(self):
        self._change_entity(self.entity_service.create_new())
    
    def delete(self):
        entity = self.view.entity
        # Quite a lot of ugly edge cases - should be handled by the gui - but you never know
        if entity == None:
            # No entity displayed at all
            return
        if entity.id == None:
            # Entity is not yet saved, so we just jump to the last entity
            self.view.entity = self.entity_service.get_last(self.view.filter_expression)
            return
        
        first_entity = self.entity_service.get_first(self.view.filter_expression)
        if first_entity == self.view.entity:
            goto_entity = self.entity_service.get_next(entity, self.view.filter_expression)
        else:
            goto_entity = self.entity_service.get_previous(entity, self.view.filter_expression)
        self.entity_service.delete(entity)
        if goto_entity == entity:
            # We just deleted the last entity
            self._change_entity(None)
        else:
            self._change_entity(goto_entity)

    def quit(self):
        self.message_broker.send_message(Message(REQ_QUIT))
    
    def _change_entity(self, entity):
        self._save_if_necessary()
        self.view.entity = entity
    
    def _save(self):
        entity = self.view.entity
        if not entity.id:
            entity = self.entity_service.save(entity) # Post processors may need an id
        for post_processor in self.post_processors:
            entity = post_processor.run(entity)
        entity = self.entity_service.save(entity)
        return entity
    
    def _save_if_necessary(self):
        has_changed = self.view.entity_has_changed()
        if has_changed:
            return self._save()
        else:
            return self.view.entity