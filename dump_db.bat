SET container_id=b9c36f8601fcfacf90ed351d3c2e10e227cb6813f4f702b9116d0b0f14ea7c8d


docker exec -t %container_id% pg_dump -U postgres nadejda_94_django > d:\postgre_dump\dump_records.sql
