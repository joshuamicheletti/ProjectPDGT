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
// const path = require('path');
// const fs = require('fs');
// const { resolvePtr } = require("dns");

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

// minioClient.setRequestOptions({timeout: 3000});

// middleware for handling json and cookies
app.use(express.json());
app.use(cookieparser());

// counter for salt, ensures that passwords aren't the same thanks to the salt
var saltCounter = 0;

// old code
{
// const data = new Map();
// data.set(1, {name: "Mario", surname: "Rossi"});
// data.set(2, {name: "Luigi", surname: "Verdi"});

// var dataID = 2;



// app.get('/people', (req, resp) => {
//   if (!req.accepts('application/json')) {
//     resp.sendStatus(406);
//     return;
//   }
  
//   const output = Array.from(data, ([key, value]) => {
//     return {
//       id: key,
//       name: value.name,
//       surname: value.surname
//     };
//   });
//   resp.json(output);
// });

// app.get('/people/:id', (req, resp) => {
//   const id = Number.parseInt(req.params.id);
  
//   if (Number.isNaN(id)) {
//     resp.sendStatus(400);
//     return;
//   }
//   if (!data.has(id)) {
//     resp.sendStatus(404);
//     return;
//   }
  
//   const person = data.get(id);
  
//   resp.format({
//     'text/plain': () => {
//       resp.send(person.name + ' ' + person.surname);
//     },
//     'text/html': () => {
//       resp.send('<html><body><p>Il signor <b>' + person.name + ' ' + person.surname + '</b></p></body></html>');
//     },
//     'application/json': () => {
//       //resp.send(JSON.stringify(person));
//       resp.json(person);
//     },
//     defaul: () => {
//       resp.sendStatus(406);
//     }
//   });
// });

// app.post('/people', (req, resp) => {
//   const input = req.body;
  
//   if (!input.name) {
//     resp.sendStatus(422);
//     return;
//   }
//   if (!input.surname) {
//     resp.sendStatus(422);
//     return;
//   }
  
//   const name = new String(input.name);
//   const surname = new String(input.surname);
  
//   dataID++;
//   const newId = dataID;
//   data.set(newId, {name: name, surname: surname});
  
//   resp.status(201).type('application/json').send(JSON.stringify({id: newId, name: name, surname: surname}));
// });

// app.delete('/people/:id', (req, resp) => {
//   const id = Number.parseInt(req.params.id);
  
//   if (Number.isNaN(id)) {
//     resp.sendStatus(400);
//     return;
//   }
//   if (!data.has(id)) {
//     resp.sendStatus(404);
//     return;
//   }
  
//   data.delete(id);
  
//   resp.sendStatus(200);
// });
}

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
  return(hash == user.hash);
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
      return true;
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
  const [login, password] = decodeBase64(req.headers.authorization);
  
  console.log("Login: " + login + ", password: " + password);
  
  // attempt a login with the authorization header credentials
  return attemptLogin(login, password);
}

// HTTP REQUESTS MANAGEMENT

// get /check to check the logins and servers maps
app.get('/check', (req, res) => {
  console.log(servers);
  console.log(logins);
  res.status(200).end();
});

// get /secret to test the authorization features
app.get('/secret', (req, resp) => {
  if (attemptAuth(req)) {
    if (req.headers.authorization) {
      const [login, password] = decodeBase64(req.headers.authorization);
      resp.status(200).send(login).end();
    } else {
      resp.status(200).send(cookies.get(req.cookies.auth)).end();
    }
    
  } else {
    resp.set('WWW-Authenticate', 'Basic realm="Cose segrete"').status(401).send("Wrong Username or Password").end();
  }
});

// get /hash to test the sha256 algorithm
app.get('/hash', (req, resp) => {
  const input = req.query.input;
  
  const h = sha256.create();
  h.update(input);
  resp.type('text/plain').status(200).send(h.hex()).end();
});

// post /login to login into the server and get a cookie
app.post('/login', (req, resp) => {
  // store the credentials passed through query
  const username = req.query.username;
  const password = req.query.password;
  // check if the username and password correspond to any user stored in 'logins'
  if (!attemptLogin(username, password)) {
    resp.status(403).send("Wrong Username or Password").end();
    return;
  }
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
  
  resp.status(200).send(username).end();
});

