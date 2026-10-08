from app.db.models import Customer
from app.repositories.customer import CustomerRepository


class CustomerService:

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def create_customer(
        self,
        name: str,
        email: str,
    ) -> Customer:

        existing_customer = self.customer_repository.get_by_email(email)

        if existing_customer:
            raise ValueError(
                "Customer with this email already exists"
            )

        return self.customer_repository.create(
            name=name,
            email=email,
        )

    def get_customer(
        self,
        customer_id: int,
    ) -> Customer | None:

        return self.customer_repository.get_by_id(customer_id)

    def get_customer_by_email(
        self,
        email: str,
    ) -> Customer | None:

        return self.customer_repository.get_by_email(email)

    def list_customers(self) -> list[Customer]:

        return self.customer_repository.get_all()

    def update_customer(
        self,
        customer_id: int,
        name: str | None = None,
        email: str | None = None,
    ) -> Customer | None:

        customer = self.customer_repository.get_by_id(customer_id)

        if customer is None:
            return None

        if email is not None:
            existing_customer = (
                self.customer_repository.get_by_email(email)
            )

            if (
                existing_customer is not None
                and existing_customer.id != customer_id
            ):
                raise ValueError(
                    "Customer with this email already exists"
                )

        return self.customer_repository.update(
            customer_id=customer_id,
            name=name,
            email=email,
        )

    def delete_customer(
        self,
        customer_id: int,
    ) -> bool:

        customer = self.customer_repository.get_by_id(customer_id)

        if customer is None:
            return False

        return self.customer_repository.delete(customer_id)
