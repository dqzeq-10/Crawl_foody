// Toggle location dropdown
document.addEventListener('DOMContentLoaded', function () {
    // Toggle location dropdown
    document.getElementById('location-dropdown').addEventListener('click', function () {
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
    ];    // Populate location list
    const locationList = document.querySelector('.location-list');
    if (locationList) {
        locations.forEach(location => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = "#"; // Change to client-side handling
            a.textContent = location.name;
            a.dataset.id = location.id; // Store ID as data attribute
            a.addEventListener('click', function (e) {
                e.preventDefault();
                // Update location name in UI
                document.querySelector('.location-name').textContent = location.name;
                // Close popup
                document.getElementById('popup-location').style.display = 'none';
                // Reset pagination and reload branches for this location
                currentPage = 1;
                fetchBranches(location.id);
            });
            li.appendChild(a);
            locationList.appendChild(li);
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function (event) {
        const dropdown = document.getElementById('location-dropdown');
        const popup = document.getElementById('popup-location');

        if (dropdown && popup && !dropdown.contains(event.target)) {
            popup.style.display = 'none';
        }
    });

    // Handle bookmark icons
    const bookmarkIcons = document.querySelectorAll('.bookmark-icon');
    bookmarkIcons.forEach(icon => {
        icon.addEventListener('click', function () {
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

    // Fetch branches from API and display them
    fetchBranches();
});

// Function to fetch branches from API
async function fetchBranches(locationId) {
    // Show loading state
    const rowView = document.querySelector('.row-view-content');
    if (rowView) {
        rowView.innerHTML = `
            <div class="loading-message">
                <p>Đang tải dữ liệu...</p>
                <div class="spinner"></div>
            </div>
        `;
    }

    try {
        // API base URL - adjust this based on your setup
        const apiBaseUrl = 'http://localhost:8000';

        // Fetch branches data with a timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 seconds timeout

        // Add location parameter if provided
        const url = locationId
            ? `${apiBaseUrl}/branches?location=${locationId}`
            : `${apiBaseUrl}/branches`;

        const response = await fetch(url, {
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const branches = await response.json();
        displayBranches(branches);
    } catch (error) {
        console.error('Error fetching branches:', error);
        // Display error message on the page
        const rowView = document.querySelector('.row-view-content');
        if (rowView) {
            rowView.innerHTML = `
                <div class="error-message">
                    <p>Không thể tải dữ liệu. Vui lòng thử lại sau.</p>
                    <p>Chi tiết lỗi: ${error.name === 'AbortError' ? 'Kết nối quá thời gian. Vui lòng kiểm tra kết nối mạng của bạn.' : error.message}</p>
                    <button class="retry-button" onclick="fetchBranches()">Thử lại</button>
                </div>
            `;
        }
    }
}

// Global variables for pagination
let currentPage = 1;
let itemsPerPage = 12;
let allBranches = [];

// Function to display branches in the UI with pagination
function displayBranches(branches) {
    const rowViewContent = document.querySelector('.row-view-content');
    if (!rowViewContent) return;

    // Store all branches globally for pagination
    allBranches = branches;

    // Clear existing content
    rowViewContent.innerHTML = '';

    // Check if we have branches to display
    if (!branches || branches.length === 0) {
        rowViewContent.innerHTML = `
            <div class="error-message">
                <p>Không tìm thấy kết quả nào.</p>
                <p>Vui lòng thử tìm kiếm với từ khóa khác.</p>
            </div>
        `;
        return;
    }

    // Display current page
    displayPage(currentPage);

    // Add pagination controls
    addPaginationControls(rowViewContent);
}

// Format the branch data into HTML with error handling for missing data
// item.innerHTML = `
//     <div class="bookmark-icon">
//         <i class="far fa-heart"></i>
//     </div>
//     <div class="item-info">
//         <a href="#" class="item-name">${branch.BranchName || 'Không có tên'}</a>
//         <div class="item-address">${branch.Address || 'Không có địa chỉ'}</div>
//         <div class="item-city">${branch.City || 'Không có thành phố'}</div>
//         <div class="item-meta">
//             <div class="item-rating">
//                 <i class="fas fa-star" style="color: #FFC107;"></i>
//                 <span>${branch.AvgRating ? branch.AvgRating.toFixed(1) : 'N/A'}</span>
//             </div>
//             <div class="item-reviews">
//                 <i class="fas fa-comment"></i>
//                 ${branch.TotalReview || 0}
//             </div>
//             <div class="item-checkins">
//                 <i class="fas fa-map-marker-alt"></i>
//                 ${branch.TotalCheckins || 0}
//             </div>
//         </div>
//         <div class="item-status">
//             <div class="${branch.IsOpening ? 'open-now' : 'closed-now'}">
//                 <i class="fas fa-clock status-icon"></i>
//                 ${branch.IsOpening ? 'Đang mở cửa' : 'Đã đóng cửa'}
//             </div>
//             <div class="delivery-available">
//                 <i class="fas fa-motorcycle status-icon"></i>
//                 ${branch.HasDelivery ? 'Giao hàng' : 'Không giao'}
//             </div>
//         </div>
//     </div>
// `;

// Add item to row
//itemsRow.appendChild(item);


// Add row to container
//rowViewContent.appendChild(itemsRow);


// Re-attach event listeners for bookmark icons
const bookmarkIcons = document.querySelectorAll('.bookmark-icon');
bookmarkIcons.forEach(icon => {
    icon.addEventListener('click', function () {
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


// Function to display a specific page of branches
function displayPage(page) {
    const rowViewContent = document.querySelector('.row-view-content');
    if (!rowViewContent) return;

    // Calculate start and end indices for the current page
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, allBranches.length);

    // Get branches for the current page
    const currentBranches = allBranches.slice(startIndex, endIndex);

    // Display total results count
    const countInfo = document.createElement('div');
    countInfo.className = 'results-count';
    countInfo.innerHTML = `Hiển thị ${startIndex + 1}-${endIndex} của ${allBranches.length} kết quả`;
    rowViewContent.appendChild(countInfo);

    // Create rows of items (4 items per row)
    for (let i = 0; i < currentBranches.length; i += 4) {
        const itemsRow = document.createElement('div');
        itemsRow.className = 'items-row';

        // Add up to 4 items to this row
        for (let j = i; j < i + 4 && j < currentBranches.length; j++) {
            const branch = currentBranches[j];

            // Create item element
            const item = document.createElement('div');
            item.className = 'item';

            // Format the branch data into HTML with error handling for missing data
            item.innerHTML = `
                <div class="bookmark-icon">
                    <i class="far fa-heart"></i>
                </div>
                <div class="item-info">
                    <a href="#" class="item-name">${branch.BranchName || 'Không có tên'}</a>
                    <div class="item-address">${branch.Address || 'Không có địa chỉ'}</div>
                    <div class="item-city">${branch.City || 'Không có thành phố'}</div>
                    <div class="item-meta">
                        <div class="item-rating">
                            <i class="fas fa-star" style="color: #FFC107;"></i>
                            <span>${branch.AvgRating ? branch.AvgRating.toFixed(1) : 'N/A'}</span>
                        </div>
                        <div class="item-reviews">
                            <i class="fas fa-comment"></i>
                            ${branch.TotalReview || 0}
                        </div>
                        <div class="item-checkins">
                            <i class="fas fa-map-marker-alt"></i>
                            ${branch.TotalCheckins || 0}
                        </div>
                    </div>
                    <div class="item-status">
                        <div class="${branch.IsOpening ? 'open-now' : 'closed-now'}">
                            <i class="fas fa-clock status-icon"></i>
                            ${branch.IsOpening ? 'Đang mở cửa' : 'Đã đóng cửa'}
                        </div>
                        <div class="delivery-available">
                            <i class="fas fa-motorcycle status-icon"></i>
                            ${branch.HasDelivery ? 'Giao hàng' : 'Không giao'}
                        </div>
                    </div>
                </div>
            `;

            // Add item to row
            itemsRow.appendChild(item);
        }

        // Add row to container
        rowViewContent.appendChild(itemsRow);
    }

    // Re-attach event listeners for bookmark icons
    const bookmarkIcons = document.querySelectorAll('.bookmark-icon');
    bookmarkIcons.forEach(icon => {
        icon.addEventListener('click', function () {
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
}

// Function to add pagination controls
function addPaginationControls(container) {
    // Calculate total pages
    const totalPages = Math.ceil(allBranches.length / itemsPerPage);

    // If only one page, don't show pagination
    if (totalPages <= 1) {
        return;
    }

    // Create pagination container
    const paginationContainer = document.createElement('div');
    paginationContainer.className = 'pagination-container';

    // Previous page button
    const prevButton = document.createElement('button');
    prevButton.className = 'pagination-button prev-button';
    prevButton.disabled = currentPage === 1;
    prevButton.innerHTML = '<i class="fas fa-chevron-left"></i> Trang trước';
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            container.innerHTML = '';
            displayPage(currentPage);
            addPaginationControls(container);
        }
    });
    paginationContainer.appendChild(prevButton);

    // Page number buttons
    const paginationNumbers = document.createElement('div');
    paginationNumbers.className = 'pagination-numbers';

    // Determine which page numbers to show
    let startPageNum = Math.max(1, currentPage - 2);
    let endPageNum = Math.min(totalPages, startPageNum + 4);

    // Adjust if we're near the end
    if (endPageNum === totalPages) {
        startPageNum = Math.max(1, endPageNum - 4);
    }

    // First page button if not starting at page 1
    if (startPageNum > 1) {
        const firstPageBtn = document.createElement('button');
        firstPageBtn.className = 'pagination-button page-number';
        firstPageBtn.textContent = '1';
        firstPageBtn.addEventListener('click', () => {
            currentPage = 1;
            container.innerHTML = '';
            displayPage(currentPage);
            addPaginationControls(container);
        });
        paginationNumbers.appendChild(firstPageBtn);

        if (startPageNum > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'pagination-ellipsis';
            ellipsis.textContent = '...';
            paginationNumbers.appendChild(ellipsis);
        }
    }

    // Add page number buttons
    for (let i = startPageNum; i <= endPageNum; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = 'pagination-button page-number';
        if (i === currentPage) {
            pageButton.classList.add('active');
        }
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            currentPage = i;
            container.innerHTML = '';
            displayPage(currentPage);
            addPaginationControls(container);
        });
        paginationNumbers.appendChild(pageButton);
    }

    // Last page button if not ending at the last page
    if (endPageNum < totalPages) {
        if (endPageNum < totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'pagination-ellipsis';
            ellipsis.textContent = '...';
            paginationNumbers.appendChild(ellipsis);
        }

        const lastPageBtn = document.createElement('button');
        lastPageBtn.className = 'pagination-button page-number';
        lastPageBtn.textContent = totalPages;
        lastPageBtn.addEventListener('click', () => {
            currentPage = totalPages;
            container.innerHTML = '';
            displayPage(currentPage);
            addPaginationControls(container);
        });
        paginationNumbers.appendChild(lastPageBtn);
    }

    paginationContainer.appendChild(paginationNumbers);

    // Next page button
    const nextButton = document.createElement('button');
    nextButton.className = 'pagination-button next-button';
    nextButton.disabled = currentPage === totalPages;
    nextButton.innerHTML = 'Trang kế tiếp <i class="fas fa-chevron-right"></i>';
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            container.innerHTML = '';
            displayPage(currentPage);
            addPaginationControls(container);
        }
    });
    paginationContainer.appendChild(nextButton);

    // Add pagination container to the main container
    container.appendChild(paginationContainer);
}

// Search functionality
document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');

    //hiển thị gợi ý
    const suggestionsBox = document.getElementById('search-suggestions');

    searchInput.addEventListener('input', async function () {
        const query = searchInput.value.trim();

        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        try {
            const apiBaseUrl = 'http://localhost:8000';
            const response = await fetch(`${apiBaseUrl}/branch/search/?q=${encodeURIComponent(query)}`);
            const branches = await response.json();

            // Hiển thị gợi ý
            suggestionsBox.innerHTML = '';
            if (branches.length === 0) {
                suggestionsBox.innerHTML = `<div class="suggestion-item">Không tìm thấy kết quả</div>`;
            } else {
                branches.slice(0, 8).forEach(branch => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = branch.BranchName || 'Không rõ tên';
                    div.addEventListener('click', () => {
                        searchInput.value = branch.BranchName;
                        suggestionsBox.style.display = 'none';
                        searchBranches(branch.BranchName);
                    });
                    suggestionsBox.appendChild(div);
                });
            }

            suggestionsBox.style.display = 'block';
        } catch (error) {
            console.error('Lỗi gợi ý:', error);
            suggestionsBox.style.display = 'none';
        }
    });
    //ẩn khi rời khỏi ô tìm kiếm
    searchInput.addEventListener('blur', () => {
        setTimeout(() => suggestionsBox.style.display = 'none', 150); // chờ để xử lý click
    });



    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const query = searchInput.value.trim();

            if (query) {
                searchBranches(query);
            } else {
                // If empty query, fetch all branches
                fetchBranches();
            }
        });
        // Add search button click event
        const searchBtn = document.querySelector('.search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', function (event) {
                event.preventDefault();
                const query = searchInput.value.trim();

                if (query) {
                    searchBranches(query);
                } else {
                    // If empty query, fetch all branches
                    fetchBranches();
                }
            });
        }
    }
});

