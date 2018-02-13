---------------------
-- Try It Yourself --
---------------------

-- 1-1 --
SELECT  pls14.stabr,
        SUM(pls14.visits) AS visits_2014,
        SUM(pls14.gpterms) AS internet_connected_2014,
        SUM(pls09.visits) AS visits_2009,
        SUM(pls09.gpterms) AS internet_connected_2009,
        ROUND((CAST(SUM(pls14.gpterms) AS decimal(10,1)) - SUM(pls09.gpterms))
             / SUM(pls09.gpterms) * 100, 2) AS pct_change
FROM pls_fy2014_pupld14a pls14 JOIN pls_fy2009_pupld09a pls09
  ON pls14.fscskey = pls09.fscskey
WHERE pls14.gpterms >= 0 AND pls09.gpterms >= 0
GROUP BY pls14.stabr
ORDER BY pct_change DESC;


-- 1-2 --
SELECT  pls14.stabr,
        SUM(pls14.visits) AS visits_2014,
        SUM(pls14.pitusr) AS pulic_pc_usage_2014,
        SUM(pls09.visits) AS visits_2009,
        SUM(pls09.pitusr) AS public_pc_usage_2009,
        ROUND((CAST(SUM(pls14.pitusr) AS decimal(10,1)) - SUM(pls09.pitusr))
             / SUM(pls09.pitusr) * 100, 2) AS pct_change
FROM pls_fy2014_pupld14a pls14 JOIN pls_fy2009_pupld09a pls09
  ON pls14.fscskey = pls09.fscskey
WHERE pls14.pitusr >= 0 AND pls09.pitusr >= 0
GROUP BY pls14.stabr
ORDER BY pct_change DESC;

-- 2-1 --
SELECT  pls14.obereg,
    SUM(pls14.visits) AS visits_2014,
        SUM(pls09.visits) AS visits_2009,
        ROUND((CAST(SUM(pls14.visits) AS decimal(10,1)) - SUM(pls09.visits))
             / SUM(pls09.visits) * 100, 2) AS pct_change
FROM pls_fy2014_pupld14a pls14 JOIN pls_fy2009_pupld09a pls09
  ON pls14.fscskey = pls09.fscskey
WHERE pls14.visits >= 0 AND pls09.visits >= 0
GROUP BY pls14.obereg
ORDER BY pct_change DESC;


-- 2-2 --
CREATE TABLE obereg_codes (
  obereg varchar(2) CONSTRAINT obereg_key PRIMARY KEY,
    region varchar(100)
);

INSERT INTO obereg_codes
VALUES  ('01', 'New England (CT ME MA NH RI VT)'),
    ('02', 'Mid East (DE DC MD NJ NY PA)'),
        ('03', 'Great Lakes (IL IN MI OH WI)'),
        ('04', 'Plains (IA KS MN MO NE ND SD)'),
        ('05', 'Southeast (AL AR FL GA KY LA MS NC SC TN VA WV)'),
        ('06', 'Soutwest (AZ NM OK TX)'),
        ('07', 'Rocky Mountains (CO ID MT UT WY)'),
        ('08', 'Far West (AK CA HI NV OR WA)'),
        ('09', 'Outlying Areas (AS GU MP PR VI)');


-- 2-3 --
SELECT  obg.region AS region,
        SUM(pls14.visits) AS visits_2014,
        SUM(pls09.visits) AS visits_2009,
        ROUND((CAST(SUM(pls14.visits) AS decimal(10,1)) - SUM(pls09.visits))
             / SUM(pls09.visits) * 100, 2) AS pct_change
FROM pls_fy2014_pupld14a pls14 JOIN pls_fy2009_pupld09a pls09
  ON pls14.fscskey = pls09.fscskey
JOIN obereg_codes obg
  ON pls14.obereg = obg.obereg
WHERE pls14.visits >= 0 AND pls09.visits >= 0
GROUP BY obg.region
ORDER BY pct_change DESC;


-- 3--
SELECT *
FROM pls_fy2014_pupld14a pls14 FULL OUTER JOIN pls_fy2009_pupld09a pls09
  ON pls14.fscskey = pls09.fscskey
  WHERE pls14.libname IS NULL OR pls09.libname IS NULL;
