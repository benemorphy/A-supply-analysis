import os
os.environ.get("NEO4J_PASSWORD","")"A-supply-analysis 数据模型os.environ.get("NEO4J_PASSWORD","")"
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    stock_code: Optional[str] = None
    industry: Optional[str] = None

class SupplyRelation(BaseModel):
    source: str           # 公司名
    target: str           # 客户/供应商名
    relation_type: str    # "客户" | "供应商"
    year: int
    ratio: Optional[float] = None  # 交易占比
    amount: Optional[float] = None # 交易金额(亿元)

class RawTextInput(BaseModel):
    company: str
    year: int
    raw_text: str

class CleanResult(BaseModel):
    company: str
    year: int
    items: List[SupplyRelation]
    filtered_items: int  # 被过滤的匿名条目数
