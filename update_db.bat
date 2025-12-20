SET container_id=b9c36f8601fcfacf90ed351d3c2e10e227cb6813f4f702b9116d0b0f14ea7c8d


docker exec -it %container_id% psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS nadejda_94_django WITH (FORCE)";

docker exec -it %container_id% psql -U postgres -d postgres -c "CREATE DATABASE nadejda_94_django";

docker exec -i %container_id% psql -U postgres -d nadejda_94_django < d:\postgre_dump\dump_records.sql