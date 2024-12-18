from pydantic import BaseModel, Field
from langchain.tools import StructuredTool


# Input schemas for each function
class StockPriceChangeInput(BaseModel):
    open_price: float = Field(description="The opening price of the stock.")
    close_price: float = Field(description="The closing price of the stock.")


class MovingAverageInput(BaseModel):
    prices: list[float] = Field(description="A list of historical stock prices.")
    period: int = Field(description="The number of periods over which to calculate the moving average.")


class BollingerBandsInput(BaseModel):
    prices: list[float] = Field(description="A list of historical stock prices.")
    period: int = Field(description="The number of periods for the moving average.")
    num_std_dev: float = Field(description="The number of standard deviations for the Bollinger Bands.")


class VolatilityInput(BaseModel):
    prices: list[float] = Field(description="A list of historical stock prices.")
    period: int = Field(description="The number of periods for calculating volatility.")


class ExponentialMovingAverageInput(BaseModel):
    prices: list[float] = Field(description="A list of historical stock prices.")
    period: int = Field(description="The number of periods for calculating the EMA.")


class RSIInput(BaseModel):
    prices: list[float] = Field(description="A list of historical stock prices.")
    period: int = Field(description="The number of periods for calculating the RSI.")


# Function definitions
def stock_price_change(open_price: float, close_price: float) -> float | str:
    """Calculate percentage change in stock price."""
    try:
        return ((close_price - open_price) / open_price) * 100
    except ZeroDivisionError:
        return "Open price cannot be zero."


def moving_average(prices: list[float], period: int) -> float | str:
    """Calculate the moving average for a given period."""
    if len(prices) < period:
        return "Not enough data points to calculate the moving average."
    try:
        return sum(prices[-period:]) / period
    except Exception as e:
        return f"Error in calculating moving average: {e}"


def bollinger_bands(prices: list[float], period: int, num_std_dev: float) -> dict[str, float] | str:
    """Calculate Bollinger Bands."""
    if len(prices) < period:
        return "Not enough data points to calculate Bollinger Bands."
    try:
        ma = moving_average(prices, period)
        std_dev = (sum((price - ma) ** 2 for price in prices[-period:]) / period) ** 0.5
        upper_band = ma + (num_std_dev * std_dev)
        lower_band = ma - (num_std_dev * std_dev)
        return {"upper_band": upper_band, "lower_band": lower_band, "moving_average": ma}
    except Exception as e:
        return f"Error in calculating Bollinger Bands: {e}"


def volatility(prices: list[float], period: int) -> float | str:
    """Calculate price volatility as standard deviation over a period."""
    if len(prices) < period:
        return "Not enough data points to calculate volatility."
    try:
        ma = moving_average(prices, period)
        std_dev = (sum((price - ma) ** 2 for price in prices[-period:]) / period) ** 0.5
        return std_dev
    except Exception as e:
        return f"Error in calculating volatility: {e}"


def exponential_moving_average(prices: list[float], period: int) -> float | str:
    """Calculate the exponential moving average (EMA)."""
    if len(prices) < period:
        return "Not enough data points to calculate EMA."
    try:
        multiplier = 2 / (period + 1)
        ema = prices[0]  # Start with the first price as the initial EMA
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    except Exception as e:
        return f"Error in calculating EMA: {e}"


def rsi(prices: list[float], period: int) -> float | str:
    """Calculate the Relative Strength Index (RSI)."""
    if len(prices) < period + 1:
        return "Not enough data points to calculate RSI."
    try:
        gains = []
        losses = []
        for i in range(1, period + 1):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        return 100 - (100 / (1 + rs))
    except Exception as e:
        return f"Error in calculating RSI: {e}"


# Tool creation
stock_price_change_tool = StructuredTool.from_function(
    func=stock_price_change,
    name="StockPriceChangeTool",
    description="Calculate the percentage change in stock price based on opening and closing prices.",
    args_schema=StockPriceChangeInput,
)

moving_average_tool = StructuredTool.from_function(
    func=moving_average,
    name="moving_average",
    description='''moving_average(prices: list[float], period: int) -> float | str:
    Calculates the moving average of stock prices over a specified period.''',
    args_schema=MovingAverageInput,
)

bollinger_bands_tool = StructuredTool.from_function(
    func=bollinger_bands,
    name="BollingerBandsTool",
    description="Calculate Bollinger Bands for stock prices.",
    args_schema=BollingerBandsInput,
)

volatility_tool = StructuredTool.from_function(
    func=volatility,
    name="VolatilityTool",
    description="Calculate price volatility over a specified period.",
    args_schema=VolatilityInput,
)

exponential_moving_average_tool = StructuredTool.from_function(
    func=exponential_moving_average,
    name="ExponentialMovingAverageTool",
    description="Calculate the exponential moving average (EMA) of stock prices.",
    args_schema=ExponentialMovingAverageInput,
)

rsi_tool = StructuredTool.from_function(
    func=rsi,
    name="rsi",
    description='''rsi(prices: list[float], period: int) -> float | str:

Calculates the Relative Strength Index (RSI) for the given list of prices over the specified period.
prices is a list of floats representing numerical data points (e.g., stock prices).
period is an integer representing the number of consecutive data points used to calculate the RSI.
Rules and Behavior:

If the length of prices is less than period + 1, the function returns "Not enough data points to calculate RSI."
RSI is calculated using the following steps:
Compute the difference between consecutive elements in prices.
Separate differences into gains (positive values) and losses (absolute negative values).
Calculate the average gain and average loss over the specified period.
Compute the Relative Strength (RS) as average gain / average loss.
Calculate the RSI using the formula:
RSI = 100 - (100 / (1 + RS))
If average loss is zero, RS is treated as zero.
Handles exceptions during computation and returns a string in the format "Error in calculating RSI: <error_message>" if any issues occur.
Restrictions:

The prices list must contain at least period + 1 elements to compute the RSI.
Ensure all elements in prices are numerical values.
Example Usage:

rsi([50.0, 51.5, 52.0, 51.0, 52.5], 3) returns the RSI value for a 3-period window.
rsi([45.0, 46.0], 3) returns "Not enough data points to calculate RSI." due to insufficient elements.''',
    args_schema=RSIInput,
)

# Example Usage
if __name__ == "__main__":
    # Example inputs
    example_prices = [100, 102, 104, 103, 105, 106, 108, 110, 112, 114]
    example_period = 5
    example_open_price = 100
    example_close_price = 110

    # Stock Price Change
    print("Stock Price Change (%):", stock_price_change(example_open_price, example_close_price))

    # Moving Average
    print("Moving Average:", moving_average(example_prices, example_period))

    # Bollinger Bands
    print("Bollinger Bands:", bollinger_bands(example_prices, example_period, 2))

    # Volatility
    print("Volatility:", volatility(example_prices, example_period))

    # Exponential Moving Average
    print("Exponential Moving Average:", exponential_moving_average(example_prices, example_period))

    # RSI
    print("RSI:", rsi(example_prices, example_period))
