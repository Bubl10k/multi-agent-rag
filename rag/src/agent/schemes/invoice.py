from pydantic import BaseModel


class ExtractDetailsOutput(BaseModel):
    client_info: dict
    line_items: list[dict]
    invoice_meta: dict
    tax_rate: float
    is_complete: bool
    missing_fields: list[str]
    retry_count: int
    max_retries: int
    validation_errors: list[str]


class ValidateOutput(BaseModel):
    line_items: list[dict]
    subtotal: float
    tax_amount: float
    total: float
    is_valid: bool
    validation_errors: list[str]


class FixItemsOutput(BaseModel):
    client_info: dict
    line_items: list[dict]
    invoice_meta: dict
    tax_rate: float
    retry_count: int


class GenerateInvoiceOutput(BaseModel):
    invoice_meta: dict


class FormatInvoiceOutput(BaseModel):
    invoice_file_url: str | None
    invoice_file_name: str
