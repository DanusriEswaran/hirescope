-- Work-mode split
SELECT work_mode, count(*) AS postings
FROM marts.mart_job
WHERE 1=1
  [[AND {{role}}]]
  [[AND {{city}}]]
  [[AND {{experience}}]]
  [[AND {{work_mode}}]]
GROUP BY work_mode
ORDER BY postings DESC;
