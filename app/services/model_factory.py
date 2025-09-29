from typing import Literal
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

ModelName = Literal["linear", "random_forest"]

def make_model(name: ModelName = "linear", **kwargs):
    if name == "linear":
        return LinearRegression(**kwargs)
    if name == "random_forest":
        return RandomForestRegressor(
            n_estimators=200,
            random_state=0,
            **kwargs
        )
    raise ValueError(f"Unknown model '{name}'")
