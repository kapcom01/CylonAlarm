var net = require('net')
var http = require('http');
var fs = require('fs');
var path = require('path')

function socket_proxy(data_to_forward,response){
  var socket = net.createConnection(5000);

  socket.on('connect', function() {
    console.log('Socket Connected.');
  });
  socket.on('end', function() {
    console.log('Socket Disconnected.');
  });
  socket.on('data', function(data) {
    console.log('RESPONSE: ' + data);
    response.writeHead(200, {"Content-Type": "text/plain; charset=utf-8"});
    response.write(data);
    response.end();
    socket.end();
  });

  socket.write(JSON.stringify(data_to_forward));
}

var server = http.createServer(function (request, response) {

  // I should get some sleep and rethink everything here!!

	p = path.resolve(request.url,"..");

	if(request.url.indexOf('jquery-1.10.2.js') != -1){ //req.url has the pathname, check if it conatins '.js'
    fs.readFile(__dirname + '/webui/js/jquery-1.10.2.js', function (err, data) {
      if (err) console.log(err);
      response.writeHead(200, {'Content-Type': 'text/javascript'});
      response.write(data);
      response.end();
    });

  }

  else if(request.url.indexOf('bootstrap.min.css') != -1){ //req.url has the pathname, check if it conatins '.css'
    fs.readFile(__dirname + '/webui/css/bootstrap.min.css', function (err, data) {
      if (err) console.log(err);
      response.writeHead(200, {'Content-Type': 'text/css'});
      response.write(data);
      response.end();
    });

  }

  else if(path.basename(p)=="actdeact"){
    var domain = path.basename(request.url);
    console.log("> actdeact "+domain);
    var d = {
      "actdeact" : {
        "domain_id" : domain
      }
    };
    socket_proxy(d,response);
  }

  else if(path.basename(request.url)=="status"){
    console.log("> status");
    var d = {
      "status" : {
        "check_all" : true
      }
    };
    socket_proxy(d,response);
  }


  else{
      fs.readFile('./webui/index.html', function(err, file) {  
          if(err) {  
              // write an error response or nothing here  
              return;  
          }  
          response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });  
          response.end(file, "utf-8");  
      });
  }
});

server.listen(80);
console.log("Server running..");