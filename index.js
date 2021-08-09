const express = require("express");
const app = express();
const sha256 = require("js-sha256");
const cookieparser = require("cookie-parser");
const multer  = require('multer');
const path = require('path');
const fs = require('fs');
const { resolvePtr } = require("dns");
const minio = require('minio');
// const multerMinioStorage = require('multer-minio-storage');
// const upload = multer({ dest: 'uploads/' })

var storage = multer.diskStorage(
  {
    destination: function (req, file, cb) {
      // cb(null, "./uploads/" + req.query.serverName + "/");
      console.log("test");
      cb(null, "./uploads/");
    },
    filename: function (req, file, cb) {
      console.log("testone");
      cb(null, file.originalname);
    }
  }
);

// const upload = multer({storage: storage});
// const upload = multer();
const upload = multer({storage: multer.memoryStorage()});


const minioClient = new minio.Client({
  endPoint: '188.152.172.50',
  port: 9000,
  accessKey: "minio",
  secretKey: "password",
  signatureVersion: 'v4',
  useSSL: false
});

console.log(minioClient.ClientOptions);

// const uploadMinio = multer({
//   storage: multerMinioStorage({
//     minioClient: minioClient,
//     bucket: 'mods'
//   })
// });


app.use(express.json());
app.use(cookieparser());

var saltCounter = 0;

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


const logins = new Map();
logins.set('joshua', {salt: '123456', hash: 'aca2d6bd777ac00e4581911a87dcc8a11b5faf11e08f584513e380a01693ef38'}, {admin: true});

const servers = new Map();
const h = sha256.create();
h.update("0" + "password");
servers.set('minecuraftu', {salt: '0', hash: h.hex(), owner: "joshua"});

const cookies = new Map();

function attemptLogin(username, password) {
  if (!logins.has(username)) {
    return(false);
  }
  
  const user = logins.get(username);
  
  const compound = user.salt + password;

  const h = sha256.create();
  h.update(compound);
  
  return(h.hex() == user.hash);
}

function attemptAuth(req) {
  console.log("Authentication header: " + req.headers.authorization);
  
  console.log("Cookies: " + JSON.stringify(req.cookies));
  
  if (req.cookies.auth) {
    if (cookies.has(req.cookies.auth)){
      const username = cookies.get(req.cookies.auth);
      console.log("L'utente: " + username + " si è collegato tramite cookie");
      
      return true;
    }
  }
  
  if (!req.headers.authorization) {
    return false;
  }
  
  if (!req.headers.authorization.startsWith('Basic ')) {
    return false;
  }
  
  // Basic am9zaHVhOnBhc3N3b3Jk
  const auth = req.headers.authorization.substr(6);
  const decoded = new Buffer(auth, 'base64').toString();
  const [login, password] = decoded.split(':');
  
  console.log("Login: " + login + ", password: " + password);
  
  //return(login == 'joshua' && password == 'password');
  return attemptLogin(login, password);
}

app.get('/secret', (req, resp) => {
  if (attemptAuth(req)) {
    if (req.headers.authorization) {
      const auth = req.headers.authorization.substr(6);
      const decoded = new Buffer(auth, 'base64').toString()
      const [login, password] = decoded.split(':');
      resp.status(200).send(login).end();
    } else {
      resp.status(200).send(cookies.get(req.cookies.auth)).end();
    }
    
  } else {
    resp.set('WWW-Authenticate', 'Basic realm="Cose segrete"').status(401).send("Wrong Username or Password").end();
  }
});

app.get('/hash', (req, resp) => {
  const input = req.query.input;
  
  const h = sha256.create();
  h.update(input);
  resp.type('text/plain').status(200).send(h.hex()).end();
});


app.post('/login', (req, resp) => {
  const username = req.query.username;
  const password = req.query.password;
  
  if (!attemptLogin(username, password)) {
    resp.status(403).send("Wrong Username or Password").end();
    return;
  }
  
  const now = new Date().toString();
  
  const h = sha256.create();
  h.update(now);
  const sessionId = h.hex();
  
  cookies.set(sessionId, username);
  
  resp.cookie('auth', sessionId);
  
  resp.status(200).send(username).end();
});

app.post('/register', (req, resp) => {
  if (!req.headers.authorization) {
    resp.status(400).send("Invalid Registration").end();
    return;
  }

  const auth = req.headers.authorization.substr(6);
  const decoded = new Buffer(auth, 'base64').toString();
  const [user, password] = decoded.split(':');
  console.log("Register: " + user + ", password: " + password);

  if (user.length == 0) {
    resp.status(400).send("Invalid User").end();
    return;
  }

  if (password.length == 0) {
    resp.status(400).send("Invalid Password").end();
    return;
  }

  if (logins.has(user)) {
    console.log("User " + user + " already exists");
    resp.status(400).send("User already registered").end();
    return;
  }

  const compound = saltCounter.toString() + password;

  const h = sha256.create();
  h.update(compound);

  logins.set(user, {salt: saltCounter.toString(), hash: h.hex()}, {admin: false});
  console.log(h.hex(), saltCounter);
  saltCounter++;

  resp.status(200).send(user);
});

