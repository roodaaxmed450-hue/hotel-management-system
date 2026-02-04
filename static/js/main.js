
// Main Application Interactivity
document.addEventListener('DOMContentLoaded', () => {
    initToasts();
    initTableSearch();
    initSidebar();
    
    // Auto-init specific page modules
    if(document.querySelector('#booking-form')) initBookingCalculator();
});

// Toast Notifications
function initToasts() {
    const messages = document.querySelectorAll('.django-message');
    const container = document.createElement('div');
    container.className = 'fixed top-4 right-4 z-50 space-y-3 pointer-events-none'; // Avoid clicking through
    document.body.appendChild(container);

    messages.forEach(msg => {
        // Extract content and type
        const text = msg.innerText;
        const isError = msg.classList.contains('bg-red-100');
        
        // Hide original
        msg.style.display = 'none';
        
        // Create new toast
        const toast = document.createElement('div');
        toast.className = `transform transition-all duration-300 translate-x-full opacity-0 pointer-events-auto flex items-center p-4 rounded-lg shadow-lg min-w-[300px] text-white ${isError ? 'bg-red-600' : 'bg-green-600'}`;
        toast.innerHTML = `
            <div class="flex-1">${text}</div>
            <button class="ml-4 hover:opacity-75 focus:outline-none" onclick="this.parentElement.remove()">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
        });
        
        // Auto remove
        setTimeout(() => {
            toast.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    });
}

// Table Search
function initTableSearch() {
    const table = document.querySelector('table');
    if (!table) return;

    // Create Search Bar
    const container = table.closest('.overflow-x-auto').parentElement;
    const header = container.querySelector('.flex.justify-between');
    if (!header) return;

    const searchWrapper = document.createElement('div');
    searchWrapper.className = 'relative text-gray-400 focus-within:text-gray-600 flex items-center';
    searchWrapper.innerHTML = `
        <svg class="w-5 h-5 absolute left-3 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input type="text" placeholder="Search..." class="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none transition-all w-64 text-sm">
    `;
    
    // Insert before the "New" button if possible, or append
    const btn = header.querySelector('a');
    if(btn) {
        header.insertBefore(searchWrapper, btn);
        searchWrapper.classList.add('mr-4');
    } else {
        header.appendChild(searchWrapper);
    }

    const input = searchWrapper.querySelector('input');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    input.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        
        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            if (text.includes(term)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Check if no results
        let visible = rows.filter(r => r.style.display !== 'none').length;
        let noMsg = tbody.querySelector('.no-results');
        
        if (visible === 0) {
            if(!noMsg) {
                noMsg = document.createElement('tr');
                noMsg.className = 'no-results';
                noMsg.innerHTML = '<td colspan="100%" class="px-6 py-8 text-center text-gray-400">No matching records found.</td>';
                tbody.appendChild(noMsg);
            }
        } else if (noMsg) {
            noMsg.remove();
        }
    });
}

// Sidebar Toggle (Mobile)
function initSidebar() {
    // Check if on mobile
    if (window.innerWidth > 768) return; 
    // We can implement mobile menu toggle later if needed.
    // For now, let's add a collapse button
}

// Dynamic Price Calculator for Booking
function initBookingCalculator() {
    const checkIn = document.querySelector('[name="check_in_date"]');
    const checkOut = document.querySelector('[name="check_out_date"]');
    const roomSelect = document.querySelector('[name="room"]');
    
    if(!checkIn || !checkOut || !roomSelect) return;

    // Create display element
    const display = document.createElement('div');
    display.className = 'mt-4 p-4 bg-blue-50 text-blue-800 rounded-lg border border-blue-100 hidden';
    checkOut.closest('.grid').parentNode.appendChild(display);

    function updatePrice() {
        const start = new Date(checkIn.value);
        const end = new Date(checkOut.value);
        
        if(isNaN(start) || isNaN(end)) return;
        
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
        
        if(diffDays <= 0) {
            display.classList.add('hidden');
            return;
        }

        // Get Room Price (We need to parse it from the select option text or data attribute)
        // Since attributes aren't standard in Django's widget without customizing, 
        // we'll try to extract from option text "Room 101 ($100.00)"
        const option = roomSelect.options[roomSelect.selectedIndex];
        if(!option) return;
        
        const text = option.text;
        // Regex to find price: checks for $XXX.XX pattern
        const match = text.match(/\$(\d+(\.\d{1,2})?)/);
        
        if(match) {
            const price = parseFloat(match[1]);
            const total = price * diffDays;
            
            display.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="font-medium">Estimated Total (${diffDays} nights)</span>
                    <span class="text-xl font-bold">$${total.toFixed(2)}</span>
                </div>
            `;
            display.classList.remove('hidden');
        }
    }

    checkIn.addEventListener('change', updatePrice);
    checkOut.addEventListener('change', updatePrice);
    roomSelect.addEventListener('change', updatePrice);
}
