// const express = require('express');
// const axios = require('axios');  // Phải cài thêm bằng: npm install axios

// const app = express();
// const port = 3000;

// app.use(express.static('public'));

// // Route gọi FastAPI
// app.get('/api/sanpham', async (req, res) => {
//   try {
//     const response = await axios.get('http://localhost:8000/api/sanpham');
//     res.json(response.data);
//   } catch (err) {
//     console.error(err);
//     res.status(500).send('Lỗi gọi API');
//   }
// });

// // Mặc định trả về HTML
// app.get('/', (req, res) => {
//   res.sendFile(__dirname + '/public/foody.html');
// });

// app.listen(port, () => {
//   console.log(`Web chạy tại http://localhost:${port}`);
// });
const express = require('express');
const path = require('path');
const app = express();
const port = 3000; // hoặc cổng bạn expose

app.use(express.static('public')); // hoặc thư mục của bạn chứa HTML/CSS


// Cấp quyền phục vụ toàn bộ thư mục web_page là static (bao gồm HTML + ảnh)
app.use(express.static(path.join(__dirname, 'web_page')));

// Nếu muốn đảm bảo truy cập trang chủ (/) trả về file HTML:
// app.get('/', (req, res) => {
//   res.sendFile(path.join(__dirname, 'web_page', '/public/foody.html'));
// });

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
