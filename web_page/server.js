const express = require('express');
const axios = require('axios');  // Phải cài thêm bằng: npm install axios

const app = express();
const port = 3000;

app.use(express.static('public'));

// Route gọi FastAPI
app.get('/api/sanpham', async (req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/api/sanpham');
    res.json(response.data);
  } catch (err) {
    console.error(err);
    res.status(500).send('Lỗi gọi API');
  }
});

// Mặc định trả về HTML
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/foody.html');
});

app.listen(port, () => {
  console.log(`Web chạy tại http://localhost:${port}`);
});
