const express = require("express");
const app = express();
const sha256 = require("js-sha256");
const cookieparser = require("cookie-parser");

app.use(express.json());
app.use(cookieparser());

const data = new Map();
data.set(1, {name: "Mario", surname: "Rossi"});
data.set(2, {name: "Luigi", surname: "Verdi"});

var dataID = 3;

app.get('/people', (req, resp) => {
  if (!req.accepts('application/json')) {
    resp.sendStatus(406);
    return;
  }
  
  const output = Array.from(data, ([key, value]) => {
    return {
      id: key,
      name: value.name,
      surname: value.surname
    };
  });
  resp.json(output);
});

app.get('/people/:id', (req, resp) => {
  const id = Number.parseInt(req.params.id);
  
  if (Number.isNaN(id)) {
    resp.sendStatus(400);
    return;
  }
  if (!data.has(id)) {
    resp.sendStatus(404);
    return;
  }
  
  const person = data.get(id);
  
  resp.format({
    'text/plain': () => {
      resp.send(person.name + ' ' + person.surname);
    },
    'text/html': () => {
      resp.send('<html><body><p>Il signor <b>' + person.name + ' ' + person.surname + '</b></p></body></html>');
    },
    'application/json': () => {
      //resp.send(JSON.stringify(person));
      resp.json(person);
    },
    defaul: () => {
      resp.sendStatus(406);
    }
  });
});

app.post('/people', (req, resp) => {
  const input = req.body;
  
  if (!input.name) {
    resp.sendStatus(422);
    return;
  }
  if (!input.surname) {
    resp.sendStatus(422);
    return;
  }
  
  const name = new String(input.name);
  const surname = new String(input.surname);
  
  dataID++;
  const newId = dataID;
  data.set(newId, {name: name, surname: surname});
  
  resp.status(201).type('application/json').send(JSON.stringify({id: newId, name: name, surname: surname}));
});

app.delete('/people/:id', (req, resp) => {
  const id = Number.parseInt(req.params.id);
  
  if (Number.isNaN(id)) {
    resp.sendStatus(400);
    return;
  }
  if (!data.has(id)) {
    resp.sendStatus(404);
    return;
  }
  
  data.delete(id);
  
  resp.sendStatus(200);
});


const logins = new Map();
logins.set('joshua', {salt: '123456', hash: 'aca2d6bd777ac00e4581911a87dcc8a11b5faf11e08f584513e380a01693ef38'});

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
    resp.status(200).send("File segretissimo").end();
  } else {
    resp.set('WWW-Authenticate', 'Basic realm="Cose segrete"').sendStatus(401).end();
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
    resp.sendStatus(403).end();
    return;
  }
  
  const now = new Date().toString();
  
  const h = sha256.create();
  h.update(now);
  const sessionId = h.hex();
  
  cookies.set(sessionId, username);
  
  resp.cookie('auth', sessionId);
  
  resp.status(200).send("Sei autenticato!").end();
});







// listen for requests :)
const listener = app.listen(process.env.PORT, () => {
  console.log("Your app is listening on port " + listener.address().port);
});