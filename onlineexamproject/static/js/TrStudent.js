// Highlight active menu item
const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item => {
    const li = item.parentElement;
    item.addEventListener('click', function () {
        allSideMenu.forEach(i => {
            i.parentElement.classList.remove('active');
        });
        li.classList.add('active');
    });
});

// Sidebar toggle
function initializeSidebarToggle() {
    const menuBar = document.querySelector('#menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (menuBar && sidebar && content) {
        menuBar.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('collapsed');
        });
    }
}

// Call the function to initialize sidebar toggle
initializeSidebarToggle();

// Collapse sidebar by default on small screens
if (window.innerWidth < 768) {
    sidebar.classList.add('collapsed');
    document.getElementById('content').classList.add('collapsed');
}

// Section switching
function initializeSectionSwitching() {
    document.querySelectorAll('.side-menu a').forEach(link => {
        link.addEventListener('click', function (e) {
            if (this.closest('li').classList.contains('logout')) return;

            e.preventDefault();

            // Highlight active menu item
            document.querySelectorAll('.side-menu li').forEach(item => {
                item.classList.remove('active');
            });
            this.parentElement.classList.add('active');

            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });

            // Show the clicked section
            const target = this.getAttribute('data-target');
            if (target) {
                const targetSection = document.getElementById(target);
                if (targetSection) {
                    targetSection.style.display = 'block';

                    // Fetch results if the Exam Results Section is clicked
                    if (target === 'exam-results-section') {
                        fetchResults();
                    }
                    const sectionName = this.querySelector('.text').textContent.trim();
                    document.getElementById('breadcrumb-active').textContent = sectionName;
                }
            }
        });
    });
}

// Fetch and display results in the Exam Results Section
function fetchResults() {
    fetch('/api/results') // Replace with your actual API endpoint
        .then(response => response.json())
        .then(data => {
            const resultsTableBody = document.querySelector('#results-table tbody');
            resultsTableBody.innerHTML = ''; // Clear existing rows

            if (data.results && data.results.length > 0) {
                data.results.forEach(result => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><img src="/static/Profiles/${result.link}" alt="${result.Name}" style="width: 150px; height: 100px;"></td>
                        <td>${result.Name}</td>
                        <td>${result.TotalMark}</td>
                        <td>${result.Grade}</td>
                        <td>${result.Date}</td>
                        <td>
                            ${result.Status === 'Pass' 
                                ? '<span class="badge badge-success">Pass</span>' 
                                : '<span class="badge badge-danger">Fail</span>'}
                        </td>
                    `;
                    resultsTableBody.appendChild(row);
                });
            } else {
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="6" class="text-center">No results available.</td>`;
                resultsTableBody.appendChild(row);
            }
        })
        .catch(error => {
            console.error('Error fetching results:', error);
        });
}

// Show default section on load
function showDefaultSection() {
    const defaultSection = document.querySelector('[data-target="exam-question-section"]');
    if (defaultSection) {
        defaultSection.click();
    }
}

// Initialize section switching
document.addEventListener('DOMContentLoaded', function () {
    initializeSectionSwitching();
    showDefaultSection();
});

// Sidebar navigation
document.querySelectorAll('.side-menu a').forEach(link => {
    link.addEventListener('click', function (e) {
        if (this.closest('li').classList.contains('logout')) return;

        // Allow the browser to follow the link
        const targetUrl = this.getAttribute('href');
        if (targetUrl) {
            window.location.href = targetUrl;
        }
    });
});

// Logout handling
const logoutLink = document.querySelector('.logout a');
if (logoutLink) {
    logoutLink.addEventListener('click', function (e) {
        e.preventDefault();
        window.location.href = this.getAttribute('href');
    });
}

// Question type change handling
document.getElementById('question_type').addEventListener('change', function () {
    const questionType = this.value;
    const mcqOptions = document.getElementById('mcq-options');
    if (questionType === 'MCQ') {
        mcqOptions.style.display = 'block';
    } else {
        mcqOptions.style.display = 'none';
    }
});
