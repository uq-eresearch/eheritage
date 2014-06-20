var args = process.argv.slice(2);
if(args.length == 0) {
  console.log('usage: ' + process.argv[0] + ' ' + process.argv[1] +
    ' <sa heritage shapefile (points) e.g. dd_heritp_shp.sh>' +
    ' [elasticsearch host defaults to http://localhost:9200]');
  process.exit(1);
}
var importCounter = 0;
var shapefile = require('shapefile');
var elasticsearch = require('elasticsearch');
var shpfile = args[0];
var host = args[1]?args[1]:'http://localhost:9200';
console.log('importing sa heritage data from file '+shpfile+' to elasticsearch host '+host);
var client = new elasticsearch.Client({
  host: host
});
var reader = shapefile.reader(shpfile);
reader.readHeader(function(error, header) {
  if(error) {
    console.error(error);
    process.exit(2);
  } else {
    reader.readRecord(nextRecord);
  }
});
function nextRecord(error, record) {
  if(error) {
    console.log(error);
    process.exit(2);
  } else if(record == shapefile.end) {
    reader.close(function() {
      console.log();
      console.log('imported '+importCounter+' documents into elasticsearch host '+host);
      process.exit()
    });
  } else {
    var hp = ehrtge(record);
    if(hp != null) {
      //console.log(JSON.stringify(hp, null, 2));
      index(hp, function callback() {
        importCounter++;
        if(importCounter%100 == 0) {
          process.stdout.write('.');
        }
        reader.readRecord(nextRecord);
      });
    } else {
      console.error('failed to create a record for heritage nr '+record.properties.HERITAGENR);
      process.exit(2);
    }
  }
}
function ehrtge(record) {
  var name = record.properties.DETAILS;
  if(!name) {
    name = record.properties.AS2482DESC;
  }
  if(!name) {
    name = record.properties.PARLOCATIO;
  }
  if(!name) {
    return null;
  }
  var result = {};
  result.addresses = [];
  result.addresses.push({
    country: 'AUSTRALIA',
    lga_name: record.properties.LGADESC,
    state: 'SA',
    street_name: record.properties.STREETNAME,
    street_type : record.properties.STREETTYPE,
    street_number: record.properties.STREETNR,
    suburb: record.properties.SUBURB,
    address: record.properties.PARLOCATIO
  });
  result.geolocation = {
    lat: record.geometry.coordinates[1],
    lon: record.geometry.coordinates[0]
  }
  result.heritagenr = record.properties.HERITAGENR;
  result.id = record.properties.OBJECTID;
  result.name = name;
  result.state = 'SA';
  result.description = record.properties.EXTENTOFLI;
  result.significance = record.properties.SIGNIFICAN;
  result.categories = categories(record.properties.AS2482DESC);
  result.url = 'http://apps.planning.sa.gov.au/HeritageSearch/HeritageItem.aspx?p_heritageno=' +
    record.properties.HERITAGENR;
  return result;
}
function categories(str) {
  if(!str) {
    return null;
  }
  var result = [];
  str.split(';').forEach(function(v1) {
    v1.trim().split('-').forEach(function(v2) {
      var s = v2.trim();
      if(s) {
        result.push({name: s});
      }
    });
  });
  return result;
}
function index(record, callback) {
  client.index({
    index: 'eheritage_v2',
    type: 'heritage_place',
    id: record.state+'-'+record.id,
    body: record
  }, function (err, resp) {
    if(err) {
      console.error(err);
      console.error(resp);
      process.exit(2);
    }
    callback();
  });
}
