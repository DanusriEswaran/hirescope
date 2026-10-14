-- Salary range by skill (postings with a disclosed salary only; skills with >= 15 such postings)
SELECT skill_name AS skill,
       count(DISTINCT job_id) AS postings_with_salary,
       round(cast(percentile_cont(0.25) WITHIN GROUP (ORDER BY salary_mid_lpa) AS numeric), 1) AS p25_lpa,
       round(cast(percentile_cont(0.50) WITHIN GROUP (ORDER BY salary_mid_lpa) AS numeric), 1) AS median_lpa,
       round(cast(percentile_cont(0.75) WITHIN GROUP (ORDER BY salary_mid_lpa) AS numeric), 1) AS p75_lpa
FROM marts.mart_job_skill
WHERE salary_disclosed
  AND NOT is_generic
  [[AND {{role}}]]
  [[AND {{city}}]]
  [[AND {{experience}}]]
  [[AND {{work_mode}}]]
GROUP BY skill_name
HAVING count(DISTINCT job_id) >= 15
ORDER BY median_lpa DESC
LIMIT 15;
