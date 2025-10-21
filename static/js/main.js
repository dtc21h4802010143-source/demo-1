document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.createElement('button');
    navToggle.classList.add('nav-toggle');
    navToggle.innerHTML = '☰';
    document.querySelector('.main-nav').prepend(navToggle);

    navToggle.addEventListener('click', () => {
        document.querySelector('.nav-links').classList.toggle('active');
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Flash message auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('invalid');
                    
                    // Create or update error message
                    let errorMessage = field.nextElementSibling;
                    if (!errorMessage || !errorMessage.classList.contains('error-message')) {
                        errorMessage = document.createElement('div');
                        errorMessage.classList.add('error-message');
                        field.parentNode.insertBefore(errorMessage, field.nextSibling);
                    }
                    errorMessage.textContent = 'Trường này là bắt buộc';
                } else {
                    field.classList.remove('invalid');
                    const errorMessage = field.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains('error-message')) {
                        errorMessage.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Dynamic content loading
    const loadMoreButtons = document.querySelectorAll('.load-more');
    loadMoreButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const target = this.dataset.target;
            const page = parseInt(this.dataset.page) || 1;
            
            try {
                const response = await fetch(`/api/load-more/${target}?page=${page + 1}`);
                const data = await response.json();
                
                if (data.items && data.items.length > 0) {
                    const container = document.querySelector(`#${target}-container`);
                    data.items.forEach(item => {
                        // Create and append new elements based on item type
                        const element = createElementFromData(item, target);
                        container.appendChild(element);
                    });
                    
                    this.dataset.page = page + 1;
                    
                    if (!data.hasMore) {
                        this.style.display = 'none';
                    }
                }
            } catch (error) {
                console.error('Error loading more items:', error);
            }
        });
    });
});

// Utility function to create elements from data
function createElementFromData(item, type) {
    const element = document.createElement('div');
    
    switch(type) {
        case 'programs':
            element.classList.add('program-card');
            element.innerHTML = `
                <h3>${item.name}</h3>
                <p class="program-code">Mã ngành: ${item.code}</p>
                <p class="program-description">${item.description}</p>
                <div class="program-details">
                    <span>Thời gian: ${item.duration}</span>
                    <span>Học phí: ${item.tuition_fee.toLocaleString('vi-VN')} VNĐ/năm</span>
                </div>
                <a href="/programs/${item.id}" class="btn btn-outline">Chi tiết</a>
            `;
            break;
            
        case 'news':
            element.classList.add('news-card');
            element.innerHTML = `
                <img src="${item.image}" alt="${item.title}">
                <div class="news-content">
                    <h3>${item.title}</h3>
                    <p class="news-date">${new Date(item.date).toLocaleDateString('vi-VN')}</p>
                    <p>${item.excerpt}</p>
                    <a href="/news/${item.id}" class="btn btn-text">Đọc thêm</a>
                </div>
            `;
            break;
            
        // Add more cases as needed
    }
    
    return element;
}

// Handle file uploads with preview
function handleFileUpload(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.querySelector(`#${input.dataset.preview}`);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Initialize dynamic components
function initDynamicComponents() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.dataset.tooltip;
            const tooltipEl = document.createElement('div');
            tooltipEl.classList.add('tooltip');
            tooltipEl.textContent = tooltipText;
            document.body.appendChild(tooltipEl);
            
            const rect = this.getBoundingClientRect();
            tooltipEl.style.top = `${rect.top - tooltipEl.offsetHeight - 5}px`;
            tooltipEl.style.left = `${rect.left + (rect.width - tooltipEl.offsetWidth) / 2}px`;
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });

    // Initialize tabs
    const tabContainers = document.querySelectorAll('.tab-container');
    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('.tab');
        const panels = container.querySelectorAll('.tab-panel');
        
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs and panels
                tabs.forEach(t => t.classList.remove('active'));
                panels.forEach(p => p.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding panel
                tab.classList.add('active');
                panels[index].classList.add('active');
            });
        });
    });
}