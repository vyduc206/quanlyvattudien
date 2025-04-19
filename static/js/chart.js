/**
 * Xử lý vẽ biểu đồ cho báo cáo
 */

// Vẽ biểu đồ thống kê tồn kho
function drawInventoryChart(elementId, products, categories) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Chuẩn bị dữ liệu
    const productData = [];
    const backgroundColors = [];
    const borderColors = [];
    
    // Danh sách màu
    const colors = [
        ['rgba(255, 99, 132, 0.2)', 'rgba(255, 99, 132, 1)'],
        ['rgba(54, 162, 235, 0.2)', 'rgba(54, 162, 235, 1)'],
        ['rgba(255, 206, 86, 0.2)', 'rgba(255, 206, 86, 1)'],
        ['rgba(75, 192, 192, 0.2)', 'rgba(75, 192, 192, 1)'],
        ['rgba(153, 102, 255, 0.2)', 'rgba(153, 102, 255, 1)'],
        ['rgba(255, 159, 64, 0.2)', 'rgba(255, 159, 64, 1)'],
        ['rgba(199, 199, 199, 0.2)', 'rgba(199, 199, 199, 1)'],
        ['rgba(83, 102, 255, 0.2)', 'rgba(83, 102, 255, 1)'],
        ['rgba(40, 159, 64, 0.2)', 'rgba(40, 159, 64, 1)'],
        ['rgba(210, 199, 199, 0.2)', 'rgba(210, 199, 199, 1)']
    ];
    
    for (let i = 0; i < products.length && i < 30; i++) {
        productData.push({
            name: products[i].name.length > 20 ? products[i].name.substring(0, 20) + '...' : products[i].name,
            quantity: products[i].quantity,
            category: products[i].category
        });
        
        const colorIndex = i % colors.length;
        backgroundColors.push(colors[colorIndex][0]);
        borderColors.push(colors[colorIndex][1]);
    }
    
    // Vẽ biểu đồ cột
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: productData.map(p => p.name),
            datasets: [{
                label: 'Số lượng tồn kho',
                data: productData.map(p => p.quantity),
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số lượng'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Sản phẩm'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Thống kê tồn kho theo sản phẩm',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Số lượng: ${context.raw}`;
                        },
                        afterLabel: function(context) {
                            const dataIndex = context.dataIndex;
                            return `Danh mục: ${productData[dataIndex].category || 'Chưa phân loại'}`;
                        }
                    }
                }
            }
        }
    });
    
    return chart;
}

// Vẽ biểu đồ thống kê tồn kho theo danh mục
function drawCategoryChart(elementId, categories) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Chuẩn bị dữ liệu
    const categoryNames = categories.map(c => c.name);
    const categoryCounts = categories.map(c => c.count);
    
    const backgroundColors = [
        'rgba(255, 99, 132, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(199, 199, 199, 0.2)',
        'rgba(83, 102, 255, 0.2)'
    ];
    
    const borderColors = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(199, 199, 199, 1)',
        'rgba(83, 102, 255, 1)'
    ];
    
    // Vẽ biểu đồ tròn
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categoryNames,
            datasets: [{
                data: categoryCounts,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Phân bố sản phẩm theo danh mục',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                },
                legend: {
                    position: 'right'
                }
            }
        }
    });
    
    return chart;
}

// Vẽ biểu đồ thống kê nhập xuất theo thời gian
function drawTransactionChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Vẽ biểu đồ đường
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Nhập kho',
                    data: data.import,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1,
                    fill: true
                },
                {
                    label: 'Xuất kho',
                    data: data.export,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số lượng'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Thời gian'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Thống kê nhập xuất kho theo thời gian',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            interaction: {
                mode: 'nearest',
                intersect: false
            }
        }
    });
    
    return chart;
}

// Vẽ biểu đồ thống kê tài chính
function drawFinancialChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Vẽ biểu đồ cột kết hợp
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Giá trị nhập kho',
                    data: data.import,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    order: 2
                },
                {
                    label: 'Giá trị xuất kho',
                    data: data.export,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    order: 1
                },
                {
                    label: 'Chênh lệch',
                    data: data.difference,
                    type: 'line',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    order: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Giá trị (VNĐ)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Thời gian'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Thống kê giá trị nhập xuất kho',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                intersect: false
            }
        }
    });
    
    return chart;
}
