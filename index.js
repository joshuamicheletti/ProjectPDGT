// library for HTTP requests
const express = require("express");
// express object
const app = express();
// library for sha256 hash encoding
const sha256 = require("js-sha256");
// library for managing and parsing cookies
const cookieparser = require("cookie-parser");
// library for receiving files through HTTP requests
const multer  = require('multer');

// API for communicating with the Blob server Minio
const minio = require('minio');

// object for uploading files
const upload = multer({storage: multer.memoryStorage()});

// Minio blob storage server's client
const minioClient = new minio.Client({
  endPoint: 'mathorgadaorc.ddns.net', // IP
  port: 9000,                         // port
  accessKey: "minio",                 // username
  secretKey: "password",              // password
  signatureVersion: 'v4',             // verification version
  useSSL: false                       // HTTP transfer only
});

// middleware for handling json and cookies
app.use(express.json());
app.use(cookieparser());

// counter for salt, ensures that passwords aren't the same thanks to the salt
var saltCounter = 0;

// function to obtain an object (JSON) from a map object
function mapToObject(map) {
  // create an empty object
  const out = Object.create(null)
  // cycles through the map entries
  map.forEach((value, key) => {
    // if the entry in the map is a map itself
    if (value instanceof Map) {
      // recursively resolve the inner map
      out[key] = mapToObject(value)
    } else {
      // store the value in the object indexed as the key
      out[key] = value
    }
  })
  // return the object constructed from the map
  return out
}

// function to obtain a string from a stream
async function streamToString(stream) {
  // create an empty list to store the stream chunks
  const chunks = [];
  // the function returns a promise that finishes when the stream ends
  return new Promise((resolve, reject) => {
    // when there's a 'data' event on the stream, store the received chunk in the list
    stream.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
    // when there's an 'error' event on the stream, reject the promise
    stream.on('error', (err) => reject(err));
    // when there's an 'end' event on the stream, return the concatenation of all the chunks into string
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
  })
}

// function to decode base64 headers for basic authorization
function decodeBase64(authHeader) {
  // get the encoded data: Basic: *****************
  const auth = authHeader.substr(6);
  // decode the credentials (username:password)
  const decoded = new Buffer(auth, 'base64').toString();
  // return the split credentials
  return (decoded.split(':'));
}

// function to append salt and string and encode it in sha256
function encodeSaltPasswordSha256(salt, password) {
  // build a compound string by adding salt and password
  const compound = salt + password;
  // create the sha256 object
  const h = sha256.create();
  // add the compound to the object as an input string
  h.update(compound);
  // return the encoded string
  return(h.hex());
}

// map for storing login info (username, password (salt + hash))
const logins = new Map();

// fetch the login info stored in the 'users.json' file in the bucket 'info' in the Minio server
minioClient.getObject('info', "users.json", async function(err, dataStream) {
  // if an error occurs, return the function and display the error
  if (err) {
    return console.log(err);
  }
  // store the string coming from the stream
  usersString = await streamToString(dataStream);
  // parse the string into a javascript object
  usersObject = JSON.parse(usersString);
  // store the values from the object into the 'logins' map
  for (var key in usersObject) {
    logins.set(key, usersObject[key]);
  }
});


// map for storing servers info (server name, server password (salt + hash), server owner)
const servers = new Map();

// fetch the login info stored in the 'servers.json' file in the bucket 'info' in the Minio server
minioClient.getObject('info', "servers.json", async function(err, dataStream) {
  // if an error occurs, return the function and display the error
  if (err) {
    return console.log(err);
  }
  // store the string coming from the stream
  serversString = await streamToString(dataStream);
  // parse the string into a javascript object
  serversObject = JSON.parse(serversString);
  // store the values from the object into the 'servers' map
  for (var key in serversObject) {
    servers.set(key, serversObject[key]);
  }
});


// map for storing cookies
const cookies = new Map();

// function to verify the identity of the user and check if his login credentials match the ones stored
function attemptLogin(username, password) {
  // if the username is not in the logins list, discard the login attempt
  if (!logins.has(username)) {
    return false;
  }

  // get the object with the user's info (username, password (salt + hash))
  const user = logins.get(username);
  // encode the salt and password into sha256
  var hash = encodeSaltPasswordSha256(user.salt, password);
  // check if the new generated string is the same as the one saved (meaning that passwords match and the user is logged in)
  return (hash == user.hash);
}

