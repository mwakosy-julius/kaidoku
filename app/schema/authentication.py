from pydantic import BaseModel, Field

email_or_phone_pattern = r"^(?:(?:[a-zA-Z0-9.!#$%&'*+=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})|(?:(?:\+|00)?255|0)?\d{9})$"
code_pattern = r"^[A-Za-z\d@$!%*?&#_%]{8,}$"


class Login(BaseModel):
    """Login Payload."""

    email_or_phone_number: str = Field(
        description="Email/Phone Number",
        min_length=5,
        max_length=50,
        pattern=email_or_phone_pattern,
        examples=["john.doe@example.com"],
    )
    password: str = Field(
        description="Password",
        pattern=code_pattern,
        min_length=8,
        max_length=50,
        examples=["@Abc12345678"],
    )

    # @model_validator(mode="after")
    # def post_validation(self) -> "Login":
    #     """Validate values."""
    #     self.email_or_phone_number = self.email_or_phone_number.lower().strip()
    #     if not re.match(email_or_phone_pattern, self.email_or_phone_number):
    #         msg = "Invalid value provided, it should be either phone or email"
    #         raise ValueError(msg)
    #     # Check if is phone number
    #     if "@" not in self.email_or_phone_number:
    #         self.email_or_phone_number = Validations.phone_number_validator(
    #             self.email_or_phone_number
    #         )
    #     if not re.match(code_pattern, self.password):
    #         msg = "Invalid password format"
    #         raise ValueError(msg)
    #     return self

    @property
    def is_email(self) -> bool:
        """Check whether its email or phone number."""
        return "@" in self.email_or_phone_number
