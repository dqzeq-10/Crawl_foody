// Toggle location dropdown
document.addEventListener('DOMContentLoaded', function() {
    // Toggle location dropdown
    document.getElementById('location-dropdown').addEventListener('click', function() {
        const popup = document.getElementById('popup-location');
        if (popup.style.display === 'block') {
            popup.style.display = 'none';
        } else {
            popup.style.display = 'block';
        }
    });

    // Sample data for locations
    const locations = [
        { name: 'Hồ Chí Minh', id: '217' },
        { name: 'Hà Nội', id: '218' },
        { name: 'Đà Nẵng', id: '219' },
        { name: 'Cần Thơ', id: '220' },
        { name: 'Hải Phòng', id: '221' },
        { name: 'Nha Trang', id: '222' },
        { name: 'Vũng Tàu', id: '223' },
    ];

    // Populate location list
    const locationList = document.querySelector('.location-list');
    if (locationList) {
        locations.forEach(location => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `/${location.name.toLowerCase().replace(' ', '-')}`;
            a.textContent = location.name;
            li.appendChild(a);
            locationList.appendChild(li);
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('location-dropdown');
        const popup = document.getElementById('popup-location');
        
        if (dropdown && popup && !dropdown.contains(event.target)) {
            popup.style.display = 'none';
        }
    });

    // Handle bookmark icons
    const bookmarkIcons = document.querySelectorAll('.bookmark-icon');
    bookmarkIcons.forEach(icon => {
        icon.addEventListener('click', function() {
            const heartIcon = this.querySelector('i');
            if (heartIcon.classList.contains('far')) {
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                heartIcon.style.color = '#ee4d2d';
            } else {
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                heartIcon.style.color = '#ccc';
            }
        });
    });
});