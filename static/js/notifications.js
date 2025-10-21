/**
 * Notification System for Admission System
 * Provides toast notifications and notification center
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.unreadCount = 0;
        this.init();
    }

    init() {
        // Create toast container
        this.createToastContainer();
        
        // Load notifications if user is logged in
        if (window.currentUserId) {
            this.loadNotifications();
            // Poll for new notifications every 30 seconds
            setInterval(() => this.loadNotifications(), 30000);
        }
    }

    createToastContainer() {
        // Create container for toast notifications
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-3';
        container.style.maxWidth = '400px';
        document.body.appendChild(container);
        this.container = container;
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: success, error, warning, info
     * @param {number} duration - Duration in ms (0 = no auto-dismiss)
     */
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast-notification transform translate-x-full transition-all duration-300 ease-out 
                          bg-white rounded-lg shadow-2xl p-4 flex items-start gap-3 border-l-4`;
        
        // Icon and color based on type
        let icon, borderColor, iconBg;
        switch(type) {
            case 'success':
                icon = 'fa-circle-check';
                borderColor = 'border-green-500';
                iconBg = 'bg-green-100 text-green-600';
                break;
            case 'error':
                icon = 'fa-circle-xmark';
                borderColor = 'border-red-500';
                iconBg = 'bg-red-100 text-red-600';
                break;
            case 'warning':
                icon = 'fa-triangle-exclamation';
                borderColor = 'border-yellow-500';
                iconBg = 'bg-yellow-100 text-yellow-600';
                break;
            default:
                icon = 'fa-circle-info';
                borderColor = 'border-blue-500';
                iconBg = 'bg-blue-100 text-blue-600';
        }
        
        toast.classList.add(borderColor);
        
        toast.innerHTML = `
            <div class="w-10 h-10 rounded-full ${iconBg} flex items-center justify-center flex-shrink-0">
                <i class="fa-solid ${icon} text-lg"></i>
            </div>
            <div class="flex-1">
                <p class="text-sm text-gray-800 font-medium">${message}</p>
            </div>
            <button class="text-gray-400 hover:text-gray-600 transition close-toast">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 10);
        
        // Close button
        toast.querySelector('.close-toast').addEventListener('click', () => {
            this.dismissToast(toast);
        });
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismissToast(toast);
            }, duration);
        }
    }

    dismissToast(toast) {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Load notifications from server
     */
    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                const data = await response.json();
                this.updateNotificationBadge(data.unread_count);
                this.updateNotificationDropdown(data.notifications);
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            this.unreadCount = count;
            badge.textContent = count;
            badge.classList.toggle('hidden', count === 0);
        }
    }

    updateNotificationDropdown(notifications) {
        const dropdown = document.getElementById('notificationDropdown');
        if (!dropdown) return;
        
        const list = dropdown.querySelector('.notification-list');
        if (!list) return;
        
        if (notifications.length === 0) {
            list.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fa-solid fa-bell-slash text-4xl mb-2"></i>
                    <p class="text-sm">Không có thông báo mới</p>
                </div>
            `;
            return;
        }
        
        list.innerHTML = notifications.map(notif => {
            const typeIcons = {
                'success': 'fa-circle-check text-green-500',
                'error': 'fa-circle-xmark text-red-500',
                'warning': 'fa-triangle-exclamation text-yellow-500',
                'info': 'fa-circle-info text-blue-500'
            };
            
            const icon = typeIcons[notif.type] || typeIcons.info;
            const bgClass = notif.is_read ? 'bg-white' : 'bg-blue-50';
            
            return `
                <div class="notification-item ${bgClass} hover:bg-gray-50 p-4 border-b cursor-pointer transition"
                     data-id="${notif.id}" 
                     onclick="notificationSystem.markAsRead(${notif.id}, '${notif.link || ''}')">
                    <div class="flex items-start gap-3">
                        <i class="fa-solid ${icon} mt-1"></i>
                        <div class="flex-1 min-w-0">
                            <h4 class="font-semibold text-sm text-gray-800">${notif.title}</h4>
                            <p class="text-xs text-gray-600 mt-1">${notif.message}</p>
                            <span class="text-xs text-gray-400 mt-2 inline-block">
                                ${this.formatTime(notif.created_at)}
                            </span>
                        </div>
                        ${!notif.is_read ? '<span class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2"></span>' : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Mark notification as read
     */
    async markAsRead(notificationId, link = '') {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.loadNotifications(); // Reload to update UI
                
                // Navigate to link if provided
                if (link) {
                    setTimeout(() => {
                        window.location.href = link;
                    }, 200);
                }
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }

    /**
     * Mark all notifications as read
     */
    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.loadNotifications();
                this.showToast('Đã đánh dấu tất cả thông báo là đã đọc', 'success');
            }
        } catch (error) {
            console.error('Failed to mark all as read:', error);
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // seconds
        
        if (diff < 60) return 'Vừa xong';
        if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
        if (diff < 604800) return `${Math.floor(diff / 86400)} ngày trước`;
        
        return date.toLocaleDateString('vi-VN');
    }
}

// Initialize notification system
let notificationSystem;
document.addEventListener('DOMContentLoaded', function() {
    notificationSystem = new NotificationSystem();
    
    // Toggle notification dropdown
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationDropdown = document.getElementById('notificationDropdown');
    
    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationDropdown.classList.toggle('hidden');
        });
        
        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (!notificationDropdown.contains(e.target) && !notificationBtn.contains(e.target)) {
                notificationDropdown.classList.add('hidden');
            }
        });
    }
    
    // Mark all as read button
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function() {
            notificationSystem.markAllAsRead();
        });
    }
});

// Expose to global scope for inline onclick handlers
window.notificationSystem = notificationSystem;
