var net = require('net');

var PORT = 8000;

var client = new net.Socket();

client.connect(PORT, '127.0.0.1', function() {
    var obj = {target: "LightSensor", service: "status"};
    var json = JSON.stringify(obj);
    console.log('Connected');
    client.write(json);
});

client.on('data', function(data) {
    console.log("Receive:" + data);
    client.destroy();
});

client.on('close', function() {
    console.log('Connection close');
});