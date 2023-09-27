import uuid
import random
import pytest
from datetime import datetime
from faker import Faker
from enum import Enum
from model.Employee import Employee, Address, BasePay, PlatformIds, EmploymentStatus, EmploymentType, Period, PayCycle

fake = Faker()

@pytest.fixture
def random_employee():
    employee = Employee(
        id=str(uuid.uuid4()),
        account=str(random.randint(1000, 9999)),
        address=Address(
            street1=fake.street_address(),
            street2=fake.secondary_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            zipCode=fake.zipcode(),
            country=fake.country()
        ),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        full_name=fake.name(),
        birth_date=fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d"),
        email=fake.email(),
        phone_number=fake.phone_number(),
        picture_url=None,
        job_title=fake.job(),
        ssn=fake.ssn(),
        marital_status=random.choice(["Single", "Married", "Divorced", "Widowed", None]),
        gender=random.choice(["Male", "Female", "Other", None]),
        hire_date=fake.date_time_between(start_date="-5y", end_date="now").strftime("%Y-%m-%d"),
        termination_date=fake.date_time_between(start_date="-1y", end_date="now").strftime("%Y-%m-%d"),
        termination_reason=random.choice(["Resigned", "Laid off", "Retired", None]),
        employer=fake.company(),
        platform_ids=PlatformIds(
            employee_id=str(uuid.uuid4()),
            position_id=str(uuid.uuid4()),
            platform_user_id=str(uuid.uuid4())
        ),
        created_at=datetime.now(),
        update_at=datetime.now(),
        metadata=None
    )
    return employee


def test_random_employee(random_employee):
    assert isinstance(random_employee, Employee)
    assert random_employee.id is not None
    assert random_employee.account is not None
    assert random_employee.address is not None
    assert random_employee.first_name is not None
    assert random_employee.last_name is not None
    assert random_employee.full_name is not None
    assert random_employee.birth_date is not None
    assert random_employee.email is not None
    assert random_employee.phone_number is not None
    assert random_employee.job_title is not None
    assert random_employee.ssn is not None
    assert random_employee.marital_status in ["Single", "Married", "Divorced", "Widowed", None]
    assert random_employee.gender in ["Male", "Female", "Other", None]
    assert random_employee.hire_date is not None
    assert random_employee.termination_date is not None
    assert random_employee.termination_reason in ["Resigned", "Laid off", "Retired", None]
    assert random_employee.employer is not None
    assert random_employee.platform_ids is not None
    assert random_employee.created_at is not None
    assert random_employee.update_at is not None
    assert random_employee.metadata is None  # Assuming metadata is None for this test