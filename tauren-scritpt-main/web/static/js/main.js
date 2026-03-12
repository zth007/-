
let statusPollingInterval = null;
let currentEditAccountId = null;
let currentLogs = [];
let logSearchKeyword = '';
let logLevelFilter = 'all';
let currentTheme = localStorage.getItem('theme') || 'light';

// 主题切换功能
function initTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeToggleButton();
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeToggleButton();
    showToast(`${currentTheme === 'dark' ? '暗黑' : '亮色'}模式已启用`, 'success');
}

function updateThemeToggleButton() {
    const themeToggle = document.getElementById('theme-toggle');
    if (currentTheme === 'dark') {
        themeToggle.innerHTML = '<i class="fas fa-sun"></i> <span>亮色模式</span>';
    } else {
        themeToggle.innerHTML = '<i class="fas fa-moon"></i> <span>暗黑模式</span>';
    }
}

// Toast 提示功能
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    toast.innerHTML = `
        <i class="${icons[type] || icons.info}"></i>
        <div class="toast-content">${message}</div>
        <span class="toast-close">&times;</span>
    `;

    container.appendChild(toast);

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => closeToast(toast));

    if (duration > 0) {
        setTimeout(() => closeToast(toast), duration);
    }

    function closeToast(element) {
        element.classList.add('fade-out');
        setTimeout(() => {
            if (element.parentNode === container) {
                container.removeChild(element);
            }
        }, 300);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const addAccountBtn = document.getElementById('add-account-btn');
    const saveConfigBtn = document.getElementById('save-config-btn');
    const modal = document.getElementById('account-modal');
    const closeModalBtn = document.querySelector('.close-btn');
    const cancelModalBtn = document.getElementById('cancel-modal');
    const saveAccountBtn = document.getElementById('save-account');

    startBtn.addEventListener('click', startScript);
    stopBtn.addEventListener('click', stopScript);
    addAccountBtn.addEventListener('click', openAddAccountModal);
    saveConfigBtn.addEventListener('click', saveConfig);
    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);
    saveAccountBtn.addEventListener('click', saveAccount);

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    initSidebarNavigation();

    // 日志功能初始化
    const logSearchInput = document.getElementById('log-search');
    const logLevelSelect = document.getElementById('log-level-filter');
    const clearLogsBtn = document.getElementById('clear-logs-btn');
    
    logSearchInput.addEventListener('input', (e) => {
        logSearchKeyword = e.target.value.toLowerCase();
        updateLogs(currentLogs);
    });
    
    logLevelSelect.addEventListener('change', (e) => {
        logLevelFilter = e.target.value;
        updateLogs(currentLogs);
    });
    
    clearLogsBtn.addEventListener('click', clearLogs);

    // 主题切换初始化
    const themeToggle = document.getElementById('theme-toggle');
    initTheme();
    
    themeToggle.addEventListener('click', toggleTheme);

    fetchStatus();
    fetchAccounts();
    fetchConfig();
    statusPollingInterval = setInterval(fetchStatus, 2000);
    setInterval(fetchAccounts, 15000);
});

function initSidebarNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionId = this.getAttribute('data-section');
            const targetSection = document.getElementById(sectionId);
            
            if (targetSection) {
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    const navHelp = document.getElementById('nav-help');
    if (navHelp) {
        navHelp.addEventListener('click', function(e) {
            e.preventDefault();
            alert('帮助文档\n\n功能说明：\n1. 控制面板 - 查看运行状态和控制脚本\n2. 账号管理 - 添加、编辑、删除账号\n3. 系统配置 - 修改脚本运行参数\n4. 运行日志 - 查看实时日志\n5. 数据统计 - 查看操作统计数据\n\n如有问题，请查看项目README文档。');
        });
    }

    const sections = document.querySelectorAll('section[id]');
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.getAttribute('id');
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('data-section') === sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));
}

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('获取状态失败:', error);
    }
}

async function fetchAccounts() {
    try {
        const response = await fetch('/api/accounts');
        const data = await response.json();
        updateAccounts(data);
    } catch (error) {
        console.error('获取账号列表失败:', error);
    }
}

