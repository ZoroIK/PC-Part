const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const axios = require('axios');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const app = express();
app.use(express.json());
app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

const jwt = require('jsonwebtoken'); // Import JWT
const SECRET_KEY = 'your_secret_key'; // Replace with a strong, secure key

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'Love@123456',
  database: 'pc',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
});

app.get('/', (req, res) => {
  return res.json('From Backend Side');
});

function authenticateToken(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1]; // Get token from Authorization header
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  jwt.verify(token, SECRET_KEY, (err, user) => {
      if (err) return res.status(403).json({ error: 'Invalid token' });
      req.user = user; // Attach the decoded user info to the request
      next();
  });
}
app.get('/user/saved-components', authenticateToken, (req, res) => {
  const userId = req.user.userId; // Get userId from the token

  const query = 'SELECT * FROM SavedComponents WHERE UserID = ?';
  pool.query(query, [userId], (err, results) => {
      if (err) {
          console.error('Error fetching components:', err);
          return res.status(500).send('Internal Server Error');
      }

      res.status(200).json(results);
  });
});

// Handle login request
app.post('/login', (req, res) => {
  const { email, password } = req.body;

    // Query the database to check email and password
    const query = 'SELECT * FROM Users WHERE Email = ?';
    pool.query(query, [email], (err, results) => {
        if (err) {
            console.error('Error executing MySQL query:', err);
            return res.status(500).send('Internal Server Error');
        }

        if (results.length === 0 || !validatePassword(password, results[0].PasswordHash)) {
            return res.status(401).send('Invalid email/password combination');
        }

        // Generate a JWT token
        const userId = results[0].UserID;
        const token = jwt.sign({ userId, email }, SECRET_KEY, { expiresIn: '1h' }); // Token valid for 1 hour

        // If login successful, return user data
        const userObj = {
            UserID: results[0].UserID,
            Email: results[0].Email,
        };

        res.status(200).json(userObj);
    });
});

// Function to validate password using bcrypt
function validatePassword(inputPassword, hashedPassword, salt) {
  return bcrypt.compareSync(inputPassword, hashedPassword);
}

// Handle create account request
app.post('/create-account', async (req, res) => {
  const { email, password } = req.body;

  try {
    // Check if email already exists in the database
    const query = 'SELECT * FROM Users WHERE Email = ?';
    const [rows] = await pool.promise().query(query, [email]);

    if (rows.length > 0) {
        return res.status(409).json({ error: 'Email already exists.' });
    }

    // Hash the password and save the new user to the database
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    const insertQuery = 'INSERT INTO Users (Email, PasswordHash) VALUES (?, ?)';
    await pool.promise().query(insertQuery, [email, hashedPassword]);

    res.status(201).json({ success: 'Account created successfully.' });
} catch (error) {
    console.error('Error creating account:', error);
    res.status(500).send('Internal Server Error');
}
});


//Amd Cpu
// Endpoint to get the list of all CPUs from the CPU_AMD table
app.get('/api/cpus_amd', (req, res) => {
  const query = 'SELECT * FROM CPU_AMD';

  pool.query(query, (err, results) => {
      if (err) {
          console.error('Error fetching data:', err);
          return res.status(500).json({ error: 'Failed to fetch CPUs' });
      }

      // Send the results as a JSON response
      res.json(results);
  });
});


const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});


pool.getConnection((err, connection) => {
  if (err) {
    console.error('Error getting database connection:', err);
    throw err;
  }

  console.log('Connected to database');

  connection.release();
});