// post /users to create a new account and save it in 'logins'
app.post('/users', (req, resp) => {
  // check if the request has an authorization header to get the user credentials from
  if (!req.headers.authorization) {
    resp.status(400).send("Invalid Registration").end();
    return;
  }

  // decode the user credentials from the base64 encoding
  const [user, password] = decodeBase64(req.headers.authorization);

  console.log("Register: " + user + ", password: " + password);

  // check if the username is a valid string
  if (user.length == 0) {
    resp.status(400).send("Invalid User").end();
    return;
  }
  // check if the password is a valid string
  if (password.length == 0) {
    resp.status(400).send("Invalid Password").end();
    return;
  }
  // check if the user already exists in the 'logins' map
  if (logins.has(user)) {
    console.log("User " + user + " already exists");
    resp.status(400).send("User already registered").end();
    return;
  }

  // encode the password by adding a salt and encoding it through sha256
  var hash = encodeSaltPasswordSha256(saltCounter.toString(), password);
  // store the new user in the 'logins' map
  logins.set(user, {salt: saltCounter.toString(), hash: hash});

  console.log(h.hex(), saltCounter);
  // increase the salt counter
  saltCounter++;

  // store the login info in the "users.json" file in the Minio blob server (after converting it into a string)
  minioClient.putObject("info", "users.json", JSON.stringify(mapToObject(logins)), function(error, etag) {
    // check if an error occurs while storing the file in the Minio server
    if (error) {
      resp.status(400).send("Minio Error").end();
      return console.log(error);
    } else {
      resp.status(200).send(user).end();
    }
  });
});

// delete /users to delete an account from the 'logins' map
app.delete('/users', (req, resp) => {
  // check if the request has an authorization header
  if (!req.headers.authorization) {
    resp.status(400).send("Not Authorized").end();
    return;
  }
  // decode the authorization header from base64 to read the credentials
  const [user, password] = decodeBase64(req.headers.authorization);

  // check if the user is a registered user in the list of accounts
  if (!logins.has(user)) {
    resp.status(404).send("User Not Found").end();
    return;
  }

  // encode the password in the request to sha256
  var hash = encodeSaltPasswordSha256(logins.get(user).salt + password);

  // check if the password matches the one saved in the account
  if (hash != logins.get(user).hash) {
    resp.status(403).send("Wrong password").end();
    return;
  }
  // remove the account from the 'logins' map
  logins.delete(user);

  // save the updated accounts list to the "users.json" file in the Minio Server (after converting it into a string)
  minioClient.putObject("info", "users.json", JSON.stringify(mapToObject(logins)), function(error, etag) {
    // check if an error occurs while storing the file in the Minio server
    if (error) {
      resp.status(400).send("Minio Error").end();
      return console.log(error);
    } else {
      resp.status(200).send("Deleted user: " + user).end();
    }
  });
});

// post /upload to upload a single mod to a server
app.post('/upload', upload.single('avatar'), (req, res) => {
  // check if the request has info about the target server
  if (!req.query.serverName || !req.query.serverPassword) {
    res.status(400).send('Invalid Server Name or Password').end();
    return false;
  }
  // check if the targeted server exists
  if (!servers.has(req.query.serverName)) {
    res.status(400).send("No server with that name").end();
    return false;
  }

  // encode the received password with the known salt of the server
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the password matches with the server
  if (hash != servers.get(req.query.serverName).hash) {
    res.status(400).send("Access Denied, wrong server password").end();
    return false;
  }

  // check if the request has a form of authentication
  if (!req.headers.authorization && !req.cookies.auth) {
    res.status(400).send("Invalid Login Info").end();
    return false;
  }

  // check if the user is authorized
  if (!attemptAuth(req)) {
    res.status(400).send("Wrong login info").end();
    return false;
  }
  
  // obtain the username from the request
  if (req.cookies.auth) {
    // get the username from the cookie map
    var username = cookies.get(req.cookies.auth);
  } else if (req.headers.authorization) {
    // decode the authorization header
    const [login, password] = decodeBase64(req.headers.authorization);
    // get the username from the request
    var username = login;
  }

  // check if the upload user is the server owner (aka allowed to upload)
  if (servers.get(req.query.serverName).owner != username) {
    res.status(403).send("Not allowed to upload mods").end();
    return false;
  }

  // output for storing the list of mods
  const output = [];

  // get the list of mods in the server
  var stream = minioClient.listObjects("mods");
  console.log("got the stream");

  // store the mod names in 'output'
  stream.on('data', function(obj) {
    console.log("pushed obj to output");
    output.push(obj.name);
  });

  // catch any error
  stream.on('error', function(err) {
    console.log(err);
    res.status(400).send("Minio Timeout Error").end();
  });

  // once we have all the data from the stream
  stream.on('end', function() {
    // check if the mod we're trying to upload already exists
    for (var i = 0; i < output.length; i++) {
      if (req.file.originalname == output[i]) {
        res.status(400).send("Mod already exists").end();
        return;
      }
    }

    console.log("putting object in bucket");
    // put the uploaded mod in the bucket of the server
    minioClient.putObject("mods", req.file.originalname, req.file.buffer, function(error, etag) {
      console.log("finished putting object");
      // check for Minio errors
      if (error) {
        res.status(400).send("Minio Error").end();
        return console.log(error);
      } else {
        res.status(200).send("Mod succesfully uploaded").end();
      }
    });
  });
});

// WRONG, REMEMBER TO MAKE IT WORK WITH USER AUTHORIZATION AND WITH SPECIFIC SERVER MODS