function updateUI(data) {
    const statusIndicator = document.getElementById('status-indicator');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    if (data.running) {
        statusIndicator.innerHTML = '<i class="fas fa-play-circle"></i> 运行中';
        statusIndicator.className = 'status-indicator running';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusIndicator.innerHTML = '<i class="fas fa-power-off"></i> 已停止';
        statusIndicator.className = 'status-indicator stopped';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    document.getElementById('start-time').textContent = data.start_time || '-';
    document.getElementById('current-cycle').textContent = data.current_cycle;
    document.getElementById('total-cycles').textContent = data.total_cycles;

    document.getElementById('total-links').textContent = data.stats.total_links;
    document.getElementById('success-likes').textContent = data.stats.success_likes;
    document.getElementById('failed-likes').textContent = data.stats.failed_likes;

    const total = data.stats.success_likes + data.stats.failed_likes;
    const rate = total > 0 ? Math.round((data.stats.success_likes / total) * 100) : 0;
    document.getElementById('success-rate').textContent = rate + '%';

    updateLogs(data.logs);
}

function updateAccounts(data) {
    const container = document.getElementById('accounts-container');
    
    if (!data.accounts || data.accounts.length === 0) {
        container.innerHTML = '<p class="log-empty">暂无账号</p>';
        return;
    }

    const html = data.accounts.map(account => `
        <div class="account-item ${account.status}">
            <div class="account-name"><i class="fas fa-user"></i> ${account.name}</div>
            <div class="account-info"><i class="fas fa-info-circle"></i> 状态: ${account.status === 'active' ? '✅ 正常' : '⚠️ 风控'}</div>
            <div class="account-info"><i class="fas fa-cookie-bite"></i> Cookie: ${account.cookie_file}</div>
            <div class="account-info"><i class="fas fa-chart-bar"></i> 操作次数: ${account.operation_count || 0}</div>
            <div class="account-info"><i class="fas fa-clock"></i> 最后使用: ${account.last_used ? new Date(account.last_used).toLocaleString() : '-'}</div>
            <div class="account-actions">
                <button class="btn-edit" onclick="editAccount('${account.account_id}')"><i class="fas fa-edit"></i> 编辑</button>
                <button class="btn-delete" onclick="deleteAccount('${account.account_id}')"><i class="fas fa-trash"></i> 删除</button>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

function updateLogs(logs) {
    currentLogs = logs || [];
    const container = document.getElementById('logs-container');
    
    // 应用过滤条件
    let filteredLogs = currentLogs;
    
    if (logLevelFilter !== 'all') {
        filteredLogs = filteredLogs.filter(log => log.level === logLevelFilter);
    }
    
    if (logSearchKeyword) {
        filteredLogs = filteredLogs.filter(log => 
            log.message.toLowerCase().includes(logSearchKeyword) || 
            log.time.includes(logSearchKeyword)
        );
    }
    
    if (filteredLogs.length === 0) {
        container.innerHTML = '<p class="log-empty">暂无匹配的日志...</p>';
        return;
    }

    const html = filteredLogs.map(log => `
        <div class="log-entry">
            <span class="log-time">[${log.time}]</span>
            <span class="log-level ${log.level}">${log.level}</span>
            <span class="log-message">${log.message}</span>
        </div>
    `).join('');

    container.innerHTML = html;
    
    // 自动滚动到底部
    container.scrollTop = container.scrollHeight;
}

async function clearLogs() {
    if (!confirm('确定要清空所有日志吗？')) {
        return;
    }
    
    try {
        const response = await fetch('/api/logs/clear', {
            method: 'POST'
        });
        const result = await response.json();
        if (result.success) {
            currentLogs = [];
            updateLogs(currentLogs);
            showToast('日志已清空', 'success');
        } else {
            showToast('清空失败：' + result.message, 'error');
        }
    } catch (error) {
        console.error('清空日志失败:', error);
        // 即使API调用失败，也清空前端显示的日志
        currentLogs = [];
        updateLogs(currentLogs);
        showToast('日志已清空', 'success');
    }
}

function openAddAccountModal() {
    currentEditAccountId = null;
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-user-plus"></i> 添加账号';
    document.getElementById('account-name').value = '';
    document.getElementById('account-cookie').value = '';
    document.getElementById('account-enabled').checked = true;
    document.getElementById('account-modal').classList.add('show');
}

function editAccount(accountId) {
    fetch('/api/accounts')
        .then(res => res.json())
        .then(data => {
            const account = data.accounts.find(a => a.account_id === accountId);
            if (account) {
                currentEditAccountId = accountId;
                document.getElementById('modal-title').innerHTML = '<i class="fas fa-user-edit"></i> 编辑账号';
                document.getElementById('account-name').value = account.name;
                document.getElementById('account-cookie').value = account.cookie_file;
                document.getElementById('account-enabled').checked = account.status === 'active';
                document.getElementById('account-modal').classList.add('show');
            }
        });
}

function closeModal() {
    document.getElementById('account-modal').classList.remove('show');
    currentEditAccountId = null;
}

async function saveAccount() {
    const name = document.getElementById('account-name').value.trim();
    const cookieFile = document.getElementById('account-cookie').value.trim();
    const enabled = document.getElementById('account-enabled').checked;

    if (!name) {
        showToast('请输入账号名称', 'warning');
        return;
    }

    try {
        let response;
        if (currentEditAccountId) {
            response = await fetch(`/api/accounts/${currentEditAccountId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    cookie_file: cookieFile,
                    status: enabled ? 'active' : 'risk'
                })
            });
        } else {
            response = await fetch('/api/accounts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, cookie_file: cookieFile })
            });
        }

        const result = await response.json();
        if (result.success) {
            closeModal();
            fetchAccounts();
            showToast('账号保存成功', 'success');
        } else {
            showToast('操作失败', 'error');
        }
    } catch (error) {
        console.error('保存账号失败:', error);
        showToast('保存失败，请检查控制台', 'error');
    }
}

