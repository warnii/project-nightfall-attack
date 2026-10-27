"""Analytical event timeline visualization."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import plotly.express as px
import plotly.graph_objects as go


def create_timeline(events: list[dict[str, Any]]) -> go.Figure:
    if not events:
        figure = go.Figure()
        figure.update_layout(title="No evidence matches the selected filters")
        return figure
    chart_events = [
        {
            **event,
            "timestamp": datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")),
        }
        for event in events
    ]
    figure = px.scatter(
        chart_events,
        x="timestamp",
        y="category",
        color="category",
        hover_name="evidence_id",
        hover_data={
            "description": True,
            "host_or_identity": True,
            "confidence": ":.0%",
            "timestamp": True,
            "category": False,
        },
        title="Evidence timeline (timestamps are synthetic and in UTC)",
        labels={"timestamp": "Timestamp (UTC)", "category": "Evidence category"},
    )
    figure.update_traces(marker={"size": 13}, showlegend=False)
    figure.update_layout(height=max(340, 70 * len({event["category"] for event in events})))
    return figure