// function to verify if the user is authenticated to access the server
function attemptAuth(req) {
  console.log("Authentication header: " + req.headers.authorization);
  
  console.log("Cookies: " + JSON.stringify(req.cookies));
  
  // if the user has a cookie
  if (req.cookies.auth) {
    // check if the cookie is stored in the cookie list
    if (cookies.has(req.cookies.auth)){
      const username = cookies.get(req.cookies.auth);
      console.log("L'utente: " + username + " si è collegato tramite cookie");

      // the user is authenticated
      return [username, 0];
    }
  }
  
  // if the user doesn't have a cookie or an authorization header
  if (!req.headers.authorization) {
    // the user isn't authenticated
    return false;
  }
  
  // if the user doesn't have a cookie but has an authorization header that uses a format different than 'Basic'
  if (!req.headers.authorization.startsWith('Basic ')) {
    // the user isn't authenticated
    return false;
  }
  
  // decode the authorization header in base64
  const [username, password] = decodeBase64(req.headers.authorization);
  
  console.log("Login: " + username + ", password: " + password);
  
  // attempt a login with the authorization header credentials
  if (attemptLogin(username, password)) {
    return [username, password];
  } else {
    return false;
  }
}


// HTTP REQUESTS MANAGEMENT

// get /check to check the logins and servers maps
app.get('/check', (req, resp) => {
  console.log(servers);
  console.log(logins);
  resp.status(200).end();
});

// get /hash to test the sha256 algorithm
app.get('/hash', (req, resp) => {
  const input = req.query.input;
  
  const h = sha256.create();
  h.update(input);
  resp.type('text/plain').status(200).send(h.hex()).end();
});

// get /login to test the authorization features
app.get('/login', (req, resp) => {
  // check if the user is authorized
  const loginResult = attemptAuth(req);

  // if the user is not authorized
  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong Login Credentials").end();
    return false;
  }

  // save the username of the request
  const username = loginResult[0];

  // respond with 200 OK and the information of the user that is connected
  resp.status(200).send(username).end();
});

// post /loginCookie to login into the server and get a cookie
app.post('/loginCookie', (req, resp) => {
  // check if the user is authorized
  const loginResult = attemptAuth(req);
  // if the user is not authorized
  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong Login Credentials").end();
    return false;
  }

  // save the username of the request
  const username = loginResult[0];

  // random number to generate a cookie
  const now = new Date().toString();
  // convert the random number into a sha256 encoded string
  const h = sha256.create();
  h.update(now);
  const sessionId = h.hex();
  // store the newly created cookie in the 'cookies' map
  cookies.set(sessionId, username);
  // send the cookie to the user connecting
  resp.cookie('auth', sessionId);
  // respond with 201 CREATED (as it created the new cookie) and the information of the user 
  resp.status(201).send(username).end();
});

// post /users to create a new account and save it in 'logins'
app.post('/users', (req, resp) => {
  // check if the request has an authorization header to get the user credentials from
  if (!req.headers.authorization) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid Registration").end();
    return false;
  }

  // decode the user credentials from the base64 encoding
  const [user, password] = decodeBase64(req.headers.authorization);

  console.log("Register: " + user + ", password: " + password);

  // check if the username is a valid string
  if (user.length == 0) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid User").end();
    return false;
  }

  // check if the password is a valid string
  if (password.length == 0) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid Password").end();
    return false;
  }

  // check if the user already exists in the 'logins' map
  if (logins.has(user)) {
    console.log("User " + user + " already exists");
    // respond with 409 CONFLICT
    resp.status(409).send("User already registered").end();
    return false;
  }

  // encode the password by adding a salt and encoding it through sha256
  var hash = encodeSaltPasswordSha256(saltCounter.toString(), password);

  // store the new user in a temporary logins map
  var tmpLogins = new Map(logins);
  tmpLogins.set(user, {salt: saltCounter.toString(), hash: hash});

  // store the temporary login info in the "users.json" file in the Minio blob server (after converting it into a string)
  minioClient.putObject("info", "users.json", JSON.stringify(mapToObject(tmpLogins)), function(error, etag) {
    // check if an error occurs while storing the file in the Minio server
    if (error) {
      // respond with 503 SERVICE UNAVAILABLE
      resp.status(503).send("Minio Error").end();
      return console.log(error);
    }
    // if everything went well, we can update the logins map with the new entry
    else {
      logins.set(user, {salt: saltCounter.toString(), hash: hash});
      // increase the salt counter
      saltCounter++;
      // respond with 201 CREATED
      resp.status(201).send(user).end();
    }
  });
});

