const fs = require('fs');
const path = require('path');

const defaultData = {
  users: [],
  products: [],
  inventory: [],
  counters: { user: 1, product: 1, inventory: 1 }
};

class Store {
  constructor(filePath) {
    this.filePath = filePath;
    this.data = this.load();
  }

  load() {
    if (!fs.existsSync(this.filePath)) {
      this.persist(defaultData);
      return JSON.parse(JSON.stringify(defaultData));
    }
    return JSON.parse(fs.readFileSync(this.filePath, 'utf8'));
  }

  persist(data) {
    fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
    fs.writeFileSync(this.filePath, JSON.stringify(data, null, 2));
  }

  save() {
    this.persist(this.data);
  }

  nextId(kind) {
    const id = this.data.counters[kind];
    this.data.counters[kind] += 1;
    return id;
  }
}

module.exports = { Store };
