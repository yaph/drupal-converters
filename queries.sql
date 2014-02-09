-- select existing url aliases for nodes
SELECT n.nid, ua.dst FROM node n
INNER JOIN url_alias ua ON ua.src = CONCAT( 'node/', n.nid )
WHERE n.status =1 ORDER BY n.changed DESC