// delete /users to delete an account from the 'logins' map
app.delete('/users', (req, resp) => {
  // check if the request has an authorization header
  if (!req.headers.authorization) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Not Authorized").end();
    return false;
  }

  // decode the authorization header from base64 to read the credentials
  const [user, password] = decodeBase64(req.headers.authorization);

  // check if the username is a valid string
  if (user.length == 0) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid User").end();
    return false;
  }

  // check if the password is a valid string
  if (password.length == 0) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid Password").end();
    return false;
  }

  // check if the user is a registered user in the list of accounts
  if (!logins.has(user)) {
    // respond with 404 FILE NOT FOUND
    resp.status(404).send("User Not Found").end();
    return false;
  }

  // encode the password in the request to sha256
  var hash = encodeSaltPasswordSha256(logins.get(user).salt, password);

  // check if the password matches the one saved in the account
  if (hash != logins.get(user).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong password").end();
    return false;
  }

  // remove the account from the temporary logins map
  var tmpLogins = new Map(logins);
  tmpLogins.delete(user);

  // save the updated accounts list to the "users.json" file in the Minio Server (after converting it into a string)
  minioClient.putObject("info", "users.json", JSON.stringify(mapToObject(tmpLogins)), function(error, etag) {
    // check if an error occurs while storing the file in the Minio server
    if (error) {
      // respond with 409 SERVICE UNAVAILABLE
      resp.status(409).send("Minio Error").end();
      return console.log(error);
    }
    // if everything went well and the user has been deleted from the "users.json" file
    else {
      // remove the user from the logins map
      logins.delete(user);
      // respond with 200 OK and the information of the deleted user
      resp.status(200).send("Deleted user: " + user).end();
    }
  });
});



// post /upload to upload a single file to a server
app.post('/upload', upload.single('avatar'), (req, resp) => {
  // check if the request has info about the target server
  if (!req.query.serverName || !req.query.serverPassword) {
    // respond with 400 BAD REQUEST
    resp.status(400).send('Invalid Server Name or Password').end();
    return false;
  }

  // check if the targeted server exists
  if (!servers.has(req.query.serverName)) {
    // respond with 404 FILE NOT FOUND
    resp.status(404).send("No server with that name").end();
    return false;
  }

  // encode the received password with the known salt of the server
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the password matches with the server
  if (hash != servers.get(req.query.serverName).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Access Denied, wrong server password").end();
    return false;
  }

  // check if the user is authorized
  const loginResult = attemptAuth(req);

  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong login info").end();
    return false;
  }
  
  // obtain the username from the request
  var username = loginResult[0];

  // check if the upload user is the server owner (aka allowed to upload)
  if (servers.get(req.query.serverName).owner != username) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Not allowed to upload files").end();
    return false;
  }

  // output for storing the list of files
  const output = [];

  // get the list of files in the server
  var stream = minioClient.listObjects(req.query.serverName);
  console.log("got the stream");

  // store the file names in 'output'
  stream.on('data', function(obj) {
    console.log("pushed obj to output");
    output.push(obj.name);
  });

  // catch any error
  stream.on('error', function(err) {
    console.log(err);
    // respond with 503 SERVICE UNAVAILABLE
    resp.status(503).send("Minio Timeout Error").end();
  });

  // once we have all the data from the stream
  stream.on('end', function() {
    // check if the file we're trying to upload already exists
    for (var i = 0; i < output.length; i++) {
      if (req.file.originalname == output[i]) {
        // respond with 409 CONFLICT
        resp.status(409).send("File already exists").end();
        return false;
      }
    }

    console.log("putting object in bucket");
    // put the uploaded file in the bucket of the server
    minioClient.putObject(req.query.serverName, req.file.originalname, req.file.buffer, function(error, etag) {
      console.log("finished putting object");
      // check for Minio errors
      if (error) {
        // respond with 503 SERVICE UNAVAILABLE
        resp.status(503).send("Minio Error").end();
        return console.log(error);
      } else {
        // respond with 201 CREATED
        resp.status(201).send("File succesfully uploaded").end();
      }
    });
  });
});

