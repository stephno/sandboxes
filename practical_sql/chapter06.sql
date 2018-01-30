---------------------
-- Try It Yourself --
---------------------

-- 1 --
SELECT (c2000.state_us_abbreviation,
        c2010.state_us_abbreviation) AS states,
        c2000.geo_name AS counties_2000,
        c2010.geo_name AS counties_2010
FROM us_counties_2000 c2000 FULL OUTER JOIN us_counties_2010 c2010
  ON c2000.state_fips = c2010.state_fips
  AND c2000.county_fips = c2010.county_fips
WHERE c2000.geo_name IS NULL
  OR  c2010.geo_name IS NULL;


-- 2 --
SELECT mt.states AS states,
       mt.median_2000 AS median_2000,
       mt.median_2010 AS median_2010,
       ROUND(
           CAST(((mt.median_2010 - mt.median_2000)
           / mt.median_2000) AS numeric(8,4)) * 100, 2) AS median_pct_change
FROM ( SELECT c2000.state_us_abbreviation AS states,
       (
           SELECT PERCENTILE_CONT(.5)
           WITHIN GROUP(ORDER BY c2000bis.p0010001)
           FROM us_counties_2000 c2000bis
           WHERE c2000bis.state_us_abbreviation = c2000.state_us_abbreviation
       ) AS median_2000,
       (
           SELECT PERCENTILE_CONT(.5)
           WITHIN GROUP(ORDER BY c2010bis.p0010001)
           FROM us_counties_2010 c2010bis
           WHERE c2010bis.state_us_abbreviation = c2000.state_us_abbreviation
       ) AS median_2010
      FROM us_counties_2000 c2000 INNER JOIN us_counties_2010 c2010
      ON c2000.state_fips = c2010.state_fips
      AND c2000.county_fips = c2010.county_fips
      GROUP BY c2000.state_us_abbreviation
    ) AS mt
ORDER BY mt.states ASC;


-- 3 --
SELECT losses.states AS states,
       losses.pop_2000 AS population_2000,
       losses.pop_2010 AS population_2010,
       (losses.pop_2010 - losses.pop_2000) AS losses
FROM ( SELECT c2000.state_us_abbreviation as states,
       (
           SELECT SUM(c2000bis.p0010001)
           FROM us_counties_2000 c2000bis
           WHERE c2000bis.state_us_abbreviation = c2000.state_us_abbreviation
       ) AS pop_2000,
       (
           SELECT SUM(c2010bis.p0010001)
           FROM us_counties_2010 c2010bis
           WHERE c2010bis.state_us_abbreviation = c2000.state_us_abbreviation
       ) AS pop_2010
       FROM us_counties_2000 c2000 FULL OUTER JOIN us_counties_2010 c2010
         ON c2000.state_fips = c2010.state_fips
        AND c2000.county_fips = c2010.state_fips
       GROUP BY c2000.state_us_abbreviation
     ) AS losses
WHERE losses.pop_2010 < losses.pop_2000;

