---------------------
-- Try It Yourself --
---------------------

-- 1 --
SELECT  trip_id,
        tpep_dropoff_datetime AS dropoff,
        tpep_pickup_datetime AS pickup,
        tpep_dropoff_datetime - tpep_pickup_datetime AS ride_length
FROM nyc_yellow_taxi_trips_2016_06_01
ORDER BY ride_length DESC;


-- 2 --
SELECT  '2100-01-01 00:00:00-05' AT TIME ZONE 'US/Eastern' AS "New York",
        '2100-01-01 00:00:00-05' AT TIME ZONE 'Europe/London' AS "London",
        '2100-01-01 00:00:00-05' AT TIME ZONE 'Africa/Johannesburg' AS "Johannesburg",
        '2100-01-01 00:00:00-05' AT TIME ZONE 'Europe/Moscow' AS "Moscow",
        '2100-01-01 00:00:00-05' AT TIME ZONE 'Australia/Melbourne' AS "Melbourne";


-- 3 --
SELECT  ROUND(
            CORR(total_amount,
                 (date_part('epoch', tpep_dropoff_datetime) -
                  date_part('epoch', tpep_pickup_datetime))
                )::numeric, 2
        ) AS amount_time_corr,
        ROUND(
            REGR_R2(total_amount,
                    (date_part('epoch', tpep_dropoff_datetime) -
                     date_part('epoch', tpep_pickup_datetime))
                   )::numeric, 3
        ) AS amount_time_rsquared,
        ROUND(
            CORR(total_amount, trip_distance)::numeric, 2
        ) AS distance_corr,
        ROUND(
            REGR_R2(total_amount, trip_distance)::numeric, 3
        ) AS distance_rsquared
FROM nyc_yellow_taxi_trips_2016_06_01
WHERE (tpep_dropoff_datetime - tpep_pickup_datetime <= '3 hours'::interval);
