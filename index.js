const express = require("express");
const app = express();
const sha256 = require("js-sha256");
const cookieparser = require("cookie-parser");
const multer  = require('multer');
const path = require('path');
const fs = require('fs');
// const upload = multer({ dest: 'uploads/' })

var storage = multer.diskStorage(
  {
    destination: './uploads/',
    filename: function (req, file, cb) {
      cb(null, file.originalname);
    }
  }
);

const upload = multer({storage: storage});


app.use(express.json());
app.use(cookieparser());

const data = new Map();
data.set(1, {name: "Mario", surname: "Rossi"});
data.set(2, {name: "Luigi", surname: "Verdi"});

var dataID = 2;

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
    resp.status(200).send(cookies.get(req.cookies.auth)).end();
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
  
  resp.status(200).send(username).end();
});



// app.use(fileUpload());

// app.post('/upload', function(req, res) {
//   if (!req.files || Object.keys(req.files).length === 0) {
//     return res.status(400).send('No files were uploaded.');
//   }

//   // The name of the input field (i.e. "sampleFile") is used to retrieve the uploaded file
//   let sampleFile = req.files.sampleFile;

//   // Use the mv() method to place the file somewhere on your server
//   sampleFile.mv('/somewhere/on/your/server/filename.jpg', function(err) {
//     if (err)
//       return res.status(500).send(err);

//     res.send('File uploaded!');
//   });
// });





app.post('/upload', upload.single('avatar'), function(req, res) {
  if (!req.file) {
    res.status(400).send('No files uploaded');
  } else {

    var info;

    info = {
      fieldname: req.file.fieldname,
      originalName: req.file.originalname,
      encoding: req.file.encoding,
      mimetype: req.file.mimetype,
      size: req.file.size,
      destination: req.file.destination,
      filename: req.file.filename,
      path: req.file.path,
      buffer: req.file.buffer
    }


    res.json(info);
  }
});

app.get('/upload', (req, res) => {
  const directoryPath = path.join('./uploads');
  const output = [];

  fs.readdir(directoryPath, function (err, files) {
    if (err) {
      res.sendStatus(400);
    } else {
      files.forEach(function (file) {
        output.push(file);
      });

      res.json(output);
    }
  });
});


app.get('/download', (req, res) => {
  const fileDirectory = './uploads/' + req.query.mod;
  // const file = './uploads/Xaeros_Minimap_21.10.0.3_Forge_1.16.5.jar';
  res.download(fileDirectory);
});





// listen for requests :)
// const listener = app.listen(process.env.PORT, () => {
//   console.log("Your app is listening on port " + listener.address().port);
// });

const listener = app.listen(2000, () => {
  console.log("Your app is listening on port " + listener.address().port);
});