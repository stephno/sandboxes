---------------------
-- Try It Yourself --
---------------------

-- 1 --
SELECT ROUND( CAST( pi() * (5^2) AS numeric(4,2) ), 2);


-- 2 --
SELECT state_us_abbreviation AS states,
       geo_name AS counties,
       p0010001 AS total_population,
       p0010005 AS american_and_alaska_natives,
       ROUND(
                (CAS(p0010005 AS decimal(6,1)) / p0010001) * 100
        ,2) AS american_and_alaska_natives_pct
FROM us_counties_2010
WHERE state_us_abbreviation LIKE 'NY'
ORDER BY american_and_alaska_natives_pct DESC
LIMIT 1;


-- 3 --
SELECT state_us_abbreviation AS states,
       SUM(p0010001) AS total_population,
       (
            SELECT PERCENTILE_CONT(.5)
            WITHIN GROUP(ORDER BY p0010001)
        ) AS median_population
FROM us_counties_2010
WHERE state_us_abbreviation LIKE 'NY'
   OR state_us_abbreviation LIKE 'CA'
GROUP BY state_us_abbreviation
ORDER BY median_population DESC;
