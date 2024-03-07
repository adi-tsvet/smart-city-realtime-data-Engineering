DROP TABLE IF EXISTS route_information;

CREATE TABLE route_information AS
SELECT 
    to_timestamp(v.timestamp, 'YYYY-MM-DD HH24:MI:SS.US') AS timestamp,
    CASE
        WHEN v.location ~ '^\[\d+(\.\d+)?,\s*-?\d+(\.\d+)?\]$'
        THEN split_part(trim(']' from trim('[' from v.location)), ',', 1)::numeric
        ELSE NULL
    END AS latitude,
    CASE
        WHEN v.location ~ '^\[\d+(\.\d+)?,\s*-?\d+(\.\d+)?\]$'
        THEN split_part(trim(']' from trim('[' from v.location)), ',', 2)::numeric
        ELSE NULL
    END AS longitude,
    CASE
        WHEN v.speed ~ '^\d+(\.\d+)?$'
        THEN v.speed::double precision
        ELSE NULL
    END AS speed,
    v.direction AS direction,
    e.type AS incident_type,
    e.status AS incident_status,
    w.weathercondition AS weather_condition
FROM
    vehicle_data v
LEFT JOIN
    emergency_data e ON v.timestamp = e.timestamp AND v.location = e.location
LEFT JOIN
    weather_data w ON v.timestamp = w.timestamp AND v.location = w.location;



SELECT * FROM route_information
ORDER BY timestamp;

SELECT * FROM weather_data;

