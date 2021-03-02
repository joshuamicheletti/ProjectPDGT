const express = require("express");
const app = express();

app.use(express.json());

const data = new Map();
data.set(1, {name: "Mario", surname: "Rossi"});
data.set(2, {name: "Luigi", surname: "Verdi"});

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
  
  const newId = data.size + 1;
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


// listen for requests :)
const listener = app.listen(process.env.PORT, () => {
  console.log("Your app is listening on port " + listener.address().port);
});