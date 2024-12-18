from pydantic import BaseModel, Field
from langchain.tools import StructuredTool


# Input schemas for each function
class NPVInput(BaseModel):
    cash_flows: list[float] = Field(description="A list of cash flows.")
    discount_rate: float = Field(description="The discount rate as a decimal.")


class FinancialStatementsInput(BaseModel):
    balance_sheet: dict = Field(description="Balance sheet data as a dictionary.")
    income_statement: dict = Field(description="Income statement data as a dictionary.")


class PaybackPeriodInput(BaseModel):
    cash_flows: list[float] = Field(description="A list of cash flows.")
    initial_investment: float = Field(description="The initial investment amount.")


class IRRInput(BaseModel):
    cash_flows: list[float] = Field(
        description="A list of cash flows starting with the initial investment as a negative value."
    )


class BreakEvenPointInput(BaseModel):
    fixed_costs: float = Field(description="Fixed costs.")
    variable_cost_per_unit: float = Field(description="Variable cost per unit.")
    price_per_unit: float = Field(description="Price per unit.")


class DepreciationInput(BaseModel):
    initial_cost: float = Field(description="Initial cost of the asset.")
    salvage_value: float = Field(description="Salvage value of the asset.")
    useful_life: int = Field(description="Useful life of the asset in years.")


class WorkingCapitalInput(BaseModel):
    current_assets: float = Field(description="Current assets.")
    current_liabilities: float = Field(description="Current liabilities.")


# Function definitions
def calculate_net_present_value(cash_flows: list[float], discount_rate: float) -> float:
    """Calculate the Net Present Value (NPV) of a series of cash flows."""
    try:
        return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows))
    except Exception as e:
        return f"Error in calculating NPV: {e}"


def analyze_financial_statements(balance_sheet: dict, income_statement: dict) -> dict:
    """Perform a basic analysis of financial statements."""
    try:
        return {
            "current_ratio": balance_sheet["current_assets"] / balance_sheet["current_liabilities"],
            "profit_margin": income_statement["net_income"] / income_statement["revenue"],
            "debt_to_equity_ratio": balance_sheet["total_liabilities"] / balance_sheet["total_equity"],
            "return_on_assets": income_statement["net_income"] / balance_sheet["total_assets"],
        }
    except KeyError as e:
        return f"Missing key in financial data: {e}"
    except ZeroDivisionError:
        return "Division by zero in financial ratio calculation."


def calculate_payback_period(cash_flows: list[float], initial_investment: float) -> str | int:
    """Calculate the Payback Period for an investment."""
    try:
        cumulative_cash_flow = 0
        for i, cf in enumerate(cash_flows, start=1):
            cumulative_cash_flow += cf
            if cumulative_cash_flow >= initial_investment:
                return i
        return "Payback period exceeds available cash flows."
    except Exception as e:
        return f"Error in calculating payback period: {e}"


def calculate_internal_rate_of_return(cash_flows: list[float]) -> float:
    """Calculate the Internal Rate of Return (IRR)."""
    from scipy.optimize import irr

    try:
        return irr(cash_flows)
    except Exception as e:
        return f"Error in calculating IRR: {e}"


def calculate_break_even_point(fixed_costs: float, variable_cost_per_unit: float, price_per_unit: float) -> float:
    """Calculate the Break-Even Point in units."""
    try:
        return fixed_costs / (price_per_unit - variable_cost_per_unit)
    except ZeroDivisionError:
        return "Price per unit must be greater than variable cost per unit."
    except Exception as e:
        return f"Error in calculating break-even point: {e}"


def depreciation_schedule(initial_cost: float, salvage_value: float, useful_life: int) -> list:
    """Calculate the depreciation schedule using the straight-line method."""
    try:
        annual_depreciation = (initial_cost - salvage_value) / useful_life
        return [annual_depreciation] * useful_life
    except ZeroDivisionError:
        return "Useful life cannot be zero."
    except Exception as e:
        return f"Error in calculating depreciation schedule: {e}"


def working_capital_management(current_assets: float, current_liabilities: float) -> dict:
    """Calculate working capital and the working capital ratio."""
    try:
        working_capital = current_assets - current_liabilities
        working_capital_ratio = current_assets / current_liabilities
        return {
            "working_capital": working_capital,
            "working_capital_ratio": working_capital_ratio,
        }
    except ZeroDivisionError:
        return "Current liabilities cannot be zero."
    except Exception as e:
        return f"Error in calculating working capital: {e}"


# Tool creation
npv_tool = StructuredTool.from_function(
    func=calculate_net_present_value,
    name="calculate_net_present_value",
    description='''calculate_net_present_value(cash_flows: list[float], discount_rate: float) -> float | str:
    Calculates the Net Present Value (NPV) of cash flows given a discount rate.
    Example usage:
    input: {"cash_flows": [100, 200, 300, 400, 500], "discount_rate": 0.1}
    returns: 139.75''',
    args_schema=NPVInput,
)

financial_analysis_tool = StructuredTool.from_function(
    func=analyze_financial_statements,
    name="analyze_financial_statements",
    description='''analyze_financial_statements(financial_data: dict) -> dict | str:
    Analyzes financial statements to compute basic ratios such as liquidity, profitability, and solvency.''',
    args_schema=FinancialStatementsInput,
)

payback_period_tool = StructuredTool.from_function(
    func=calculate_payback_period,
    name="calculate_payback_period",
    description='''calculate_payback_period(initial_investment: float, cash_flows: list[float]) -> float | str:
    Calculates the payback period for an investment based on initial investment and cash flows.''',
    args_schema=PaybackPeriodInput,
)

irr_tool = StructuredTool.from_function(
    func=calculate_internal_rate_of_return,
    name="calculate_internal_rate_of_return",
    description='''calculate_internal_rate_of_return(cash_flows: list[float]) -> float | str:
    Calculates the Internal Rate of Return (IRR) for a series of cash flows.''',
    args_schema=IRRInput,
)

break_even_tool = StructuredTool.from_function(
    func=calculate_break_even_point,
    name="calculate_break_even_point",
    description='''calculate_break_even_point(fixed_costs: float, variable_cost_per_unit: float, price_per_unit: float) -> float | str:
    Calculates the Break-Even Point in units based on fixed costs, variable cost per unit, and price per unit.''',
    args_schema=BreakEvenPointInput,
)

depreciation_tool = StructuredTool.from_function(
    func=depreciation_schedule,
    name="depreciation_schedule",
    description='''depreciation_schedule(asset_value: float, salvage_value: float, useful_life: int) -> list[float] | str:
    Calculates the depreciation schedule using the straight-line method based on asset value, salvage value, and useful life.''',
    args_schema=DepreciationInput,
)

working_capital_tool = StructuredTool.from_function(
    func=working_capital_management,
    name="working_capital_management",
    description='''working_capital_management(current_assets: float, current_liabilities: float) -> dict | str:
    Calculates working capital and the working capital ratio based on current assets and liabilities.''',
    args_schema=WorkingCapitalInput,
)
