import asyncio

import numpy as np
from sklearn.linear_model import LinearRegression

"""---Start User Variables---"""
COST_PER_THERM = 2.40  # In Dollars
COST_PER_KWH = 0.45  # In Dollars

# Furnace AFUE (Annual Fuel Utilization Efficiency) Rating
AFUE = 80

# Temperature in Fahrenheit : Coefficient of Performance (COP) at that temperature
TEMPERATURE_COP_DATA = {
    17: 2.44,
    45: 3.62,
}

GRANULARITY = 5  # in Fahrenheit.  Set this to 5 if you have a ecobee thermostat.

"""---End User Variables---"""


class PumpOrBurn:

    def __init__(self):
        self.cost_per_therm = COST_PER_THERM
        self.cost_per_kwh = COST_PER_KWH
        self.afue = AFUE
        self.temperature_cop_data = TEMPERATURE_COP_DATA
        self.granularity = GRANULARITY

    async def initialize(self):
        self.model = await self._create_linear_regression_model(
            self.temperature_cop_data
        )
        self.temp_cop_dict = await self._predict_temp_cop_dict(
            self.model, -20, 75, self.granularity
        )
        self.furnace_cost_per_therm = await self._real_cost_per_therm(
            self.cost_per_therm, self.afue
        )

    async def _create_linear_regression_model(self, data_dict: dict):
        """
        Convert the dictionary to numpy arrays, then creates a linear regression model.
        """
        temperatures = np.array(list(data_dict.keys())).reshape(-1, 1)
        cops = np.array(list(data_dict.values()))

        model = LinearRegression()
        model.fit(temperatures, cops)

        return model

    async def _predict_temp_cop_dict(
        self, model, start_temp: int, end_temp: int, step: int
    ):
        """
        Predicts the COP for a range of temperatures, and returns a dictionary of the results.
        """

        temp_cop_dict = {}
        for temp in range(start_temp, end_temp, step):
            temp_cop_dict[temp] = round(float(model.predict(np.array([[temp]]))), 2)

        return temp_cop_dict

    async def _real_cost_per_therm(self, therm_cost, afue):
        """
        returns realized cost per therm, including furnace loss
        """

        afue_loss_overhead = 1 / (afue * 0.01)
        return afue_loss_overhead * therm_cost

    async def _therm_to_kwh(self, therm_cost):
        GAS_ELECTRIC_CONSTANT = (
            29.3  # equivilant price per therm of natural gas is cost per kwh * 29.3
        )
        max_efficcency = therm_cost / GAS_ELECTRIC_CONSTANT
        afue_loss_overhead = (1 - (AFUE * 0.01)) + 1
        return max_efficcency * afue_loss_overhead

    async def calculate_result(self):
        for temp, cop in self.temp_cop_dict.items():
            heat_pump_cost_per_therm_equiv = (self.cost_per_kwh / cop) * 29.3

            if heat_pump_cost_per_therm_equiv < self.furnace_cost_per_therm:
                print(
                    f"heat pump is cheaper than gas when the outdoors is {temp}F and above"
                )
                return temp


async def main():
    pump_or_burn = PumpOrBurn()
    await pump_or_burn.initialize()
    await pump_or_burn.calculate_result()


if __name__ == "__main__":
    asyncio.run(main())