app.delete('/users', (req, resp) => {
  if (!req.headers.authorization) {
    resp.status(400).send("Not Authorized").end();
    return;
  }

  const auth = req.headers.authorization.substr(6);
  const decoded = new Buffer(auth, 'base64').toString();
  const [user, password] = decoded.split(':');

  if (!logins.has(user)) {
    resp.status(404).send("User Not Found").end();
    return;
  }

  const compound = logins.get(user).salt + password;

  const h = sha256.create();
  h.update(compound);

  if (h.hex() != logins.get(user).hash) {
    resp.status(403).send("Wrong password").end();
    return;
  }

  logins.delete(user);

  resp.status(200).send("Deleted user: " + user).end();
});

app.post('/upload', upload.single('avatar'), (req, res) => {
  if (!req.query.serverName || !req.query.serverPassword) {
    res.status(400).send('Invalid Server Name or Password').end();
    return false;
  }

  if (!servers.has(req.query.serverName)) {
    res.status(400).send("No server with that name").end();
    return false;
  }

  const h = sha256.create();
  h.update(servers.get(req.query.serverName).salt + req.query.serverPassword);

  if (h.hex() != servers.get(req.query.serverName).hash) {
    res.status(400).send("Access Denied, wrong server password").end();
    return false;
  }

  if (!req.headers.authorization && !req.cookies.auth) {
    res.status(400).send("Invalid Login Info").end();
    return false;
  }

  if (!attemptAuth(req)) {
    res.status(400).send("Wrong login info").end();
    return false;
  }

  if (req.cookies.auth) {
    var username = cookies.get(req.cookies.auth);
  } else if (req.headers.authorization) {
    const auth = req.headers.authorization.substr(6);
    const decoded = new Buffer(auth, 'base64').toString();
    const [login, password] = decoded.split(':');
    var username = login;
  }

  if (servers.get(req.query.serverName).owner != username) {
    res.status(403).send("Not allowed to upload mods").end();
    return false;
  }

  minioClient.putObject("mods", req.file.originalname, req.file.buffer, function(error, etag) {
    if (error) {
      res.status(400).send("Minio Error").end();
      return console.log(error);
    }
  });

  res.status(200).send("Mod succesfully uploaded").end();
});

app.get('/upload', (req, res) => {
  const output = [];

  var stream = minioClient.listObjects("mods");

  stream.on('data', function(obj) {
    console.log(obj);
    output.push(obj.name);
  });

  stream.on('end', function() {
    res.json(output);
  });
});

app.get('/download', (req, res) => {
  const fileDirectory = './uploads/' + req.query.mod;
  // const file = './uploads/Xaeros_Minimap_21.10.0.3_Forge_1.16.5.jar';
  res.download(fileDirectory);
});

app.get('/servers', (req, resp) => {
  if (!req.query.serverName) {
    resp.status(200).send(Array.from(servers.keys())).end();
    console.log(servers);
    return;
  }

  if (!servers.has(req.query.serverName)) {
    resp.status(400).send("No server with that name").end();
    return;
  }

  const h = sha256.create();
  h.update(servers.get(req.query.serverName).salt + req.query.serverPassword);

  if (h.hex() != servers.get(req.query.serverName).hash) {
    resp.status(400).send("Incorrect Password").end();
    return;
  }

  resp.status(200).send(req.query.serverName + "," + servers.get(req.query.serverName).owner).end();
});

app.post('/servers', (req, resp) => {
  if (!req.query.serverName || !req.query.serverPassword) {
    resp.status(400).send("Invalid Server Info").end();
    return;
  }

  serverName = req.query.serverName;
  serverPassword = req.query.serverPassword;

  if (attemptAuth(req) == false) {
    resp.status(400).send("Invalid User Login").end();
    return;
  }

  var username;

  if (req.cookies.auth) {
    username = cookies.get(req.cookies.auth);
  } else if (req.headers.authorization) {
    const auth = req.headers.authorization.substr(6);
    const decoded = new Buffer(auth, 'base64').toString()
    const [login, password] = decoded.split(':');
    username = login;
  }

  const h = sha256.create();

  h.update(saltCounter.toString() + serverPassword);
  servers.set(serverName, {salt: saltCounter.toString(), hash: h.hex(), owner: username});
  saltCounter++;

  resp.status(200).send(serverName).end();
});



// listen for requests :)
const listener = app.listen(process.env.PORT, () => {
  console.log("Your app is listening on port " + listener.address().port);
});

// const listener = app.listen(2000, () => {
//   console.log("Your app is listening on port " + listener.address().port);
// });