// Function to search branches
async function searchBranches(query) {
    // Show loading state
    const rowView = document.querySelector('.row-view-content');
    if (rowView) {
        rowView.innerHTML = `
            <div class="loading-message">
                <p>Đang tìm kiếm "${query}"...</p>
                <div class="spinner"></div>
            </div>
        `;
    }

    try {
        // API base URL - adjust this based on your setup
        const apiBaseUrl = 'http://localhost:8000';

        // Fetch search results with a timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 seconds timeout

        const response = await fetch(`${apiBaseUrl}/branch/search/?q=${encodeURIComponent(query)}`, {
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const branches = await response.json();
        // Reset current page to 1 for new search
        currentPage = 1;

        // Display search results
        displayBranches(branches);

        // Update UI to show search results text
        const deliveryTabs = document.querySelector('.delivery-tabs');
        if (deliveryTabs) {
            const tabs = deliveryTabs.querySelectorAll('.delivery-tab');
            const queryText = `Kết quả tìm kiếm: "${query}"`;

            // Tìm tab "Kết quả tìm kiếm"
            let searchTab = deliveryTabs.querySelector('.search-results-tab');

            if (searchTab) {
                // Nếu đã tồn tại, chỉ cần cập nhật nội dung
                searchTab.textContent = queryText;
            } else {
                // Nếu chưa có, tạo mới và chèn sau tab "Đánh giá tốt nhất"
                searchTab = document.createElement('a');
                searchTab.className = 'delivery-tab search-results-tab';
                searchTab.textContent = queryText;

                // Chèn sau tab "Đánh giá tốt nhất" (tab thứ 3: index 2)
                if (tabs.length >= 3) {
                    tabs[2].after(searchTab);
                } else {
                    deliveryTabs.appendChild(searchTab); // fallback
                }
            }

            // Cập nhật trạng thái active
            const currentActive = deliveryTabs.querySelector('.delivery-tab.active');
            if (currentActive) {
                currentActive.classList.remove('active');
            }
            searchTab.classList.add('active');
        }


    } catch (error) {
        console.error('Error searching branches:', error);
        // Display error message on the page
        const rowView = document.querySelector('.row-view-content');
        if (rowView) {
            rowView.innerHTML = `
                <div class="error-message">
                    <p>Không thể tìm kiếm. Vui lòng thử lại sau.</p>
                    <p>Chi tiết lỗi: ${error.name === 'AbortError' ? 'Kết nối quá thời gian. Vui lòng kiểm tra kết nối mạng của bạn.' : error.message}</p>
                    <button class="retry-button" onclick="searchBranches('${query.replace(/'/g, "\\'")}')">Thử lại</button>
                </div>
            `;
        }
    }
}

// Add filter functionality for the delivery tabs
document.addEventListener('DOMContentLoaded', function () {
    const deliveryTabs = document.querySelectorAll('.delivery-tab');

    deliveryTabs.forEach(tab => {
        tab.addEventListener('click', function (event) {
            event.preventDefault();

            // Remove active class from all tabs
            deliveryTabs.forEach(t => t.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');

            // Apply filter based on tab text
            const filter = this.textContent.trim();
            applyFilter(filter);
        });
    });
});

// Function to apply filter to branches
async function applyFilter(filter) {
    // Show loading state
    const rowView = document.querySelector('.row-view-content');
    if (rowView) {
        rowView.innerHTML = `
            <div class="loading-message">
                <p>Đang lọc kết quả...</p>
                <div class="spinner"></div>
            </div>
        `;
    }

    // Fetch all branches first
    try {
        const apiBaseUrl = 'http://localhost:8000';

        // Fetch branches data with a timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 seconds timeout

        const response = await fetch(`${apiBaseUrl}/branches`, {
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        let branches = await response.json();

        // Apply filter logic
        switch (filter) {
            case 'Đúng nhất':
                // Default sorting - no changes needed
                break;
            case 'Phổ biến nhất':
                branches.sort((a, b) => b.TotalCheckins - a.TotalCheckins);
                break;
            case 'Đánh giá tốt nhất':
                branches.sort((a, b) => b.AvgRating - a.AvgRating);
                break;
            default:
                // Default case, no sorting
                break;
        }
        // Update UI to show active filter
        const deliveryTabs = document.querySelectorAll('.delivery-tab');
        deliveryTabs.forEach(tab => {
            if (tab.textContent === filter) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Reset current page to 1 for new filter
        currentPage = 1;

        // Display filtered branches
        displayBranches(branches);
    } catch (error) {
        console.error('Error applying filter:', error);
        // Display error message on the page
        const rowView = document.querySelector('.row-view-content');
        if (rowView) {
            rowView.innerHTML = `
                <div class="error-message">
                    <p>Không thể lọc kết quả. Vui lòng thử lại sau.</p>
                    <p>Chi tiết lỗi: ${error.name === 'AbortError' ? 'Kết nối quá thời gian. Vui lòng kiểm tra kết nối mạng của bạn.' : error.message}</p>
                    <button class="retry-button" onclick="applyFilter('${filter.replace(/'/g, "\\'")}')">Thử lại</button>
                </div>
            `;
        }
    }
}