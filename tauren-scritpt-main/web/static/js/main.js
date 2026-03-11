
let statusPollingInterval = null;
let currentEditAccountId = null;

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

    fetchStatus();
    fetchAccounts();
    fetchConfig();
    statusPollingInterval = setInterval(fetchStatus, 2000);
    setInterval(fetchAccounts, 15000);
});

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
        statusIndicator.textContent = '运行中';
        statusIndicator.className = 'status-indicator running';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusIndicator.textContent = '已停止';
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
            <div class="account-name">${account.name}</div>
            <div class="account-info">状态: ${account.status === 'active' ? '✅ 正常' : '⚠️ 风控'}</div>
            <div class="account-info">Cookie: ${account.cookie_file}</div>
            <div class="account-info">操作次数: ${account.operation_count || 0}</div>
            <div class="account-info">最后使用: ${account.last_used ? new Date(account.last_used).toLocaleString() : '-'}</div>
            <div class="account-actions">
                <button class="btn-edit" onclick="editAccount('${account.account_id}')">编辑</button>
                <button class="btn-delete" onclick="deleteAccount('${account.account_id}')">删除</button>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

function updateLogs(logs) {
    const container = document.getElementById('logs-container');
    
    if (logs.length === 0) {
        container.innerHTML = '<p class="log-empty">暂无日志...</p>';
        return;
    }

    const html = logs.map(log => `
        <div class="log-entry">
            <span class="log-time">[${log.time}]</span>
            <span class="log-level ${log.level}">${log.level}</span>
            <span class="log-message">${log.message}</span>
        </div>
    `).join('');

    container.innerHTML = html;
}

function openAddAccountModal() {
    currentEditAccountId = null;
    document.getElementById('modal-title').textContent = '添加账号';
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
                document.getElementById('modal-title').textContent = '编辑账号';
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
        alert('请输入账号名称');
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
        } else {
            alert('操作失败');
        }
    } catch (error) {
        console.error('保存账号失败:', error);
        alert('保存失败，请检查控制台');
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
        } else {
            alert('删除失败');
        }
    } catch (error) {
        console.error('删除账号失败:', error);
        alert('删除失败，请检查控制台');
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
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('启动失败:', error);
        alert('启动失败，请检查控制台');
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
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('停止失败:', error);
        alert('停止失败，请检查控制台');
    }
}

async function fetchConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // 填充配置表单
        document.getElementById('config-min-delay').value = config.operation.min_delay || 2;
        document.getElementById('config-max-delay').value = config.operation.max_delay || 4;
        document.getElementById('config-max-retries').value = config.operation.max_retries || 2;
        document.getElementById('config-max-links').value = config.operation.max_links_per_cycle || 20;
        
        document.getElementById('config-headless').checked = config.operation.browser?.headless || false;
        document.getElementById('config-maximize').checked = config.operation.browser?.maximize !== false;
        
        document.getElementById('config-max-cycles').value = config.operation.cycle?.max_cycles || 5;
        document.getElementById('config-cycle-interval').value = (config.operation.cycle?.cycle_interval || 3600) / 60;
        document.getElementById('config-users-per-cycle').value = config.operation.cycle?.users_per_cycle || 10;
        document.getElementById('config-videos-per-user').value = config.operation.cycle?.videos_per_user || 5;
        
        document.getElementById('config-log-level').value = config.logging?.level || 'INFO';
        document.getElementById('config-log-dir').value = config.logging?.log_dir || 'logs';
    } catch (error) {
        console.error('获取配置失败:', error);
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
                browser: {
                    headless: document.getElementById('config-headless').checked,
                    maximize: document.getElementById('config-maximize').checked
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
            alert('配置保存成功！重启脚本后生效');
        } else {
            alert('配置保存失败：' + result.message);
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存失败，请检查控制台');
    }
}

