from pydantic import BaseModel, Field
from langchain.tools import StructuredTool


# Input schemas for each function
class MonthlySavingsInput(BaseModel):
    income: float = Field(description="Monthly income.")
    expenses: float = Field(description="Monthly expenses.")


class LoanEMIInput(BaseModel):
    principal: float = Field(description="Loan amount (principal).")
    rate: float = Field(description="Annual interest rate (in percentage).")
    tenure: int = Field(description="Loan tenure in months.")


class RetirementSavingsInput(BaseModel):
    current_savings: float = Field(description="Current savings amount.")
    monthly_contribution: float = Field(description="Monthly contribution to savings.")
    annual_rate_of_return: float = Field(description="Expected annual rate of return (in percentage).")
    years_until_retirement: int = Field(description="Years left until retirement.")


class EmergencyFundInput(BaseModel):
    monthly_expenses: float = Field(description="Monthly expenses.")
    months_covered: int = Field(description="Number of months the emergency fund should cover.")


class DebtToIncomeRatioInput(BaseModel):
    total_monthly_debt_payments: float = Field(description="Total monthly debt payments.")
    gross_monthly_income: float = Field(description="Gross monthly income.")


class InvestmentGrowthInput(BaseModel):
    initial_investment: float = Field(description="Initial investment amount.")
    annual_rate_of_return: float = Field(description="Annual rate of return (in percentage).")
    years: int = Field(description="Number of years for investment growth.")


# Function definitions
def monthly_savings(income: float, expenses: float) -> float:
    """Calculate monthly savings."""
    return income - expenses


def loan_emi(principal: float, rate: float, tenure: int) -> float:
    """Calculate loan EMI."""
    monthly_rate = rate / (12 * 100)
    emi = (principal * monthly_rate * ((1 + monthly_rate) ** tenure)) / (((1 + monthly_rate) ** tenure) - 1)
    return emi


def retirement_savings(
    current_savings: float, monthly_contribution: float, annual_rate_of_return: float, years_until_retirement: int
) -> float:
    """Estimate retirement savings using compound interest."""
    monthly_rate = annual_rate_of_return / 12 / 100
    months = years_until_retirement * 12
    future_value = current_savings * ((1 + monthly_rate) ** months)
    for _ in range(months):
        future_value += monthly_contribution * ((1 + monthly_rate) ** (months - _ - 1))
    return future_value


def emergency_fund(monthly_expenses: float, months_covered: int) -> float:
    """Calculate the recommended emergency fund amount."""
    return monthly_expenses * months_covered


def debt_to_income_ratio(total_monthly_debt_payments: float, gross_monthly_income: float) -> float:
    """Calculate debt-to-income (DTI) ratio."""
    if gross_monthly_income == 0:
        return "Gross monthly income cannot be zero."
    return (total_monthly_debt_payments / gross_monthly_income) * 100


def investment_growth(initial_investment: float, annual_rate_of_return: float, years: int) -> float:
    """Calculate future value of an investment with annual compounding."""
    return initial_investment * ((1 + annual_rate_of_return / 100) ** years)


# Tool creation
monthly_savings_tool = StructuredTool.from_function(
    func=monthly_savings,
    name="monthly_savings",
    description='''monthly_savings(income: float, expenses: float) -> float | str:
    Calculates monthly savings by subtracting expenses from income.''',
    args_schema=MonthlySavingsInput,
)

loan_emi_tool = StructuredTool.from_function(
    func=loan_emi,
    name="loan_emi",
    description='''loan_emi(principal: float, rate: float, tenure: int) -> float | str:
    Calculates the Equated Monthly Installment (EMI) for a loan based on principal, interest rate, and tenure.''',
    args_schema=LoanEMIInput,
)

retirement_savings_tool = StructuredTool.from_function(
    func=retirement_savings,
    name="retirement_savings",
    description='''retirement_savings(current_savings: float, monthly_contribution: float, annual_return: float, years: int) -> float | str:
    Estimates retirement savings based on current savings, monthly contributions, annual return rate, and investment period.''',
    args_schema=RetirementSavingsInput,
)

emergency_fund_tool = StructuredTool.from_function(
    func=emergency_fund,
    name="emergency_fund",
    description='''emergency_fund(monthly_expenses: float, months: int) -> float | str:
    Calculates the recommended emergency fund based on monthly expenses and the number of months of coverage required.''',
    args_schema=EmergencyFundInput,
)

debt_to_income_ratio_tool = StructuredTool.from_function(
    func=debt_to_income_ratio,
    name="debt_to_income_ratio",
    description='''debt_to_income_ratio(debt: float, income: float) -> float | str:
    Calculates the debt-to-income (DTI) ratio to assess financial health.''',
    args_schema=DebtToIncomeRatioInput,
)

investment_growth_tool = StructuredTool.from_function(
    func=investment_growth,
    name="investment_growth",
    description='''investment_growth(principal: float, rate: float, time: int, compounding_frequency: int) -> float | str:
    Calculates the future value of an investment using compound interest.''',
    args_schema=InvestmentGrowthInput,
)


# Example Usage
if __name__ == "__main__":
    # Monthly Savings
    print("Monthly Savings:", monthly_savings(5000, 3000))

    # Loan EMI
    print("Loan EMI:", loan_emi(500000, 7.5, 60))

    # Retirement Savings
    print(
        "Retirement Savings:",
        retirement_savings(current_savings=10000, monthly_contribution=500, annual_rate_of_return=6, years_until_retirement=20),
    )

    # Emergency Fund
    print("Emergency Fund:", emergency_fund(monthly_expenses=2000, months_covered=6))

    # Debt-to-Income Ratio
    print("Debt-to-Income Ratio:", debt_to_income_ratio(total_monthly_debt_payments=1500, gross_monthly_income=5000))

    # Investment Growth
    print("Investment Growth:", investment_growth(initial_investment=10000, annual_rate_of_return=8, years=10))
