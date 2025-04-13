// Loader Animation
function animateLoader() {
    const loader = document.getElementById('loader');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    if (!loader || !progressBar || !progressText) return;

    let progress = 10;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            setTimeout(() => {
                loader.style.opacity = '0';
                setTimeout(() => {
                    loader.style.display = 'none';
                }, 300);
            }, 400);
        }
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${Math.round(progress)}%`;
    }, 150);
}

if (document.getElementById('loader')) {
    animateLoader();
}

// Dropdown Handling
document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        const menu = toggle.nextElementSibling;
        const isOpen = !menu.classList.contains('hidden');
        // Close all dropdowns
        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.add('hidden'));
        // Toggle current dropdown
        if (!isOpen) {
            menu.classList.remove('hidden');
        }
    });
});

// Close dropdowns on outside click
document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => menu.classList.add('hidden'));
    }
});

// Form Submission with Loader
document.querySelectorAll('input, .dropdown-menu button').forEach(input => {
    input.addEventListener('click', (e) => {
        if (e.target.type === 'submit') {
            const loader = document.getElementById('loader');
            if (loader) {
                loader.style.display = 'flex';
                loader.style.opacity = '1';
                document.getElementById('progress-bar').style.width = '10%';
                document.getElementById('progress-text').textContent = '10%';
                animateLoader();
            }
        }
    });
});

// Export Button Loader
document.getElementById('export-btn')?.addEventListener('click', () => {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'flex';
        loader.style.opacity = '1';
        document.getElementById('progress-bar').style.width = '10%';
        document.getElementById('progress-text').textContent = '10%';
        animateLoader();
    }
});

// Tab Switching
function switchTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.classList.remove(`border-${themeClasses[document.body.dataset.theme].accent.replace('text-', '')}`);
    });
    const activeBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    activeBtn.classList.add('active');
    activeBtn.classList.add(`border-${themeClasses[document.body.dataset.theme].accent.replace('text-', '')}`);

    // Fade out current content
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => {
        content.style.opacity = '0';
        content.style.transition = 'opacity 0.3s ease';
        setTimeout(() => {
            content.classList.add('hidden');
            content.style.opacity = '1'; // Reset for next fade-in
        }, 300);
    });

    // Show new content
    const activeContent = document.getElementById(tabId);
    setTimeout(() => {
        activeContent.classList.remove('hidden');
        activeContent.style.opacity = '0';
        setTimeout(() => {
            activeContent.style.opacity = '1';
        }, 10);
        initCharts(tabId); // Initialize charts for active tab
    }, 300);
}

document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        switchTab(button.dataset.tab);
    });
});

// Chart Initialization
let charts = {};
function initCharts(tabId) {
    const theme = document.body.dataset.theme || 'black';
    const colors = {
        backgroundColor: themeClasses[theme].chart_bg,
        textColor: themeClasses[theme].chart_text,
        accentColor: themeClasses[theme].chart_accent,
        secondaryColors: [
            themeClasses[theme].chart_accent + 'CC', // 80% opacity
            '#6b7280CC',
            '#9ca3afCC',
            '#d1d5dbCC',
            '#e5e7ebCC'
        ]
    };

    // Destroy existing charts for this tab to prevent duplicates
    if (charts[tabId]) {
        Object.values(charts[tabId]).forEach(chart => {
            if (chart instanceof Chart) chart.destroy();
            else if (chart instanceof ApexCharts) chart.destroy();
        });
    }
    charts[tabId] = {};

    // Chart.js Charts
    if (tabId === 'tracks' && chartData.tracks && chartData.tracks.labels.length) {
        charts[tabId].tracks = new Chart(document.getElementById('tracks-chart'), {
            type: 'bar',
            data: {
                labels: chartData.tracks.labels,
                datasets: [{
                    label: 'Playcount',
                    data: chartData.tracks.data,
                    backgroundColor: colors.accentColor + '99', // 60% opacity
                    borderColor: colors.accentColor,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart',
                    x: { from: 0 },
                    y: { from: 100 }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: colors.backgroundColor,
                        titleColor: colors.textColor,
                        bodyColor: colors.textColor,
                        callbacks: {
                            title: ctx => chartData.tracks.labels[ctx[0].dataIndex],
                            label: ctx => `Plays: ${ctx.raw} | Artist: ${chartData.tracks.artists[ctx.dataIndex]}`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: colors.textColor, maxRotation: 45, minRotation: 45 },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: colors.textColor },
                        grid: { color: colors.textColor + '33' } // 20% opacity
                    }
                }
            }
        });
    }

    if (tabId === 'tracks' && chartData.recent && chartData.recent.labels.length) {
        charts[tabId].recent = new Chart(document.getElementById('recent-chart'), {
            type: 'doughnut',
            data: {
                labels: chartData.recent.labels,
                datasets: [{
                    data: chartData.recent.data,
                    backgroundColor: colors.secondaryColors,
                    borderColor: colors.backgroundColor,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuad',
                    animateRotate: true,
                    animateScale: true
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: colors.textColor }
                    },
                    tooltip: {
                        backgroundColor: colors.backgroundColor,
                        titleColor: colors.textColor,
                        bodyColor: colors.textColor
                    }
                }
            }
        });
    }

    if (tabId === 'albums' && chartData.albums && chartData.albums.labels.length) {
        charts[tabId].albums = new Chart(document.getElementById('albums-chart'), {
            type: 'bar',
            data: {
                labels: chartData.albums.labels,
                datasets: [{
                    label: 'Playcount',
                    data: chartData.albums.data,
                    backgroundColor: colors.accentColor + '99',
                    borderColor: colors.accentColor,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart',
                    x: { from: 0 },
                    y: { from: 100 }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: colors.backgroundColor,
                        titleColor: colors.textColor,
                        bodyColor: colors.textColor,
                        callbacks: {
                            title: ctx => chartData.albums.labels[ctx[0].dataIndex],
                            label: ctx => `Plays: ${ctx.raw} | Artist: ${chartData.albums.artists[ctx.dataIndex]}`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: colors.textColor, maxRotation: 45, minRotation: 45 },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: colors.textColor },
                        grid: { color: colors.textColor + '33' }
                    }
                }
            }
        });
    }

    if (tabId === 'artists' && chartData.artists && chartData.artists.labels.length) {
        charts[tabId].artists = new Chart(document.getElementById('artists-chart'), {
            type: 'bar',
            data: {
                labels: chartData.artists.labels,
                datasets: [{
                    label: 'Playcount',
                    data: chartData.artists.data,
                    backgroundColor: colors.accentColor + '99',
                    borderColor: colors.accentColor,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart',
                    x: { from: 0 },
                    y: { from: 100 }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: colors.backgroundColor,
                        titleColor: colors.textColor,
                        bodyColor: colors.textColor,
                        callbacks: {
                            title: ctx => chartData.artists.labels[ctx[0].dataIndex],
                            label: ctx => `Plays: ${ctx.raw}`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: colors.textColor, maxRotation: 45, minRotation: 45 },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: colors.textColor },
                        grid: { color: colors.textColor + '33' }
                    }
                }
            }
        });
    }

    // ApexCharts
    if (tabId === 'home' && chartData.decades && chartData.decades.labels.length) {
        charts[tabId].decades = new ApexCharts(document.querySelector('#decades-chart'), {
            series: chartData.decades.data,
            chart: {
                type: 'donut',
                height: '100%',
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    animateGradually: { enabled: true, delay: 150 }
                },
                background: 'transparent'
            },
            labels: chartData.decades.labels,
            colors: colors.secondaryColors,
            fill: { opacity: 0.9 },
            stroke: { width: 0 },
            dataLabels: {
                style: { colors: [colors.textColor] },
                dropShadow: { enabled: false }
            },
            legend: {
                position: 'bottom',
                labels: { colors: colors.textColor },
                markers: { width: 10, height: 10 }
            },
            plotOptions: {
                pie: {
                    donut: {
                        size: '65%',
                        labels: {
                            show: true,
                            total: {
                                show: true,
                                color: colors.textColor,
                                fontSize: '14px'
                            }
                        }
                    }
                }
            },
            responsive: [{
                breakpoint: 640,
                options: {
                    chart: { height: 180 },
                    legend: { position: 'bottom' }
                }
            }]
        });
        charts[tabId].decades.render();
    }

    if (tabId === 'home' && chartData.heatmap && chartData.heatmap.plays.length) {
        charts[tabId].heatmap = new ApexCharts(document.querySelector('#heatmap-chart'), {
            series: [{
                name: 'Plays',
                data: chartData.heatmap.plays.map((play, i) => ({
                    x: chartData.heatmap.hours[i],
                    y: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(chartData.heatmap.days[i]),
                    z: play * 5 // Scale bubble size
                }))
            }],
            chart: {
                type: 'bubble',
                height: '100%',
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    animateGradually: { enabled: true, delay: 150 }
                },
                background: 'transparent'
            },
            colors: [colors.accentColor],
            fill: { opacity: 0.7 },
            dataLabels: { enabled: false },
            xaxis: {
                title: { text: 'Hour', style: { color: colors.textColor, fontSize: '12px' } },
                labels: { style: { colors: colors.textColor, fontSize: '10px' } },
                min: 0,
                max: 23
            },
            yaxis: {
                title: { text: 'Day', style: { color: colors.textColor, fontSize: '12px' } },
                labels: {
                    formatter: val => ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][val],
                    style: { colors: colors.textColor, fontSize: '10px' }
                },
                min: 0,
                max: 6
            },
            tooltip: {
                theme: theme === 'light' ? 'light' : 'dark',
                style: { fontSize: '10px' },
                x: { formatter: val => `${val}:00` },
                y: { formatter: val => ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][val] },
                z: { formatter: val => `${Math.round(val / 5)} plays` }
            },
            responsive: [{
                breakpoint: 640,
                options: { chart: { height: 180 } }
            }]
        });
        charts[tabId].heatmap.render();
    }

    if (tabId === 'leaderboard' && chartData.friends && chartData.friends.users.length) {
        charts[tabId].friends = new ApexCharts(document.querySelector('#friends-chart'), {
            series: [
                { name: 'Tracks', data: chartData.friends.tracks },
                { name: 'Albums', data: chartData.friends.albums },
                { name: 'Artists', data: chartData.friends.artists }
            ],
            chart: {
                type: 'bar',
                height: '100%',
                stacked: false,
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    animateGradually: { enabled: true, delay: 150 }
                },
                background: 'transparent'
            },
            colors: [colors.accentColor, colors.secondaryColors[1], colors.secondaryColors[2]],
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '30%',
                    borderRadius: 4
                }
            },
            dataLabels: { enabled: false },
            stroke: { show: true, width: 2, colors: ['transparent'] },
            xaxis: {
                categories: chartData.friends.users,
                labels: { style: { colors: colors.textColor, fontSize: '10px' } }
            },
            yaxis: {
                title: { text: 'Scrobbles', style: { color: colors.textColor, fontSize: '12px' } },
                labels: { style: { colors: colors.textColor, fontSize: '10px' } }
            },
            legend: {
                position: 'bottom',
                labels: { colors: colors.textColor },
                markers: { width: 10, height: 10 }
            },
            tooltip: {
                theme: theme === 'light' ? 'light' : 'dark',
                y: { formatter: val => `${val} scrobbles` }
            },
            responsive: [{
                breakpoint: 640,
                options: {
                    chart: { height: 180 },
                    plotOptions: { bar: { columnWidth: '40%' } }
                }
            }]
        });
        charts[tabId].friends.render();
    }

    if (tabId === 'leaderboard' && chartData.world && chartData.world.entities.length) {
        charts[tabId].world = new ApexCharts(document.querySelector('#world-chart'), {
            series: [{
                data: chartData.world.entities.map((entity, i) => ({
                    x: entity,
                    y: chartData.world.total[i]
                }))
            }],
            chart: {
                type: 'treemap',
                height: '100%',
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    animateGradually: { enabled: true, delay: 150 }
                },
                background: 'transparent'
            },
            colors: [colors.accentColor],
            dataLabels: {
                enabled: true,
                style: { fontSize: '10px', colors: [colors.textColor] }
            },
            tooltip: {
                theme: theme === 'light' ? 'light' : 'dark',
                y: { formatter: val => `${val} scrobbles` }
            },
            responsive: [{
                breakpoint: 640,
                options: { chart: { height: 180 } }
            }]
        });
        charts[tabId].world.render();
    }

    if (tabId === 'leaderboard' && chartData.past && chartData.past.periods.length) {
        charts[tabId].past = new ApexCharts(document.querySelector('#past-chart'), {
            series: [
                { name: 'Tracks', data: chartData.past.tracks },
                { name: 'Albums', data: chartData.past.albums },
                { name: 'Artists', data: chartData.past.artists }
            ],
            chart: {
                type: 'line',
                height: '100%',
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800,
                    animateGradually: { enabled: true, delay: 150 }
                },
                background: 'transparent',
                zoom: { enabled: false }
            },
            colors: [colors.accentColor, colors.secondaryColors[1], colors.secondaryColors[2]],
            stroke: { curve: 'smooth', width: 3 },
            markers: { size: 5 },
            xaxis: {
                categories: chartData.past.periods,
                labels: { style: { colors: colors.textColor, fontSize: '10px' } }
            },
            yaxis: {
                title: { text: 'Scrobbles', style: { color: colors.textColor, fontSize: '12px' } },
                labels: { style: { colors: colors.textColor, fontSize: '10px' } }
            },
            legend: {
                position: 'bottom',
                labels: { colors: colors.textColor },
                markers: { width: 10, height: 10 }
            },
            tooltip: {
                theme: theme === 'light' ? 'light' : 'dark',
                y: { formatter: val => `${val} scrobbles` }
            },
            responsive: [{
                breakpoint: 640,
                options: { chart: { height: 180 } }
            }]
        });
        charts[tabId].past.render();
    }
}

// Initialize default tab
switchTab('home');