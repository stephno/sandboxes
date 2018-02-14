---------------------
-- Try It Yourself --
---------------------

-- 1 --
SELECT  ROUND(
            (CORR(median_hh_income, pct_bachelors_higher)::numeric), 3
        ) AS bachelors_income_r,
        ROUND(
            (CORR(median_hh_income, pct_masters_higher)::numeric), 3
        ) AS masters_income_r
FROM acs_2011_2015_stats;

 -- 2-1 --
 SELECT city,
        st,
        population,
        motor_vehicle_theft,
        ROUND(
            (motor_vehicle_theft::numeric / population) * 1000, 1
        ) AS mvt_per_1000
FROM fbi_crime_data_2015
WHERE population >= 500000
ORDER BY (motor_vehicle_theft / population) DESC
LIMIT 10;

-- 2-2 --
SELECT  city,
        st,
        population,
        violent_crime,
        ROUND(
            (violent_crime::numeric / population) * 1000, 1
        ) AS vc_per_1000
FROM fbi_crime_data_2015
WHERE population >= 500000
ORDER BY (violent_crime / population) DESC
LIMIT 10;


-- 3 --
SELECT  libname,
        city,
        stabr,
        visits,
        RANK() OVER (ORDER BY visits DESC)
FROM pls_fy2014_pupld14a
WHERE popu_lsa >= 250000;
