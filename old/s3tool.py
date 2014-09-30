#!/usr/bin/python
#remember to run "source ec2rc.sh"
#
# from https://support.rc.nectar.org.au/forum/viewtopic.php?f=3&t=256
# by Peter Embleton

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto,os,sys

connection = S3Connection(
aws_access_key_id=os.environ["EC2_ACCESS_KEY"],
aws_secret_access_key=os.environ["EC2_SECRET_KEY"],
port=8888,
host='swift.rc.nectar.org.au',
is_secure=True,
calling_format=boto.s3.connection.OrdinaryCallingFormat())

if len(sys.argv) == 2:
        if sys.argv[1] == "-?": 
                print "filecopy.py ls - display a list of all the buckets available" 
                print "filecopy.py ls <bucket name> - lists all the files in the bucket" 
                print "filecopy.py mkdir <bucket name> - creates a bucket" 
                print "filecopy.py rmdir <bucket name> - creates a bucket" 
                print "filecopy.py cp <bucket name> <file to put there> <path in the bucket> - copies a file to the specifed bucket and lists it with the specifed path" 
                print "filecopy.py rm <bucket name> <file to delete>  - deletes a file to the specifed bucket" 
                print "filecopy.py cp -r <bucket name> <folder to put there>" 
                print "filecopy.py rm -r <bucket name> - deletes all files out of the bucket"
        elif sys.argv[1] == "ls":       
                buckets = connection.get_all_buckets()
                print buckets

if len(sys.argv) == 3: 
        if sys.argv[1] == "ls":
                bucket = connection.lookup(sys.argv[2])
                for key in bucket:
                        print key.name
        elif sys.argv[1] == "mkdir": 
                bucket = connection.create_bucket(sys.argv[2])
        elif sys.argv[1] == "rmdir": 
                print "Delete bucket ",sys.argv[2]
                bucket = connection.delete_bucket(sys.argv[2])

if len(sys.argv) == 4:
        if sys.argv[1] == "rm":
                if sys.argv[2] == "-r": 
                        bucket = connection.get_bucket(sys.argv[3])
                        items = bucket.get_all_keys()
                        for key in items:
                                bucket.delete_key(key)
                                print "Deleting key: "+str(key)
                else:
                        bucket = connection.get_bucket(sys.argv[2])
                        bucket.delete_key(sys.argv[3])
                        print "Deleting key: "+str(sys.argv[3]
)gm

if len(sys.argv) == 5:
        if sys.argv[1] == "cp":
                if sys.argv[2] == "-r": 
                        bucket = connection.get_bucket(sys.argv[3])
                        for f in os.listdir(sys.argv[4]):
                                source=os.path.join(sys.argv[4], f)
                                dest = source.replace('/', '-')
                                key = bucket.new_key(dest)
                                key.set_contents_from_filename(source)
                                print "copying file: "+str(source)
                                key.set_acl('public-read')
                                bucket.set_acl('public-read', dest)

                else:   
                        print "copy file: " +sys.argv[3]
                        bucket = connection.get_bucket(sys.argv[2])
                        key = bucket.new_key(sys.argv[4])
                        key.set_contents_from_filename(sys.argv[3])
                        key.set_acl('public-read')

