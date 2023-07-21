import uuid
from pydantic import Field
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    RETIRED = "retired"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"
    SEASONAL = "seasonal"
    TEMPORARY = "temporary"
    OTHER = "other"


class Period(str, Enum):
    HOURLY = "hourly"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMIMONTHLY = "semimonthly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    SALARY = "salary"


class PayCycle(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMIMONTHLY = "semimonthly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class Address(BaseModel):
    line1: str = Field(alias="street1")
    line2: str = Field(alias="street2")
    city: str
    state: str
    postal_code: str = Field(alias="zipCode")
    country: str


class PlatformIds(BaseModel):
    employee_id: str
    position_id: str
    platform_user_id: str


class BasePay(BaseModel):
    amount: str
    period: Period
    currency: str


class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account: Optional[str]
    address: Address
    first_name: str
    last_name: str
    full_name: str
    birth_date: Optional[str] = None
    email: str
    phone_number: Optional[str] = None
    picture_url: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    employment_type: Optional[EmploymentType] = None
    job_title: Optional[str] = None
    ssn: Optional[str] = None
    marital_status: Optional[str] = None
    gender: Optional[str] = None
    hire_date: Optional[str] = None
    termination_date: Optional[str] = None
    termination_reason: Optional[str] = None
    employer: Optional[str] = None
    base_pay: Optional[BasePay] = None
    pay_cicle: Optional[PayCycle] = None
    platform_ids: Optional[PlatformIds] = None
    created_at: datetime
    update_at: datetime
    metadata: Optional[str] = None
