import pandas as pd
from sklearn.linear_model import LinearRegression

"""---Start User Variables---"""
COST_PER_THERM = 2.67  # In Dollars
COST_PER_KWH = 0.38  # In Dollars

# Furnace AFUE (Annual Fuel Utilization Efficiency) Rating
AFUE = 80

# Temperature in Fahrenheit : Coefficient of Performance (COP) at that temperature
TEMPERATURE_COP_DATA = {
    17: 2.44,
    45: 3.62,
}

GRANULARITY = 5  # in Fahrenheit.  Set this to 5 if you have a ecobee thermostat.

"""---End User Variables---"""


def create_linear_regression_model(data_dict: dict):
    """
    Convert the dictionary to a pandas DataFrame, then creates a linear regression model.
    """
    df = pd.DataFrame(list(data_dict.items()), columns=["Temperature", "COP"])
    model = LinearRegression()
    model.fit(df[["Temperature"]], df["COP"])

    return model


def predict_temp_cop_dict(model, start_temp: int, end_temp: int, step: int):
    """
    Predicts the COP for a range of temperatures, and returns a dictionary of the results.
    """

    temp_cop_dict = {}
    for temp in range(start_temp, end_temp, step):
        temp_cop_dict[temp] = round(
            float(
                model.predict(pd.DataFrame([[temp]], columns=["Temperature"])).item()
            ),
            2,
        )

    return temp_cop_dict


def real_cost_per_therm(therm_cost, afue):
    """
    returns realized cost per therm, including furnace loss
    """

    afue_loss_overhead = 1 / (afue * 0.01)
    return afue_loss_overhead * therm_cost


def therm_to_kwh(therm_cost):
    GAS_ELECTRIC_CONSTANT = (
        29.3  # equivilant price per therm of natural gas is cost per kwh * 29.3
    )
    max_efficcency = therm_cost / GAS_ELECTRIC_CONSTANT
    afue_loss_overhead = (1 - (AFUE * 0.01)) + 1
    return max_efficcency * afue_loss_overhead


def main():
    """
    Returns the temperature at which you should set your thermostat crosspoint to
    if you have a dual fuel system.
    Otherwise, the lower the temperature is, the more you should consider installing a heat pump.
    """
    # creates ML model for Tempurature to COP relationship
    model = create_linear_regression_model(TEMPERATURE_COP_DATA)

    # uses the above model to predict COP for a range of outdoor temperatures
    temp_cop_dict = predict_temp_cop_dict(model, start_temp=-20, end_temp=75, step=GRANULARITY)

    # calculates the cost per therm of gas, including furnace loss
    furnace_cost_per_therm = real_cost_per_therm(COST_PER_THERM, AFUE)

    # calculates the equivilant cost per therm of the heat pump at each temperature
    for temp, cop in temp_cop_dict.items():
        heat_pump_cost_per_therm_equiv = (COST_PER_KWH / cop) * 29.3

        if heat_pump_cost_per_therm_equiv < furnace_cost_per_therm:
            print(
                f"heat pump is cheaper than gas when the outdoors is {temp}F and above"
            )
            return temp  # set your thermostat crosspoint here

    print("gas came out cheaper at all temperatures")
    return None


if __name__ == "__main__":
    main()