// get /upload to get a list of the files in a server
app.get('/upload', (req, resp) => {
  // check if the request has info about the target server
  if (!req.query.serverName || !req.query.serverPassword) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("No server info").end();
    return false;
  }

   // check if the targeted server exists
   if (!servers.has(req.query.serverName)) {
    // respond with 404 FILE NOT FOUND
    resp.status(404).send("No server with that name").end();
    return false;
  }

  // encode the received password with the known salt of the server
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the password matches with the server
  if (hash != servers.get(req.query.serverName).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong server password").end();
    return false;
  }

  // variable for storing the list of files
  const output = [];
  
  // get the list of files from the bucket into a stream
  var stream = minioClient.listObjects(req.query.serverName);

  // read all the objects in the bucket and store them in 'output'
  stream.on('data', function(obj) {
    console.log(obj);
    if (obj.name != "1.txt" && obj.name != "2.txt") {
      output.push(obj.name);
    }
  });
  // catch any error
  stream.on('error', function(err) {
    console.log(err);
    // respond with 503 SERVICE UNAVAILABLE
    resp.status(503).send("Minio Timeout Error").end();
  });
  // once we have all the objects
  stream.on('end', function() {
    // send the list to the client
    resp.json(output);
  });
});

// delete /upload to delete a file in a server
app.delete('/upload', (req, resp) => {
  // check if the user is a valid logged in user
  const loginResult = attemptAuth(req);

  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong login info").end();
    return false;
  }

  // obtain the username from the request
  var username = loginResult[0];

  // check if the request has info about the target server
  if (!req.query.serverName || !req.query.serverPassword) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("No server info").end();
    return false;
  }

  // check if the targeted server exists
  if (!servers.has(req.query.serverName)) {
    // respond with 404 FILE NOT FOUND
    resp.status(404).send("No server with that name").end();
    return false;
  }

  // encode the received password with the known salt of the server
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the password matches with the server
  if (hash != servers.get(req.query.serverName).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong server password").end();
    return false;
  }

  // check if the upload user is the server owner (aka allowed to upload)
  if (servers.get(req.query.serverName).owner != username) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Not allowed to upload files").end();
    return false;
  }

  // check if the request contains a file name
  if (!req.query.fileName) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("No file info").end();
    return false;
  }

  // check if the file exists in the server
  var found = false;
  
  // get the list of files from the bucket into a stream
  var stream = minioClient.listObjects(req.query.serverName);

  // read all the objects in the bucket and check when it finds the selected file
  stream.on('data', function(obj) {
    if (obj.name == req.query.fileName) {
      found = true;
    }
  });
  // catch any error
  stream.on('error', function(err) {
    console.log(err);
    found = false;
  });
  // once the stream is over
  stream.on('end', function() {
    // if the selected file was found
    if (found) {
      // remove the file from the minio bucket
      minioClient.removeObject(req.query.serverName, req.query.fileName, function(err) {
        // catch any error
        if (err) {
          // respond with 503 SERVICE UNAVAILABLE
          resp.status(503).send("Minio error").end();
          return console.log(err);
        } else {
          // respond with 200 OK
          resp.status(200).send("File removed correctly").end();
          return true;
        }
      });
    } else {
      // respond with 404 FILE NOT FOUND
      resp.status(404).send("No file with that name found").end();
      return false;
    }
  });
});

