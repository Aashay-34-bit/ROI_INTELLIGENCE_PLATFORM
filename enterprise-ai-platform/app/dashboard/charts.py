import pandas as pd
import plotly.express as px


def bar_chart(data: dict[str, float], title: str):
    return px.bar(
        pd.DataFrame({"name": list(data), "value": list(data.values())}),
        x="name",
        y="value",
        title=title,
    )
