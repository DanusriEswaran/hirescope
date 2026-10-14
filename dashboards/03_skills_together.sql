-- Skills often asked together (skills with >= 50 postings overall)
SELECT skill_a || ' + ' || skill_b AS skill_pair,
       count(*) AS postings
FROM marts.mart_skill_pairs
WHERE 1=1
  [[AND {{role}}]]
  [[AND {{city}}]]
  [[AND {{experience}}]]
  [[AND {{work_mode}}]]
GROUP BY skill_a, skill_b
ORDER BY postings DESC
LIMIT 15;
