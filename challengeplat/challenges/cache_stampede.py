from .base import Challenge

class CacheStampedeChallenge(Challenge):
    def __init__(self):
        super().__init__()
        self.id = "cache-stampede"
        self.title = "Fix Cache Stampede Problem"
        self.difficulty = "Medium"
        self.test_command = "npm test"
        
        self.description = """
A Node.js API has a "thundering herd" problem with its cache.
When a popular item's cache expires, multiple requests hit the database simultaneously.

The Problem:
- Multiple identical database queries when cache expires
- System overload during traffic spikes
- Inconsistent data being cached

Your Task:
- Implement proper cache stampede prevention
- Ensure only ONE database call even with concurrent requests
- Maintain data consistency
"""
        
        self.files = {
            "server.js": '''const express = require('express');
const app = express();

const cache = new Map();

async function fetchFromDatabase(id) {
    console.log(`DB Query for ${id}`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { id, data: `Data for ${id}`, timestamp: Date.now() };
}

app.get('/api/data/:id', async (req, res) => {
    const { id } = req.params;
    
    const cached = cache.get(id);
    if (cached && Date.now() - cached.timestamp < 5000) {
        return res.json({ ...cached, source: 'cache' });
    }
    
    const data = await fetchFromDatabase(id);
    cache.set(id, data);
    
    res.json({ ...data, source: 'database' });
});

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

module.exports = { app, server };
''',

            "server.test.js": '''const request = require('supertest');
const { app, server } = require('./server');

describe('Cache Stampede Tests', () => {
    afterAll(() => {
        server.close();
    });
    
    test('should prevent cache stampede', async () => {
        const id = 'test-' + Date.now();
        let dbQueryCount = 0;
        
        const originalLog = console.log;
        console.log = (msg) => {
            if (msg.includes('DB Query')) dbQueryCount++;
            originalLog(msg);
        };
        
        const requests = Array(10).fill().map(() => 
            request(app).get(`/api/data/${id}`)
        );
        
        const responses = await Promise.all(requests);
        
        console.log = originalLog;
        
        responses.forEach(res => {
            expect(res.status).toBe(200);
            expect(res.body.id).toBe(id);
        });
        
        expect(dbQueryCount).toBe(1);
    }, 15000);
    
    test('should return consistent data', async () => {
        const id = 'consistency-test';
        
        const responses = await Promise.all(
            Array(5).fill().map(() => 
                request(app).get(`/api/data/${id}`)
            )
        );
        
        const firstData = responses[0].body.data;
        responses.forEach(res => {
            expect(res.body.data).toBe(firstData);
        });
    });
});
''',

            "package.json": '''{
  "name": "cache-challenge",
  "version": "1.0.0",
  "scripts": {
    "test": "jest --forceExit"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "supertest": "^6.3.0"
  }
}'''
        }
        
        self.solution = {
            "server.js": '''const express = require('express');
const app = express();

const cache = new Map();
const inFlightRequests = new Map();

async function fetchFromDatabase(id) {
    console.log(`DB Query for ${id}`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { id, data: `Data for ${id}`, timestamp: Date.now() };
}

app.get('/api/data/:id', async (req, res) => {
    const { id } = req.params;
    
    const cached = cache.get(id);
    if (cached && Date.now() - cached.timestamp < 5000) {
        return res.json({ ...cached, source: 'cache' });
    }
    
    if (inFlightRequests.has(id)) {
        const data = await inFlightRequests.get(id);
        return res.json({ ...data, source: 'database' });
    }
    
    const dataPromise = fetchFromDatabase(id).then(data => {
        cache.set(id, data);
        inFlightRequests.delete(id);
        return data;
    });
    
    inFlightRequests.set(id, dataPromise);
    
    const data = await dataPromise;
    res.json({ ...data, source: 'database' });
});

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT);

module.exports = { app, server };
'''
        }
        
        self.hints = [
            "Think about tracking 'in-flight' requests",
            "How can you make other requests wait for the first one?",
            "Consider using Promises effectively"
        ]