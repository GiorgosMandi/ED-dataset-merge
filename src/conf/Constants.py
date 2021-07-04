from enum import Enum


class Keys(Enum):
    ORIGIN = 'origin'
    ID = 'id'
    NO_SENTENCES = 'no-of-sentences'
    SENTENCES = 'sentences'
    TEXT = 'text'
    WORDS = 'words'
    LEMMA = 'lemma'
    POS_TAGS = 'pos-tags'
    NER = 'ner'
    ENTITIES_MENTIONED = 'golden-entity-mentions'
    EVENTS_MENTIONED = 'golden-event-mentions'
    PENN_TREEBANK = 'penn-treebank'
    DEPENDENCY_PARSING = "dependency-parsing"
    CHUNKS = 'chunks'
    START = 'start'
    END = 'end'
    ENTITY_ID = 'entity-id'
    ENTITY_TYPE = 'entity-type'
    EXISTING_ENTITY_TYPE = 'existing-entity-type'
    ROLE = 'role'
    ARGUMENTS = 'arguments'
    TRIGGER = 'trigger'
    EVENT_TYPE = 'event-type'
