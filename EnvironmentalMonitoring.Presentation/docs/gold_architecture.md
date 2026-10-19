# Modelo:                               
                               
                               +---------------------------+
                               |        DimDate            |
                               +---------------------------+
                               | DateKey PK                |
                               | FullDate                  |
                               | CalendarYear              |
                               | CalendarSemester          |
                               | CalendarQuarter           |
                               | MonthNumber               |
                               | MonthName                 |
                               | DayOfMonth                |
                               | DayOfWeekNumber           |
                               | DayOfWeekName             |
                               | IsWeekend                 |
                               | IsBusinessDay             |
                               +------------+--------------+
                                            |
                                            | 1
                                            |
                                            | N
                                            |
                               +------------+--------------+
                               |     FactMeasurements      |
                               +---------------------------+
                               | MeasurementKey PK         |
                               |                           |
                               | StationKey FK             |
                               | ParameterKey FK           |
                               | DateKey FK                |
                               | TimeKey FK                |
                               |                           |
                               | ReadingId                 |
                               | ReadingValueId UQ         |
                               | MeasurementDateTime       |
                               |                           |
                               | MeasuredValue             |
                               | MovingAverageValue        |
                               | ZScore                    |
                               | IqrLowerBound             |
                               | IqrUpperBound             |
                               | IsOutlier                 |
                               | OutlierMethod             |
                               |                           |
                               | LoadedAt                  |
                               | PipelineRunId             |
                               +----+------------+-----+---+
                                    |            |     |
                                  N |          N |     | N
                                    |            |     |
                                  1 |          1 |     | 1
                                    |            |     |
              +---------------------+            |     +-------------------------+
              |                                  |                               |
              |                                  |                               |
 +------------+--------------+       +-----------+-----------+       +-----------+-----------+
 |       DimStation          |       |       DimTime         |       |     DimParameter      |
 +---------------------------+       +-----------------------+       +-----------------------+
 | StationKey PK             |       | TimeKey PK            |       | ParameterKey PK       |
 | StationId NK/UQ           |       | FullTime UQ           |       | ParameterId NK/UQ     |
 | StationCode UQ            |       | HourNumber            |       | ParameterCode UQ      |
 | StationName               |       | MinuteNumber          |       | ParameterApiCode      |
 | Latitude                  |       | SecondNumber          |       | ParameterName         |
 | Longitude                 |       +-----------------------+       | Unit                  |
 +---------------------------+                                       | CategoryId            |
                                                                     | CategoryCode          |
                                                                     | CategoryName          |
                                                                     +-----------------------+


# Fluxo Silver -> Gold:
CAMADA SILVER                                CAMADA GOLD
────────────────                             ───────────

Stations ──────────────────────────────────► DimStation
  Id                                          StationId
  Code                                        StationCode
  Name                                        StationName
  Latitude                                    Latitude
  Longitude                                   Longitude


Parameters ───────────────┐
                          ├────────────────► DimParameter
ParameterCategories ──────┘
                                              ParameterId
                                              ParameterCode
                                              ParameterApiCode
                                              ParameterName
                                              Unit
                                              CategoryId
                                              CategoryCode
                                              CategoryName


Calendário gerado ─────────────────────────► DimDate


Horários gerados ──────────────────────────► DimTime


Readings ─────────────────┐
                          ├────────────────► FactMeasurements
ReadingValues ────────────┘
                                              ReadingId
                                              ReadingValueId
                                              MeasurementDateTime
                                              MeasuredValue
                                              +
                                              StationKey
                                              ParameterKey
                                              DateKey
                                              TimeKey
                                              +
                                              estatísticas