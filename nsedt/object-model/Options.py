from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CEData:
    strikePrice: float
    expiryDate: str
    underlying: str
    identifier: str
    openInterest: int
    changeinOpenInterest: int

@dataclass
class PEData:
    strikePrice: float
    expiryDate: str
    underlying: str
    identifier: str
    openInterest: int
    changeinOpenInterest: int

@dataclass
class RecordsData:
    CE: List[CEData]
    PE: List[PEData]

@dataclass
class Records:
    data: RecordsData

@dataclass
class OptionChainData:
    records: Records
    expiryDates: List[str]
    timestamp: str

@dataclass
class OptionChainResponse:
    records: OptionChainData
    other_data: Dict[str, Any]
