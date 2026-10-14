-- Top skills by share of postings
WITH f AS (
  SELECT job_id, skill_name, is_generic
  FROM marts.mart_job_skill
  WHERE 1=1
    [[AND {{role}}]]
    [[AND {{city}}]]
    [[AND {{experience}}]]
    [[AND {{work_mode}}]]
)
SELECT skill_name AS skill,
       count(DISTINCT job_id) AS postings,
       round(100.0 * count(DISTINCT job_id) / NULLIF((SELECT count(DISTINCT job_id) FROM f), 0), 1) AS pct_of_postings
FROM f
WHERE NOT is_generic
GROUP BY skill_name
ORDER BY postings DESC
LIMIT 15;
