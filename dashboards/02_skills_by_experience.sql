-- Top skills by experience level (share of postings within each level)
WITH f AS (
  SELECT job_id, skill_name, is_generic, experience_level, experience_level_order
  FROM marts.mart_job_skill
  WHERE 1=1
    [[AND {{role}}]]
    [[AND {{city}}]]
    [[AND {{experience}}]]
    [[AND {{work_mode}}]]
),
lvl AS (
  SELECT experience_level, count(DISTINCT job_id) AS jobs
  FROM f GROUP BY experience_level
),
top_skills AS (
  SELECT skill_name FROM f
  WHERE NOT is_generic
  GROUP BY skill_name
  ORDER BY count(DISTINCT job_id) DESC
  LIMIT 8
)
SELECT f.experience_level,
       f.skill_name AS skill,
       round(100.0 * count(DISTINCT f.job_id) / l.jobs, 1) AS pct_of_level_postings
FROM f
JOIN top_skills t ON t.skill_name = f.skill_name
JOIN lvl l ON l.experience_level = f.experience_level
WHERE NOT f.is_generic
GROUP BY f.experience_level, f.experience_level_order, f.skill_name, l.jobs
ORDER BY f.experience_level_order, pct_of_level_postings DESC;
