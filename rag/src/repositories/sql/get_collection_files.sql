SELECT DISTINCT e.cmetadata->>'source' AS source
FROM langchain_pg_embedding e
JOIN langchain_pg_collection c ON e.collection_id = c.uuid
WHERE c.name = :name
  AND e.cmetadata->>'source' IS NOT NULL
ORDER BY source