async function deleteAccount(accountId) {
    if (!confirm('确定要删除这个账号吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/accounts/${accountId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (result.success) {
            fetchAccounts();
            showToast('账号删除成功', 'success');
        } else {
            showToast('删除失败', 'error');
        }
    } catch (error) {
        console.error('删除账号失败:', error);
        showToast('删除失败，请检查控制台', 'error');
    }
}

async function startScript() {
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        if (result.success) {
            fetchStatus();
            showToast('脚本启动成功', 'success');
        } else {
            showToast(result.message, 'error');
        }
    } catch (error) {
        console.error('启动失败:', error);
        showToast('启动失败，请检查控制台', 'error');
    }
}

async function stopScript() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        if (result.success) {
            fetchStatus();
            showToast('脚本已停止', 'success');
        } else {
            showToast(result.message, 'error');
        }
    } catch (error) {
        console.error('停止失败:', error);
        showToast('停止失败，请检查控制台', 'error');
    }
}

async function fetchConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('config-min-delay').value = config.operation.min_delay || 2;
        document.getElementById('config-max-delay').value = config.operation.max_delay || 4;
        document.getElementById('config-max-retries').value = config.operation.max_retries || 2;
        document.getElementById('config-max-links').value = config.operation.max_links_per_cycle || 20;
        document.getElementById('config-like-rate').value = config.operation.like_rate || 100;
        document.getElementById('config-comment-rate').value = config.operation.comment_rate || 100;
        
        document.getElementById('config-headless').checked = config.operation.browser?.headless || false;
        document.getElementById('config-maximize').checked = config.operation.browser?.maximize !== false;
        document.getElementById('config-proxy-enabled').checked = config.operation.browser?.proxy_enabled || false;
        document.getElementById('config-proxy-pool').value = (config.operation.browser?.proxy_pool || []).join('\n');
        
        document.getElementById('config-max-cycles').value = config.operation.cycle?.max_cycles || 5;
        document.getElementById('config-cycle-interval').value = (config.operation.cycle?.cycle_interval || 3600) / 60;
        document.getElementById('config-users-per-cycle').value = config.operation.cycle?.users_per_cycle || 10;
        document.getElementById('config-videos-per-user').value = config.operation.cycle?.videos_per_user || 5;
        
        document.getElementById('config-log-level').value = config.logging?.level || 'INFO';
        document.getElementById('config-log-dir').value = config.logging?.log_dir || 'logs';

        updateCommentStatus(config.operation.comment_rate || 100);
    } catch (error) {
        console.error('获取配置失败:', error);
    }
}

function updateCommentStatus(commentRate) {
    const commentStatus = document.getElementById('comment-status');
    if (commentRate > 0) {
        commentStatus.innerHTML = `✅ 已启用 (${commentRate}% 概率)`;
        commentStatus.style.color = '#28a745';
    } else {
        commentStatus.innerHTML = '❌ 已禁用';
        commentStatus.style.color = '#dc3545';
    }
}

async function saveConfig() {
    try {
        const config = {
            operation: {
                min_delay: parseInt(document.getElementById('config-min-delay').value),
                max_delay: parseInt(document.getElementById('config-max-delay').value),
                max_retries: parseInt(document.getElementById('config-max-retries').value),
                max_links_per_cycle: parseInt(document.getElementById('config-max-links').value),
                like_rate: parseInt(document.getElementById('config-like-rate').value),
                comment_rate: parseInt(document.getElementById('config-comment-rate').value),
                browser: {
                    headless: document.getElementById('config-headless').checked,
                    maximize: document.getElementById('config-maximize').checked,
                    proxy_enabled: document.getElementById('config-proxy-enabled').checked,
                    proxy_pool: document.getElementById('config-proxy-pool').value.split('\n').filter(p => p.trim())
                },
                cycle: {
                    max_cycles: parseInt(document.getElementById('config-max-cycles').value),
                    cycle_interval: parseInt(document.getElementById('config-cycle-interval').value) * 60,
                    users_per_cycle: parseInt(document.getElementById('config-users-per-cycle').value),
                    videos_per_user: parseInt(document.getElementById('config-videos-per-user').value)
                }
            },
            logging: {
                level: document.getElementById('config-log-level').value,
                log_dir: document.getElementById('config-log-dir').value
            }
        };

        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        const result = await response.json();
        if (result.success) {
            updateCommentStatus(config.operation.comment_rate);
            showToast('配置保存成功！已实时生效', 'success');
        } else {
            showToast('配置保存失败：' + result.message, 'error');
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存失败，请检查控制台');
    }
}