// get /download to download the specified file
app.get('/download', (req, resp) => {
  // check if the user is authorized
  const loginResult = attemptAuth(req);

  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong login info").end();
    return false;
  }

  // check if the request contains any file name
  if (!req.query.fileName) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid file").end();
    return false;
  }

  if (!req.query.serverName || !req.query.serverPassword) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("No server info").end();
    return false;
  }

  // encode the received password with the known salt of the server
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the password matches with the server
  if (hash != servers.get(req.query.serverName).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong server password").end();
    return false;
  }

  // store the name of the file to download from the request
  const fileName = req.query.fileName;

  // get the list of files
  var bucketStream = minioClient.listObjects(req.query.serverName);

  // variable for storing the file names
  const files = [];

  // store the file names into 'files'
  bucketStream.on("data", function(obj) {
    files.push(obj.name);
  });

  // catch any error
  bucketStream.on("error", function(error) {
    // respond with 503 SERVICE UNAVAILABLE
    resp.status(503).send("Minio Error").end();
    return console.log(error);
  });

  // when the stream ends and we have all the files list
  bucketStream.on("end", function() {
    // check if the file we want to download exists in the file list
    var found = false;

    for (var i = 0; i < files.length; i++) {
      if (fileName == files[i]) {
        found = true;
      }
    }

    // if the file doesn't exist in the minio bucket
    if (!found) {
      // respond with 404 FILE NOT FOUND
      resp.status(404).send("file not found").end();
      return false;
    }

    // get the selected file from the Minio server
    minioClient.getObject(req.query.serverName, fileName, function(err, dataStream) {
      // catch any Minio error
      if (err) {
        // respond with 503 SERVICE UNAVAILABLE
        resp.status(503).send("Minio Error").end();
        return console.log(err);
      }
  
      // catch any stream error
      dataStream.on('error', function(err) {
        // respond with 503 SERVICE UNAVAILABLE
        resp.status(503).send("Minio Error").end();
        console.log(err);
        return false;
      });
  
      // set the response header to contain a file
      resp.setHeader('Content-disposition', 'attachment; filename=' + fileName);
      // pipe the stream from the minio server to the response object
      dataStream.pipe(resp);
    });
  });
});



// get /servers to get a list of servers or login into one
app.get('/servers', (req, resp) => {
  // if the request doesn't specify a server
  if (!req.query.serverName) {
    // send the list of all the available servers
    resp.status(200).send(Array.from(servers.keys())).end();
    console.log(servers);
    return true;
  }

  // check if the user is authorized
  const loginResult = attemptAuth(req);

  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong login info").end();
    return false;
  }

  // check that the server requested exists
  if (!servers.has(req.query.serverName)) {
    // respond with 404 FILE NOT FOUND
    resp.status(404).send("No server with that name").end();
    return false;
  }

  // encode through sha256 the salt + password compound
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the server password is correct
  if (hash != servers.get(req.query.serverName).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Incorrect Password").end();
    return false;
  }

  // return the name of the server that the user logged in to and the respective owner
  // with code 200 OK
  resp.status(200).send(req.query.serverName + "," + servers.get(req.query.serverName).owner).end();
});

// post /servers to create a new server
app.post('/servers', (req, resp) => {
  // check if the user is authorized
  const loginResult = attemptAuth(req);

  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Invalid User Login").end();
    return false;
  }

  // get the username (either from the cookie or the basic authorization)
  var username = loginResult[0];

  // check if the request contains a server name and password
  if (!req.query.serverName || !req.query.serverPassword) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Invalid Server Info").end();
    return false;
  }

  // check that the server isn't called 'info', info is a special bucket reserverd for storing servers and user data
  if (req.query.serverName == "info") {
    // respond with 409 CONFLICT
    resp.status(409).send("Server can't be called 'info'").end();
    return false;
  }

  // check that the new server doesn't have the same name as a previous one
  if (servers.has(req.query.serverName)) {
    // respond with 409 CONFLICT
    resp.status(409).send("Server with that name already exists").end();
    return false;
  }

  // store the server info in variables
  var serverName = req.query.serverName;
  var serverPassword = req.query.serverPassword;

  // encode the new password in sha256 with the salt
  var hash = encodeSaltPasswordSha256(saltCounter.toString(), serverPassword);

  // store the new server in the temporary servers map
  var tmpServers = new Map(servers);
  tmpServers.set(serverName, {salt: saltCounter.toString(), hash: hash, owner: username});

  // store the new server list into the "servers.json" file in the Minio server
  minioClient.putObject("info", "servers.json", JSON.stringify(mapToObject(tmpServers)), function(error, etag) {
    console.log("finished putting object");
    // check for Minio errors
    if (error) {
      // respond with 503 SERVICE UNAVAILABLE
      resp.status(503).send("Minio Error").end();
      return console.log(error);
    } else {
      // create a new minio bucket to store the files of the new server
      minioClient.makeBucket(serverName, function(error) {
        // check for Minio errors
        if (error) {
          // respond with 503 SERVICE UNAVAILABLE
          resp.status(503).send("Minio Bucket Error").end();
          return console.log(error);
        } else {
          // put 2 placeholder objects inside of the bucket (these objects will be invisible to the client,
          // they're there to prevent a bug on the Minio API which occurs while having a bucket with 1 item)
          minioClient.putObject(serverName, "1.txt", "do not read", function(error, etag) {
            // check for Minio errors
            if (error) {
              // respond with 503 SERVICE UNAVAILABLE
              resp.status(503).send("Minio Error").end();
              return console.log(error);
            } else {
              // put the second placeholder object
              minioClient.putObject(serverName, "2.txt", "do not read", function(error, etag) {
                if (error) {
                  // respond with 503 SERVICE UNAVAILABLE
                  resp.status(503).send("Minio Error").end();
                  return console.log(error);
                }
                // if everything went well
                else {
                  // we can update the servers map with the new server
                  servers.set(serverName, {salt: saltCounter.toString(), hash: hash, owner: username});
                  // increase the salt counter
                  saltCounter++;
                  // respond with 201 CREATED and the server name of the new server
                  resp.status(201).send(serverName).end();
                }
              });
            }
          });
        }
      });
    }
  });
});

