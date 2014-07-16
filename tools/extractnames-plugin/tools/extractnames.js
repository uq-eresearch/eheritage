var args = process.argv.slice(2);
var elasticsearch = require('elasticsearch');
var async = require('async');
var request = require('superagent');
var host = args[0]?args[0]:'http://eheritage.metadata.net:9200';
console.log('extracting qld heritage place name of persons, from '+host);
var client = new elasticsearch.Client({
  host: host
});

function search(from, size) {
  client.search({
    index: 'eheritage',
    from : from,
    size: size,
    body: {
      query: {
        match: {
          state: 'QLD'
        }
      },
      fields: []
    }
  }).then(function (resp) {
    if(resp.hits.hits.length == 0) {
      process.exit();
    }
    async.map(resp.hits.hits, function(item, callback) {
      callback(null, function(cb) {
        var url = host+'/'+item._index+'/'+item._type+'/'+item._id+'/_extractnames';
        console.log(url);
        request.post(url).end(function(response) {
          console.log(response.text);
          cb(null);
        });
      });
    }, function(error, result) {
      async.series(result, function() {
        search(from+size, size);
      });
    });
  });
}
search(0,10);

