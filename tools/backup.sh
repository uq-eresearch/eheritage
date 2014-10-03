


# Create Repository
curl -XPUT 'http://localhost:9200/_snapshot/eheritage_backup' -d '{
    "type": "fs",
    "settings": {
        "location": "/mnt/backups/eheritage_backup",
        "compress": true
    }
}'

curl -XPUT 'http://localhost:9200/_snapshot/my_s3_repository' -d '{
    "type": "s3",
    "settings": {
        "bucket": "es_backups"
    }
}'


curl -XPUT 'http://localhost:9200/_snapshot/initial_data' -d '{
    "type": "fs",
    "settings": {
        "location": "/mnt/restores",
        "compress": true
    }
}'


# Check repository
curl -XGET 'http://localhost:9200/_snapshot/eheritage_backup?pretty'


curl -XGET 'http://localhost:9200/_snapshot/my_s3_repository?pretty'

curl -XGET 'http://localhost:9200/_snapshot?pretty'

exit

# Create snapshot
curl -XPUT "localhost:9200/_snapshot/eheritage_backup/snapshot_1?wait_for_completion=true"

curl -XPUT "localhost:9200/_snapshot/eheritage_backup/snapshot_1?wait_for_completion=true" -d '{
    "indices": "eheritage_v3",
    "ignore_unavailable": "true",
    "include_global_state": false
}'



# List Snapshots
curl -XGET 'http://localhost:9200/_snapshot/eheritage_backup/_all?pretty'

exit


# Restore from Snapshot

curl -XPOST "localhost:9200/_snapshot/eheritage_backup/snapshot_1/_restore?wait_for_completion=true"


# Delete Snapshot
curl -XDELETE "localhost:9200/_snapshot/eheritage_backup/snapshot_1"



# Get Node Information and configuration
curl -XGET 'http://localhost:9200/_nodes'


tar czf ~/eheritage_backup.tar.gz eheritage_backup/


sudo apt-get install python-swiftclient


# List Indexes
curl 'localhost:9200/_cat/indices?v'
curl 'localhost:9200/_cat/aliases?v'


curl -XPUT 'http://localhost:9200/_snapshot/eheritage_backup' -d '{
    "type": "fs",
    "settings": {
        "location": "/data/snapshots/backups/eheritage_backup",
        "compress": true
    }
}'



