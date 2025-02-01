from pydantic import BaseModel, EmailStr, AnyHttpUrl
from typing import Optional
from enum import Enum
from datetime import datetime

# Step 1: Define an Enum
class AdventurePhase(Enum):
    START = "start"
    MIDDLE = "middle"
    END = "end"

class ProtagonistGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"


class SupportedLanguages(Enum):
    ENGLISH = "English"
    SPANISH = "Spanish"
    FRENCH = "French"
    GERMAN = "German"
    CHINESE = "Mandarin Chinese"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    ITALIAN = "Italian"
    PORTUGUESE = "Portuguese"
    RUSSIAN = "Russian"

class AdventureTypes(Enum):
    FANTASY = "Fantasy"
    SCIFI = "Sci-Fi"
    WESTERN = "Western"
    MYSTERY = "Mystery"
    SPORTS = "Sports"

class Perspectives(Enum):
    FIRSTPERSON = "First Person"
    SECONDPERSON = "Second Person"
    THIRDPERSON = "Third Person"

class Outcomes(Enum):
    CONTINUE = "continue"
    FINISH = "finish"
    DEAD = "dead"


class AdventureBase(BaseModel):
    adventure_id: Optional[str]


class AdventureList(BaseModel):
    adventures: list

class AdventureNodes(AdventureBase):
    adventure_id: str
    nodes: list


class AdventureNode(AdventureBase):
    adventure_id: str
    node_index: int


class AdventureCreate(BaseModel):
    prompt: str
    min_words_per_level: Optional[int] = 100
    max_words_per_level: Optional[int] = 200
    max_levels: Optional[int] = 10
    perspective: Optional[Perspectives] = Perspectives.SECONDPERSON

class AdventureDelete(AdventureBase):
    adventure_id: str  # The ID of the Adventure you want to delete, or remove nodes from.

class AdventureTruncate(AdventureBase):
    adventure_id: str  # The ID of the Adventure you want to delete, or remove nodes from.
    node_index: int # ID of the Adventure Node to truncate to.

class AdventureResponse(AdventureBase):
    adventure_id: Optional[str]  # MongoDB IDs are typically strings
    title: Optional[str] = None
    synopsis: Optional[str] = None
    createdAt: Optional[datetime] = None
    coverImageURL: Optional[str] = None
    node_index: Optional[int] = None #node_index returned also, when a new node is created.

class NodeCreate(AdventureBase):
    adventure_id: str
    start_from_node_id: Optional[int] = None
    selected_option: Optional[int] = 0
    end_after_insert: Optional[Outcomes] = Outcomes.CONTINUE