// get /upload to get a list of the mods in a server
app.get('/upload', (req, res) => {
  // variable for storing the list of mods
  const output = [];
  
  // get the list of mods from the bucket into a stream
  var stream = minioClient.listObjects("mods");

  // read all the objects in the bucket and store them in 'output'
  stream.on('data', function(obj) {
    console.log(obj);
    output.push(obj.name);
  });
  // catch any error
  stream.on('error', function(err) {
    console.log(err);
    res.status(400).send("Minio Timeout Error").end();
  });
  // once we have all the objects
  stream.on('end', function() {
    // send the list to the client
    res.json(output);
  });
});

// get /download to download the specified mod
app.get('/download', (req, res) => {
  // check if the user is authorized
  if (!attemptAuth(req)) {
    res.status(400).send("Wrong login info").end();
    return;
  }

  // check if the request contains any mod name
  if (!req.query.mod) {
    res.status(400).send("Invalid Mod").end();
    return;
  }

  const fileName = req.query.mod;

  // get the list of mods
  var bucketStream = minioClient.listObjects("mods");

  // variable for storing the mod names
  const mods = [];

  // store the mod names into 'mods'
  bucketStream.on("data", function(obj) {
    mods.push(obj.name);
  });

  // catch any error
  bucketStream.on("error", function(error) {
    console.log(error);
  });

  // when the stream ends and we have all the mods list
  bucketStream.on("end", function() {
    // check if the mod we want to download exists in the mod list
    var found = false;

    for (var i = 0; i < mods.length; i++) {
      if (fileName == mods[i]) {
        found = true;
      }
    }

    if (!found) {
      res.status(400).send("Mod not found").end();
      return;
    }

    // get the selected mod from the Minio server
    minioClient.getObject('mods', fileName, function(err, dataStream) {
      // catch any Minio error
      if (err) {
        res.status(400).send("Minio Error").end();
        return console.log(err);
      }
  
      // catch any stream error
      dataStream.on('error', function(err) {
        console.log(err);
        return;
      });
  
      // set the response header to contain a file
      res.setHeader('Content-disposition', 'attachment; filename=' + fileName);
      // pipe the stream from the minio server to the response object
      dataStream.pipe(res);
    });
  });
});


// WRONG, REMEMBER TO PUT THE AUTHENTICATION CHECK

// get /servers to get a list of servers or login into one
app.get('/servers', (req, resp) => {
  // if the request doesn't specify a server
  if (!req.query.serverName) {
    // send the list of all the available servers
    resp.status(200).send(Array.from(servers.keys())).end();
    console.log(servers);
    return;
  }

  // check that the server requested exists
  if (!servers.has(req.query.serverName)) {
    resp.status(400).send("No server with that name").end();
    return;
  }

  // encode through sha256 the salt + password compound
  var hash = encodeSaltPasswordSha256(servers.get(req.query.serverName).salt, req.query.serverPassword);

  // check if the server password is correct
  if (hash != servers.get(req.query.serverName).hash) {
    resp.status(400).send("Incorrect Password").end();
    return;
  }

  // return the name of the server that the user logged in to and the respective owner
  resp.status(200).send(req.query.serverName + "," + servers.get(req.query.serverName).owner).end();
});

// post /servers to create a new server
app.post('/servers', (req, resp) => {
  // check if the request contains a server name and password
  if (!req.query.serverName || !req.query.serverPassword) {
    resp.status(400).send("Invalid Server Info").end();
    return;
  }

  // store the server info in variables
  var serverName = req.query.serverName;
  var serverPassword = req.query.serverPassword;

  // check if the user is authorized
  if (attemptAuth(req) == false) {
    resp.status(400).send("Invalid User Login").end();
    return;
  }

  // get the username (either from the cookie or the basic authorization)
  var username;

  if (req.cookies.auth) {
    username = cookies.get(req.cookies.auth);
  } else if (req.headers.authorization) {
    const [login, password] = decodeBase64(req.headers.authorization);
    username = login;
  }

  // encode the new password in sha256 with the salt
  var hash = encodeSaltPasswordSha256(saltCounter.toString(), serverPassword);

  // store the new server in the 'servers' map
  servers.set(serverName, {salt: saltCounter.toString(), hash: hash, owner: username});
  // increase the salt counter for the next server
  saltCounter++;

  // store the new server list into the "servers.json" file in the Minio server
  minioClient.putObject("info", "servers.json", JSON.stringify(mapToObject(servers)), function(error, etag) {
    console.log("finished putting object");
    // check for Minio errors
    if (error) {
      resp.status(400).send("Minio Error").end();
      return console.log(error);
    } else {
      resp.status(200).send(serverName).end();
    }
  });
});



// listen for requests :)
const listener = app.listen(process.env.PORT, () => {
  console.log("Your app is listening on port " + listener.address().port);
});

// const listener = app.listen(2000, () => {
//   console.log("Your app is listening on port " + listener.address().port);
// });
