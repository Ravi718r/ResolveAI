from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.repositories.customer import CustomerRepository


def test_create_and_get_customer():

    db: Session = SessionLocal()

    try:
        repository = CustomerRepository(db)

        email = "test.resolveai@example.com"

        existing = repository.get_by_email(email)

        if existing:
            repository.delete(existing.id)

        customer = repository.create(
            name="Test Customer",
            email=email,
        )

        assert customer.id is not None
        assert customer.name == "Test Customer"
        assert customer.email == email

        fetched = repository.get_by_id(customer.id)

        assert fetched is not None
        assert fetched.id == customer.id

        fetched_by_email = repository.get_by_email(email)

        assert fetched_by_email is not None
        assert fetched_by_email.id == customer.id

    finally:
        db.close()