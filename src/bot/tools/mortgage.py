from typing import Literal

from lazyopenai.types import BaseTool
from mortgage import Loan
from pydantic import Field


class LoanTool(BaseTool):
    """
    A tool for calculating and summarizing loan details based on input parameters.
    """

    keywords: list[str] = Field(..., description="List of keywords associated with the loan tool.")
    principal: float = Field(..., description="The original sum of money borrowed.")
    interest: float = Field(
        ...,
        description="The annual interest rate of the loan. Interest rate must be between zero and one.",
    )
    term: float = Field(..., description="The duration of the loan.")
    term_unit: Literal["days", "months", "years"] = Field(..., description="The unit of time for the loan term.")
    compounded: Literal["daily", "monthly", "annually"] = Field(
        ..., description="The frequency at which interest is compounded."
    )
    currency: str = Field(..., description="The currency symbol used in the loan summary.")

    def __call__(self) -> str:
        """
        Calculates the loan details and returns a formatted summary.
        """

        loan = Loan(
            principal=self.principal,
            interest=self.interest,
            term=self.term,
            term_unit=self.term_unit,
            compounded=self.compounded,
            currency=self.currency,
        )

        lines = [
            f"Original Balance: {loan._currency}{loan.principal:>11,}",
            f"Interest Rate: {loan.interest:>11} %",
            f"APY: {loan.apy:>11} %",
            f"APR: {loan.apr:>11} %",
            f"Term: {loan.term:>11} {loan.term_unit}",
            f"Monthly Payment: {loan._currency}{loan.monthly_payment:>11}",
            "",
            f"Total principal payments: {loan._currency}{loan.total_principal:>11,}",
            f"Total interest payments: {loan._currency}{loan.total_interest:>11,}",
            f"Total payments: {loan._currency}{loan.total_paid:>11,}",
            f"Interest to principal: {loan.interest_to_principle:>11} %",
            f"Years to pay: {loan.years_to_pay:>11}",
        ]

        return "\n".join(lines)
