from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.analytics.service import AnalyticsService
from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.statistics_result import StatisticsResult


def make_readings(temperatures, humidities, station_id=1):
    start = datetime(2026, 9, 30, tzinfo=timezone.utc)

    return [
        Reading(
            station_id=station_id,
            timestamp=start + timedelta(hours=index),
            values=(
                ReadingValue(
                    parameter_code="temperature",
                    value=Decimal(str(temperature)),
                ),
                ReadingValue(
                    parameter_code="humidity",
                    value=Decimal(str(humidity)),
                ),
            ),
        )
        for index, (temperature, humidity) in enumerate(
            zip(temperatures, humidities)
        )
    ]


def test_calculate_separates_parameters():
    readings = make_readings(
        temperatures=[1, 2, 3, 4],
        humidities=[60, 60, 60, 60],
    )

    results = AnalyticsService().calculate(readings)
    by_parameter = {
        result.parameter_code: result for result in results
    }

    assert len(results) == 2
    assert all(isinstance(result, StatisticsResult) for result in results)

    temperature = by_parameter["temperature"]
    assert temperature.count == 4
    assert temperature.average == 2.5
    assert temperature.median == 2.5
    assert temperature.standard_deviation == pytest.approx(1.11803398875)
    assert temperature.q1 == 1.75
    assert temperature.q3 == 3.25
    assert temperature.outliers == ()

    humidity = by_parameter["humidity"]
    assert humidity.average == 60.0
    assert humidity.standard_deviation == 0.0
    assert humidity.outliers == ()


def test_calculate_with_24_temperatures():
    temperatures = [20, 21, 22, 23] * 5 + [20, 21, 22, 40]
    readings = make_readings(temperatures, [60] * 24)

    results = AnalyticsService().calculate(readings)
    temperature = next(
        result
        for result in results
        if result.parameter_code == "temperature"
    )

    assert temperature.count == 24
    assert temperature.average == pytest.approx(533 / 24)
    assert temperature.outliers == (40.0,)


def test_calculate_empty_input():
    assert AnalyticsService().calculate([]) == []


def test_calculate_rejects_multiple_stations():
    readings = (
        make_readings([20, 21], [60, 61], station_id=1)
        + make_readings([22, 23], [62, 63], station_id=2)
    )

    with pytest.raises(ValueError, match="única estação"):
        AnalyticsService().calculate(readings)


def test_calculate_rejects_single_observation():
    readings = make_readings([20], [60])

    with pytest.raises(ValueError, match="duas observações"):
        AnalyticsService().calculate(readings)