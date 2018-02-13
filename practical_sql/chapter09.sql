---------------------
-- Try It Yourself --
---------------------

-- 1 --
CREATE TABLE meat_poultry_egg_inspect_bckp AS
SELECT * FROM meat_poultry_egg_inspect;

ALTER TABLE meat_poultry_egg_inspect_bckp ADD COLUMN meat_processing boolean;
ALTER TABLE meat_poultry_egg_inspect_bckp ADD COLUMN poultry_processing boolean;


-- 2 --
UPDATE meat_poultry_egg_inspect_bckp
SET meat_processing = TRUE
WHERE activities ILIKE '%Meat Processing%';

UPDATE meat_poultry_egg_inspect_bckp
SET poultry_processing = TRUE
WHERE activities ILIKE '%Poultry Prcessing%';


-- 3 --
SELECT  COUNT(meat_processing),
        COUNT(poultry_processing)
FROM meat_poultry_egg_inspect_bckp;

-- 3 bis --
SELECT  COUNT(*)
FROM meat_poultry_egg_inspect_bckp
WHERE meat_processing = TRUE
  AND poultry_processing = TRUE;

-- Note On Question 3
---------------------
-- May a query also displaying the company names
-- show that the total results for both meat_processing
-- and poultry_processing might be irrelevant?
--
/* SELECT   company,
            COUNT(*)
   FROM meat_poultry_egg_inspect_bckp
   WHERE meat_processing = TRUE
     AND poultry_processing = TRUE
   GROUP BY company
   ORDER BY company ASC;
*/
--
-- Here are a few snippets showing duplicates.
--
/* company                          meat_and_poultry
   -------------------------        ----------------
   -- snip --
   Ajinomoto Windsor Inc.                          1
   Ajinomoto Windsor, Inc.                         7
   -- snip --
   AdvancePierre Foods, Inc                        1
   AdvancePierre Foods, Inc.                       6
   -- snip --
*/
