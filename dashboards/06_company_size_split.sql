-- Company-size split
SELECT company_size_bucket, count(*) AS postings
FROM marts.mart_job
WHERE 1=1
  [[AND {{role}}]]
  [[AND {{city}}]]
  [[AND {{experience}}]]
  [[AND {{work_mode}}]]
GROUP BY company_size_bucket
ORDER BY postings DESC;