// delete /servers to delete an existing server
app.delete('/servers', (req, resp) => {
  // check if the user credentials are correct and authorized
  const loginResult = attemptAuth(req);

  if (loginResult == false) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong login info").end();
    return false;
  }

  // obtain the username from the request headers
  var username = loginResult[0];

  // check if the request has server info
  if (!req.query.serverName || !req.query.serverPassword) {
    // respond with 400 BAD REQUEST
    resp.status(400).send("Wrong server info").end();
    return false;
  }

  // check if the server mentioned in the request exists
  if (!servers.has(req.query.serverName)) {
    // respond with 404 FILE NOT FOUND
    resp.status(404).send("No server with that name").end();
    return false;
  }

  // check if the password in the request matches with the password of the server
  hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  if (hash != servers.get(req.query.serverName).hash) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Wrong server password").end();
    return false;
  }

  // check if the user in the request is the server owner
  if (username != servers.get(req.query.serverName).owner) {
    // respond with 403 FORBIDDEN
    resp.status(403).send("Not allowed to delete server").end();
    return false;
  }

  // list all the objects in the bucket corresponding to the server
  var objectsList = [];

  var objectsStream = minioClient.listObjects(req.query.serverName);

  // store the objects in the list
  objectsStream.on('data', function(obj) {
    objectsList.push(obj.name);
  });
  // check for errors
  objectsStream.on('error', function(e) {
    console.log(e);
    // respond with 503 SERVICE UNAVAILABLE
    resp.status(503).send("Minio error").end();
    return false;
  });
  // once the list is complete
  objectsStream.on('end', function() {
    // remove the objects listed in the 'objectsList' from the bucket of the server that is being deleted
    minioClient.removeObjects(req.query.serverName, objectsList, function(e) {
      // check for errors
      if (e) {
        // respond with 503 SERVICE UNAVAILABLE
        resp.status(503).send("Minio error").end();
        return console.log("Unable to remove objects ", e);
      } else {
        // remove the bucket of the server that is being deleted
        minioClient.removeBucket(req.query.serverName, function(e) {
          if (e) {
            // respond with 503 SERVICE UNAVAILABLE
            resp.status(503).send("Minio error").end();
            return console.log("Unable to remove bucket");
          } else {
            // delete the server info from the temporary servers map
            var tmpServers = new Map(servers);
            tmpServers.delete(req.query.serverName); 
            // save the new updated info in the 'servers.json' file in the 'info' bucket
            minioClient.putObject("info", "servers.json", JSON.stringify(mapToObject(tmpServers)), function(error, etag) {
              // check for errors
              if (error) {
                // respond with 503 SERVICE UNAVAILABLE
                resp.status(503).send("Minio Error").end();
                return console.log(error);
              }
              // if everything went well
              else {
                // update the servers map
                servers.delete(req.query.serverName);
                // respond with 200 OK and the information about the deleted server 
                resp.status(200).send("Server " + req.query.serverName + " removed").end();
              }
            });
          }
        });
      }
    });
  });
});



// listen for requests :)
const listener = app.listen(process.env.PORT, () => {
 console.log("Your app is listening on port " + listener.address().port);
});

// const listener = app.listen(2000, () => {
//   console.log("Your app is listening on port " + listener.address().port);
// });