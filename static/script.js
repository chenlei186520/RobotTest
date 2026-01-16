// 全局变量
let currentTestId = null;
let isTesting = false;
let testResults = {}; // 存储每个测试项的结果
let testerName = '张三'; // 测试人员名称，默认张三
let lightTestItemIds = new Set(); // 记录已发送关闭所有灯指令的灯光测试项ID，避免重复发送
let testStartTime = null; // 测试开始时间戳（点击"开始测试"时记录）

// 自定义弹窗函数
function showModal(title, message, onConfirm, linkUrl) {
    const modal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalLinkContainer = document.getElementById('modalLinkContainer');
    const modalLink = document.getElementById('modalLink');
    const confirmBtn = document.getElementById('modalConfirmBtn');
    
    modalTitle.textContent = title || '提示';
    // 支持HTML内容
    if (message && message.includes('<')) {
        modalMessage.innerHTML = message;
    } else {
        modalMessage.textContent = message;
    }
    
    // 如果有链接URL，显示链接图标
    if (linkUrl) {
        modalLink.href = linkUrl;
        modalLinkContainer.style.display = 'flex';
    } else {
        modalLinkContainer.style.display = 'none';
    }
    
    modal.classList.add('show');
    
    // 显示确定按钮
    confirmBtn.style.display = 'block';
    
    // 绑定确定按钮事件
    confirmBtn.onclick = function() {
        modal.classList.remove('show');
        // 如果提供了回调函数，执行它
        if (onConfirm && typeof onConfirm === 'function') {
            onConfirm();
        }
    };
    
    // 点击遮罩层关闭
    const overlay = modal.querySelector('.modal-overlay');
    overlay.onclick = function() {
        modal.classList.remove('show');
        // 如果提供了回调函数，执行它
        if (onConfirm && typeof onConfirm === 'function') {
            onConfirm();
        }
    };
}

// 显示Loading弹窗
function showLoadingModal(message) {
    const modal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const confirmBtn = document.getElementById('modalConfirmBtn');
    
    modalTitle.textContent = '检测中';
    // 创建Loading内容
    modalMessage.innerHTML = `
        <div style="text-align: center;">
            <div class="loading-spinner" style="display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px; vertical-align: middle;"></div>
            <span style="vertical-align: middle;">${message || '检测车辆ID中，请稍后...'}</span>
        </div>
    `;
    modal.classList.add('show');
    
    // 隐藏确定按钮（Loading时不能点击）
    confirmBtn.style.display = 'none';
    
    // 禁用遮罩层点击关闭
    const overlay = modal.querySelector('.modal-overlay');
    overlay.onclick = null;
}

// 添加Loading动画样式
if (!document.getElementById('loadingStyle')) {
    const style = document.createElement('style');
    style.id = 'loadingStyle';
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}
let appConfig = {
    ioCheckTimeout: 30000,  // 默认30秒
    ioCheckInterval: 500,   // 默认500ms
    commandWaitTime: 1000   // 默认1秒
};

// 存储系统信息
let systemInfo = {
    PRODUCT_NAME: '',
    PRODUCT_NAME_EXTERNAL: '',
    HOSTNAME: '',
    APP_VERSION: ''
};

// 从URL获取SSH连接信息
function getSSHInfo() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        ssh_host: urlParams.get('carip') || '',
        ssh_user: urlParams.get('ssh_user') || ''
    };
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 绑定返回测试配置面按钮
    const backToConfigBtn = document.getElementById('backToConfigBtn');
    if (backToConfigBtn) {
        backToConfigBtn.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
    
    // 绑定导航项点击事件
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // 获取测试ID
            const testId = this.getAttribute('data-test-id');
            
            // 如果是测试报告
            if (testId === 'test_report') {
                // 如果正在测试中，禁止手动跳转到测试报告
                if (isTesting) {
                    showModal('提示', '测试进行中，请完成所有测试后自动跳转到测试报告');
                    return;
                }
                
                // 测试未进行时，允许切换并重置按钮
                // 移除所有活动状态
                navItems.forEach(nav => nav.classList.remove('active'));
                // 添加当前活动状态
                this.classList.add('active');
                
                currentTestId = testId;
                loadTestReport();
                // loadTestReport()内部会调用resetStartTestButton(false)，不清空测试时间
                return;
            }
            
            // 其他TAB：如果正在测试中，阻止切换
            if (isTesting) {
                showModal('提示', '测试进行中，请勿切换页面');
                return;
            }
            
            // 移除所有活动状态
            navItems.forEach(nav => nav.classList.remove('active'));
            // 添加当前活动状态
            this.classList.add('active');
            
            currentTestId = testId;
            
            // 如果切换到其他tab，断开相机测试的SSH连接
            if (currentTestId !== 'camera' && window.cameraSSHConnected) {
                disconnectCameraSSH();
            }
            
            loadTestDetails(testId);
            
            // 如果是相机测试，建立SSH连接
            if (testId === 'camera') {
                connectCameraSSH();
            }
            // 如果是按键测试，显示提示弹窗
            else if (testId === 'button') {
                showModal('提示', '测试前请检查按钮为"抬起"状态');
            }
            // 如果是显示屏测试，显示提示弹窗
            else if (testId === 'display') {
                setTimeout(() => {
                    showModal('提示', '<span style="color: #ffffff;">请点击屏幕四角和中心点，判断屏幕点击是否正常/异常</span>');
                }, 500);
            }
            
            // 重置开始测试按钮
            resetStartTestButton();
        });
    });
    
    // 绑定弹窗确定按钮（页面加载时）
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener('click', function() {
            const modal = document.getElementById('customModal');
            modal.classList.remove('show');
        });
    }

    // 绑定开始测试按钮
    const startTestBtn = document.querySelector('.start-test-btn');
    startTestBtn.addEventListener('click', function() {
        if (isTesting) {
            return;
        }
        startTest();
    });
    
    // 绑定下载报告按钮
    const downloadReportBtn = document.getElementById('downloadReportBtn');
    if (downloadReportBtn) {
        downloadReportBtn.addEventListener('click', function() {
            downloadTestReport();
        });
    }
    
    // 绑定云端同步按钮
    const cloudSyncBtn = document.getElementById('cloudSyncBtn');
    if (cloudSyncBtn) {
        cloudSyncBtn.addEventListener('click', function() {
            uploadToCloud();
        });
    }

    // 加载配置
    loadConfig();
    
    // 获取系统信息并对比hostname
    loadSystemInfo();
    
    // 加载初始测试详情
    const firstTestId = navItems[0].getAttribute('data-test-id');
    currentTestId = firstTestId;
    loadTestDetails(firstTestId);
    
    // 如果初始TAB是按键测试，显示提示弹窗
    if (firstTestId === 'button') {
        setTimeout(() => {
            showModal('提示', '测试前请检查按钮为"抬起"状态');
        }, 500);
    }
    // 如果初始TAB是显示屏测试，显示提示弹窗
    else if (firstTestId === 'display') {
        setTimeout(() => {
            showModal('提示', '<span style="color: #ffffff;">请点击屏幕四角和中心点，判断屏幕点击是否正常/异常</span>');
        }, 500);
    }
    
    // 初始化测试结果
    initTestResults();
    
    // 绑定模板中已有的灯光测试按钮事件
    bindTemplateLightButtons();
    
    // 页面卸载时断开相机测试的SSH连接
    window.addEventListener('beforeunload', function() {
        if (window.cameraSSHConnected) {
            disconnectCameraSSH();
        }
    });
});

// 加载配置
function loadConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            appConfig.ioCheckTimeout = data.io_check_timeout * 1000; // 转换为毫秒
            appConfig.ioCheckInterval = data.io_check_interval;
            appConfig.commandWaitTime = data.command_wait_time;
        })
        .catch(error => {
            console.error('加载配置失败:', error);
            // 使用默认值
        });
}

// 加载系统信息
function loadSystemInfo() {
    const sshInfo = getSSHInfo();
    
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search);
    const showSuccess = urlParams.get('showSuccess');
    const hostnameDetected = urlParams.get('hostnameDetected');
    
    // 如果URL中有showSuccess=1参数，说明是从页面A检测成功跳转过来的，先显示成功提示
    if (showSuccess === '1' && hostnameDetected) {
        const message = `车型匹配成功，请开始测试\n获取到的HOSTNAME: ${hostnameDetected}`;
        showModal('提示', message);
        // 注意：这里不return，继续执行下面的代码以获取系统信息（包括APP_VERSION）
    }
    
    // 如果没有SSH主机地址，跳过
    if (!sshInfo.ssh_host) {
        console.log('未提供SSH主机地址，跳过系统信息获取');
        return;
    }
    
    // 只有在没有showSuccess参数时才显示Loading提示（避免重复弹窗）
    if (showSuccess !== '1') {
        showLoadingModal('检测车辆ID中，请稍后...');
    }
    
    // 获取URL中的hostname参数
    const urlHostname = urlParams.get('hostname') || '';
    
    fetch('/api/get_system_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ssh_host: sshInfo.ssh_host,
            ssh_user: sshInfo.ssh_user
        })
    })
    .then(response => response.json())
    .then(data => {
        // 隐藏Loading弹窗（如果显示了的话）
        if (showSuccess !== '1') {
            const modal = document.getElementById('customModal');
            modal.classList.remove('show');
        }
        
        if (data.status === 'success') {
            // 存储系统信息（包括APP_VERSION）
            systemInfo = data.data;
            console.log('[系统信息] 已获取系统信息:', systemInfo);
            console.log('[系统信息] APP_VERSION:', systemInfo.APP_VERSION);
            
            // 如果报告页面已打开，更新报告信息
            const reportSection = document.getElementById('testReportSection');
            if (reportSection && !reportSection.classList.contains('hidden')) {
                const urlParams = new URLSearchParams(window.location.search);
                const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
                const hostname = urlParams.get('hostname') || '';
                updateReportInfo(vehicleModel, hostname);
            }
            
            // 对比hostname（只有在没有showSuccess参数时才显示对比结果）
            if (showSuccess !== '1') {
                const sshHostname = systemInfo.HOSTNAME || '';
                if (urlHostname && sshHostname) {
                    if (urlHostname === sshHostname) {
                        // 匹配成功，显示弹窗
                        const message = `车型匹配成功，请开始测试\n获取到的HOSTNAME: ${sshHostname}`;
                        showModal('提示', message);
                    } else {
                        // 匹配失败，显示警告
                        const message = `车型匹配失败\nURL中的hostname: ${urlHostname}\nSSH获取的HOSTNAME: ${sshHostname}`;
                        showModal('警告', message);
                    }
                } else if (sshHostname) {
                    // 只有SSH获取的HOSTNAME，显示提示
                    const message = `获取到的HOSTNAME: ${sshHostname}`;
                    showModal('提示', message);
                }
            }
        } else {
            console.error('获取系统信息失败:', data.message);
            // 只有在没有showSuccess参数时才显示错误提示
            if (showSuccess !== '1') {
                showModal('错误', `获取系统信息失败: ${data.message}`);
            }
        }
    })
    .catch(error => {
        console.error('获取系统信息错误:', error);
        // 隐藏Loading弹窗（如果显示了的话）
        if (showSuccess !== '1') {
            const modal = document.getElementById('customModal');
            modal.classList.remove('show');
            // 显示错误提示
            showModal('错误', `获取系统信息错误: ${error.message}`);
        }
    });
}

// 绑定模板中的测试按钮（所有TAB通用）
function bindTemplateLightButtons() {
    const testButtons = document.querySelectorAll('.test-button[data-item-id]');
    testButtons.forEach(button => {
        const itemId = button.getAttribute('data-item-id');
        // 获取按钮所在的测试区域，确定testId
        const testSection = button.closest('.test-section');
        const testId = testSection ? testSection.getAttribute('data-test-id') : currentTestId;
        
        button.addEventListener('click', function() {
            handleTestItem(itemId, testId || currentTestId);
        });
    });
}

// 初始化测试结果
function initTestResults() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(nav => {
        const testId = nav.getAttribute('data-test-id');
        testResults[testId] = {};
    });
}

// 重置开始测试按钮
// clearTestTime: 是否清空测试开始时间，默认为true（用于真正重置测试状态）
function resetStartTestButton(clearTestTime = true) {
    const startTestBtn = document.querySelector('.start-test-btn');
    startTestBtn.textContent = '开始测试';
    startTestBtn.disabled = false;
    isTesting = false;
    // 只有在需要真正重置测试状态时才清空测试开始时间
    if (clearTestTime) {
        testStartTime = null;
    }
    // 清空灯光测试项记录，允许重新测试时再次发送关闭所有灯指令
    lightTestItemIds.clear();
}

// 开始测试
function startTest() {
    isTesting = true;
    const startTestBtn = document.querySelector('.start-test-btn');
    startTestBtn.textContent = '测试中...';
    startTestBtn.disabled = true;
    
    // 记录测试开始时间戳
    const now = new Date();
    testStartTime = now.getFullYear() + '-' + 
                   String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                   String(now.getDate()).padStart(2, '0') + ' ' +
                   String(now.getHours()).padStart(2, '0') + ':' + 
                   String(now.getMinutes()).padStart(2, '0') + ':' + 
                   String(now.getSeconds()).padStart(2, '0');
    console.log('[测试时间] 记录测试开始时间:', testStartTime);
    
    // 清空灯光测试项记录，开始新的测试
    lightTestItemIds.clear();
    
    // 1. 清理所有测试结果
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(nav => {
        const testId = nav.getAttribute('data-test-id');
        if (testId && testId !== 'test_report') {
            // 清理测试结果数据
            testResults[testId] = {};
            // 清理UI显示
            clearTestResults(testId);
            
            // 清理所有按钮状态
            const testSection = document.querySelector(`.test-section[data-test-id="${testId}"]`);
            if (testSection) {
                // 清理复选框状态
                const resultCheckboxes = testSection.querySelectorAll('.result-checkbox');
                resultCheckboxes.forEach(cb => {
                    cb.checked = false;
                    cb.disabled = false;
                });
                
                // 清理按钮状态文本
                const statusElements = testSection.querySelectorAll('.button-status');
                statusElements.forEach(status => {
                    status.classList.remove('show');
                    status.textContent = '';
                });
                
                // 重置所有测试按钮
                const testButtons = testSection.querySelectorAll('.test-button');
                testButtons.forEach(btn => {
                    btn.disabled = false;
                    const itemId = btn.getAttribute('data-item-id');
                    if (itemId) {
                        updateButtonStatus(itemId, '');
                        showButtonStatus(itemId, false);
                        stopCountdownStatus(itemId);
                    }
                });
            }
        }
    });
    
    // 2. 禁用测试报告TAB的点击（测试进行中时不允许手动跳转）
    const reportNavItem = Array.from(navItems).find(item => item.getAttribute('data-test-id') === 'test_report');
    if (reportNavItem) {
        reportNavItem.style.pointerEvents = 'none';
        reportNavItem.style.opacity = '0.5';
        reportNavItem.style.cursor = 'not-allowed';
    }
    
    // 3. 跳转到第一个TAB（灯光测试）
    let firstTestNavItem = null;
    for (let i = 0; i < navItems.length; i++) {
        const testId = navItems[i].getAttribute('data-test-id');
        if (testId && testId !== 'test_report') {
            firstTestNavItem = navItems[i];
            break;
        }
    }
    
    if (firstTestNavItem) {
        // 移除所有活动状态
        navItems.forEach(nav => nav.classList.remove('active'));
        // 添加第一个TAB的活动状态
        firstTestNavItem.classList.add('active');
        
        // 更新当前测试ID
        const firstTestId = firstTestNavItem.getAttribute('data-test-id');
        currentTestId = firstTestId;
        
        // 加载第一个TAB的测试详情
        loadTestDetails(firstTestId);
        
        // 如果是按键测试，显示提示弹窗
        if (firstTestId === 'button') {
            setTimeout(() => {
                showModal('提示', '测试前请检查按钮为"抬起"状态');
            }, 500);
        }
        // 如果是显示屏测试，显示提示弹窗
        else if (firstTestId === 'display') {
            setTimeout(() => {
                showModal('提示', '<span style="color: #ffffff;">请点击屏幕四角和中心点，判断屏幕点击是否正常/异常</span>');
            }, 500);
        }
        
        // 启用第一个TAB的所有复选框
        setTimeout(() => {
            const testSection = document.querySelector(`.test-section[data-test-id="${firstTestId}"]`);
            if (testSection) {
                const resultCheckboxes = testSection.querySelectorAll('.result-checkbox');
                resultCheckboxes.forEach(cb => {
                    cb.disabled = false;
                });
            }
        }, 100);
    }
}

// 清除测试结果
function clearTestResults(testId) {
    const testSection = document.querySelector(`.test-section[data-test-id="${testId}"]`);
    if (testSection) {
        const resultCheckboxes = testSection.querySelectorAll('.result-checkbox');
        resultCheckboxes.forEach(cb => {
            cb.checked = false;
            cb.disabled = false; // 启用复选框，让用户可以直接勾选
        });
    }
}

// 加载测试详情
function loadTestDetails(testId) {
    // 获取车型信息
    const urlParams = new URLSearchParams(window.location.search);
    const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
    
    // 对于相机测试和按键测试，传递车型参数以过滤设备/测试项
    const url = (testId === 'camera' || testId === 'button')
        ? `/api/test_data/${testId}?vehiclemodel=${vehicleModel}`
        : `/api/test_data/${testId}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderTestDetails(testId, data);
        })
        .catch(error => {
            console.error('加载测试详情失败:', error);
        });
}

// 渲染测试详情
function renderTestDetails(testId, data) {
    const testDetailsContainer = document.getElementById('testDetails');
    
    // 隐藏所有测试部分
    document.querySelectorAll('.test-section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // 检查是否已存在该测试的DOM
    let testSection = document.querySelector(`.test-section[data-test-id="${testId}"]`);
    
    if (!testSection) {
        // 创建新的测试部分
        testSection = document.createElement('div');
        testSection.className = 'test-section';
        testSection.setAttribute('data-test-id', testId);
        
        data.sections.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'detail-section';
            
            const title = document.createElement('h3');
            title.className = 'section-title';
            title.textContent = section.title;
            sectionDiv.appendChild(title);
            
            // 创建每个测试项（按钮和选项在同一行）
            // 举升电机测试：先创建高度输入行
            if (testId === 'lift_motor' && section.items.length > 0 && section.items[0].id === 'lift_up') {
                // 创建高度输入行（独立一行）
                const heightRow = document.createElement('div');
                heightRow.className = 'test-item';
                heightRow.style.marginBottom = '15px';
                
                const heightButtonArea = document.createElement('div');
                heightButtonArea.className = 'button-area';
                heightButtonArea.style.display = 'flex';
                heightButtonArea.style.alignItems = 'center';
                heightButtonArea.style.flexWrap = 'nowrap';
                heightButtonArea.style.whiteSpace = 'nowrap';
                
                const heightLabel = document.createElement('label');
                heightLabel.textContent = '举升高度';
                heightLabel.style.marginRight = '8px';
                heightLabel.style.fontSize = '14px';
                heightLabel.style.whiteSpace = 'nowrap';
                heightLabel.style.color = '#b8b8d4';
                heightButtonArea.appendChild(heightLabel);
                
                const heightInput = document.createElement('input');
                heightInput.type = 'number';
                heightInput.className = 'ip-input';
                heightInput.value = '60'; // 默认60毫米
                heightInput.setAttribute('data-lift-height', 'true');
                heightInput.style.width = '80px';
                heightInput.style.marginRight = '8px';
                heightInput.style.flexShrink = '0';
                heightInput.placeholder = '高度';
                heightButtonArea.appendChild(heightInput);
                
                const heightUnit = document.createElement('span');
                heightUnit.textContent = '毫米';
                heightUnit.style.fontSize = '14px';
                heightUnit.style.whiteSpace = 'nowrap';
                heightUnit.style.flexShrink = '0';
                heightUnit.style.color = '#b8b8d4';
                heightButtonArea.appendChild(heightUnit);
                
                heightRow.appendChild(heightButtonArea);
                
                // 添加一个空的result-area以保持布局一致
                const emptyResultArea = document.createElement('div');
                emptyResultArea.className = 'result-area';
                heightRow.appendChild(emptyResultArea);
                
                sectionDiv.appendChild(heightRow);
            }
            
            // 旋转电机测试：先创建角度输入行
            if (testId === 'rotation_motor' && section.items.length > 0 && section.items[0].id === 'rotate') {
                // 创建角度输入行（独立一行）
                const angleRow = document.createElement('div');
                angleRow.className = 'test-item';
                angleRow.style.marginBottom = '15px';
                
                const angleButtonArea = document.createElement('div');
                angleButtonArea.className = 'button-area';
                angleButtonArea.style.display = 'flex';
                angleButtonArea.style.alignItems = 'center';
                angleButtonArea.style.flexWrap = 'nowrap';
                angleButtonArea.style.whiteSpace = 'nowrap';
                
                const angleLabel = document.createElement('label');
                angleLabel.textContent = '旋转角度';
                angleLabel.style.marginRight = '8px';
                angleLabel.style.fontSize = '14px';
                angleLabel.style.whiteSpace = 'nowrap';
                angleLabel.style.color = '#b8b8d4';
                angleButtonArea.appendChild(angleLabel);
                
                const angleInput = document.createElement('input');
                angleInput.type = 'number';
                angleInput.className = 'ip-input';
                angleInput.value = '90'; // 默认90度
                angleInput.setAttribute('data-rotation-angle', 'true');
                angleInput.style.width = '80px';
                angleInput.style.marginRight = '8px';
                angleInput.style.flexShrink = '0';
                angleInput.placeholder = '角度';
                angleButtonArea.appendChild(angleInput);
                
                const angleUnit = document.createElement('span');
                angleUnit.textContent = '度';
                angleUnit.style.fontSize = '14px';
                angleUnit.style.whiteSpace = 'nowrap';
                angleUnit.style.flexShrink = '0';
                angleUnit.style.color = '#b8b8d4';
                angleButtonArea.appendChild(angleUnit);
                
                angleRow.appendChild(angleButtonArea);
                
                // 添加一个空的result-area以保持布局一致
                const emptyResultArea = document.createElement('div');
                emptyResultArea.className = 'result-area';
                angleRow.appendChild(emptyResultArea);
                
                sectionDiv.appendChild(angleRow);
            }
            
            // 行走电机测试：先创建距离输入行
            if (testId === 'walking_motor' && section.items.length > 0 && section.items[0].id === 'forward') {
                // 创建距离输入行（独立一行）
                const distanceRow = document.createElement('div');
                distanceRow.className = 'test-item';
                distanceRow.style.marginBottom = '15px';
                
                const distanceButtonArea = document.createElement('div');
                distanceButtonArea.className = 'button-area';
                distanceButtonArea.style.display = 'flex';
                distanceButtonArea.style.alignItems = 'center';
                distanceButtonArea.style.flexWrap = 'nowrap';
                distanceButtonArea.style.whiteSpace = 'nowrap';
                
                const distanceLabel = document.createElement('label');
                distanceLabel.textContent = '移动距离';
                distanceLabel.style.marginRight = '8px';
                distanceLabel.style.fontSize = '14px';
                distanceLabel.style.whiteSpace = 'nowrap';
                distanceLabel.style.color = '#b8b8d4';
                distanceButtonArea.appendChild(distanceLabel);
                
                const distanceInput = document.createElement('input');
                distanceInput.type = 'number';
                distanceInput.className = 'ip-input';
                distanceInput.value = '1.0'; // 默认1.0米
                distanceInput.setAttribute('data-walking-distance', 'true');
                distanceInput.setAttribute('step', '0.1'); // 支持小数输入
                distanceInput.style.width = '80px';
                distanceInput.style.marginRight = '8px';
                distanceInput.style.flexShrink = '0';
                distanceInput.placeholder = '距离';
                distanceButtonArea.appendChild(distanceInput);
                
                const distanceUnit = document.createElement('span');
                distanceUnit.textContent = '米';
                distanceUnit.style.fontSize = '14px';
                distanceUnit.style.whiteSpace = 'nowrap';
                distanceUnit.style.flexShrink = '0';
                distanceUnit.style.color = '#b8b8d4';
                distanceButtonArea.appendChild(distanceUnit);
                
                distanceRow.appendChild(distanceButtonArea);
                
                // 添加一个空的result-area以保持布局一致
                const emptyResultArea = document.createElement('div');
                emptyResultArea.className = 'result-area';
                distanceRow.appendChild(emptyResultArea);
                
                sectionDiv.appendChild(distanceRow);
            }
            
            section.items.forEach(item => {
                // 显示屏测试：跳过"屏幕显示"项目
                if (testId === 'display' && item.id === 'screen_display') {
                    return; // 跳过这个项目，不渲染
                }
                
                const itemDiv = document.createElement('div');
                itemDiv.className = 'test-item';
                itemDiv.setAttribute('data-item-id', item.id);
                
                // 按钮区域
                const buttonArea = document.createElement('div');
                buttonArea.className = 'button-area';
                
                // 举升电机测试：只显示按钮
                if (testId === 'lift_motor') {
                    // 测试按钮
                    const testButton = document.createElement('button');
                    testButton.className = 'test-button';
                    testButton.setAttribute('data-item-id', item.id);
                    testButton.setAttribute('data-item-name', item.name);
                    testButton.textContent = item.name;
                    testButton.addEventListener('click', function() {
                        handleLiftMotorTest(item.id, testId);
                    });
                    buttonArea.appendChild(testButton);
                }
                // 旋转电机测试：只显示按钮
                else if (testId === 'rotation_motor') {
                    // 测试按钮
                    const testButton = document.createElement('button');
                    testButton.className = 'test-button';
                    testButton.setAttribute('data-item-id', item.id);
                    testButton.setAttribute('data-item-name', item.name);
                    testButton.textContent = item.name;
                    testButton.addEventListener('click', function() {
                        handleRotationMotorTest(item.id, testId);
                    });
                    buttonArea.appendChild(testButton);
                }
                // 行走电机测试：只显示按钮
                else if (testId === 'walking_motor') {
                    // 测试按钮
                    const testButton = document.createElement('button');
                    testButton.className = 'test-button';
                    testButton.setAttribute('data-item-id', item.id);
                    testButton.setAttribute('data-item-name', item.name);
                    testButton.textContent = item.name;
                    testButton.addEventListener('click', function() {
                        handleWalkingMotorTest(item.id, testId);
                    });
                    buttonArea.appendChild(testButton);
                }
                // 相机测试：显示设备名称、IP输入框和Ping按钮（TOF测试使用"测试"按钮）
                else if (testId === 'camera') {
                    // 设备名称
                    const deviceName = document.createElement('span');
                    deviceName.className = 'device-name';
                    deviceName.textContent = item.name;
                    buttonArea.appendChild(deviceName);
                    
                    // 判断是否是TOF测试项
                    const isTofTest = item.id === 'front_tof' || item.id === 'rear_tof';
                    
                    if (isTofTest) {
                        // TOF测试：添加占位元素使按钮位置与Ping按钮对齐
                        // IP输入框宽度140px + 左右边距各8px = 156px，再加50px = 206px
                        const placeholder = document.createElement('span');
                        placeholder.className = 'tof-placeholder';
                        placeholder.style.cssText = 'display: inline-block; width: 206px; margin: 0 8px;';
                        buttonArea.appendChild(placeholder);
                        
                        // TOF测试：显示"测试"按钮
                        const testButton = document.createElement('button');
                        testButton.className = 'test-button tof-test-button';
                        testButton.setAttribute('data-item-id', item.id);
                        testButton.setAttribute('data-item-name', item.name);
                        testButton.textContent = '测试';
                        // 向右移动半个按钮宽度（约35px，根据按钮实际宽度调整）
                        testButton.style.marginLeft = '140px';
                        testButton.addEventListener('click', function() {
                            handleTofTest(item.id, testId);
                        });
                        buttonArea.appendChild(testButton);
                    } else {
                        // 其他相机测试：显示IP输入框和Ping按钮
                        const ipInput = document.createElement('input');
                        ipInput.type = 'text';
                        ipInput.className = 'ip-input';
                        ipInput.value = item.default_ip || '192.168.1.1';
                        ipInput.setAttribute('data-item-id', item.id);
                        ipInput.placeholder = '请输入IP地址';
                        buttonArea.appendChild(ipInput);
                        
                        // Ping按钮
                        const pingButton = document.createElement('button');
                        pingButton.className = 'test-button ping-button';
                        pingButton.setAttribute('data-item-id', item.id);
                        pingButton.setAttribute('data-item-name', item.name);
                        pingButton.textContent = 'Ping';
                        pingButton.addEventListener('click', function() {
                            handleCameraPing(item.id, testId, ipInput.value);
                        });
                        buttonArea.appendChild(pingButton);
                    }
                } else {
                    // 显示屏测试：显示描述文字（如果有）
                    if (testId === 'display' && item.description) {
                        const descriptionDiv = document.createElement('div');
                        descriptionDiv.className = 'display-description';
                        descriptionDiv.style.cssText = 'text-align: center; margin: 20px auto; padding: 15px 20px; color: #ffffff; font-size: 14px; line-height: 1.6; max-width: 90%;';
                        descriptionDiv.textContent = item.description;
                        itemDiv.appendChild(descriptionDiv);
                        // 显示屏测试有描述的项目不显示按钮，直接跳过按钮创建
                    } else {
                        // 其他测试：显示普通按钮
                        const testButton = document.createElement('button');
                        testButton.className = 'test-button';
                        testButton.setAttribute('data-item-id', item.id);
                        testButton.setAttribute('data-item-name', item.name);
                        testButton.textContent = item.name;
                        
                        // 所有测试都使用相同的处理逻辑
                        testButton.addEventListener('click', function() {
                            handleTestItem(item.id, testId);
                        });
                        buttonArea.appendChild(testButton);
                    }
                }
                
                // 只有当buttonArea有子元素时才添加到itemDiv
                if (buttonArea.children.length > 0) {
                    itemDiv.appendChild(buttonArea);
                }
                
                // 结果选项区域
                const resultArea = document.createElement('div');
                resultArea.className = 'result-area';
                
                const resultDiv = document.createElement('div');
                resultDiv.className = 'test-result';
                
                const normalResultLabel = createCheckboxLabel(item.id + '_result', 'normal', '正常');
                normalResultLabel.classList.add('result-label');
                const normalCheckbox = normalResultLabel.querySelector('input');
                normalCheckbox.classList.add('result-checkbox');
                // 相机测试的复选框默认禁用（不允许人工修改），其他测试根据isTesting状态
                if (testId === 'camera') {
                    normalCheckbox.disabled = true;
                } else {
                    // 所有其他测试（包括举升电机、旋转电机和行走电机）：根据isTesting状态启用/禁用
                    normalCheckbox.disabled = !isTesting;
                }
                
                const abnormalResultLabel = createCheckboxLabel(item.id + '_result', 'abnormal', '异常');
                abnormalResultLabel.classList.add('result-label');
                const abnormalCheckbox = abnormalResultLabel.querySelector('input');
                abnormalCheckbox.classList.add('result-checkbox');
                // 相机测试的复选框默认禁用（不允许人工修改），其他测试根据isTesting状态
                if (testId === 'camera') {
                    abnormalCheckbox.disabled = true;
                } else {
                    // 所有其他测试（包括举升电机、旋转电机和行走电机）：根据isTesting状态启用/禁用
                    abnormalCheckbox.disabled = !isTesting;
                }
                
                resultDiv.appendChild(normalResultLabel);
                resultDiv.appendChild(abnormalResultLabel);
                resultArea.appendChild(resultDiv);
                itemDiv.appendChild(resultArea);
                
                sectionDiv.appendChild(itemDiv);
            });
            
            testSection.appendChild(sectionDiv);
        });
        
        testDetailsContainer.appendChild(testSection);
        
        // 绑定结果复选框事件（互斥选择）
        bindResultCheckboxes(testSection);
    } else {
        testSection.classList.remove('hidden');
        
        // 绑定结果复选框事件（互斥选择）
        bindResultCheckboxes(testSection);
    }
}

// 处理举升电机测试
function handleLiftMotorTest(itemId, testId) {
    if (!isTesting) {
        showModal('提示', '请先点击"开始测试"按钮');
        return;
    }
    
    const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
    if (!button) return;
    
    // 检查是否正在测试中
    const statusText = getButtonStatusElement(itemId);
    if (statusText && statusText.classList.contains('show')) {
        return; // 正在测试中，不重复点击
    }
    
    // 显示"测试中..."状态
    const itemName = button.getAttribute('data-item-name') || '测试项';
    updateButtonStatus(itemId, '测试中...');
    showButtonStatus(itemId, true);
    
    // 获取SSH连接信息
    const sshInfo = getSSHInfo();
    
    // 判断是举升还是放下
    let height;
    if (itemId === 'lift_down') {
        // 放下：固定使用高度0
        height = 0;
    } else {
        // 举升：从输入框获取高度
        const heightInput = document.querySelector('input[data-lift-height="true"]');
        if (!heightInput) {
            showModal('错误', '未找到高度输入框');
            showButtonStatus(itemId, false);
            return;
        }
        
        height = parseInt(heightInput.value);
        if (isNaN(height) || height <= 0) {
            showModal('错误', '请输入有效的举升高度（大于0的整数）');
            showButtonStatus(itemId, false);
            return;
        }
    }
    
    // 发送指令
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            item_id: itemId, 
            test_id: testId,
            height: height,  // 放下固定为0，举升从输入框获取
            ssh_host: sshInfo.ssh_host,
            ssh_user: sshInfo.ssh_user
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 指令发送成功，显示提示弹窗
            const actionName = itemId === 'lift_up' ? '举升' : '放下';
            const message = `请操作人员测量${actionName}高度，并勾选正常/异常`;
            showModal('提示', message, function() {
                // 点击确认按钮后，关闭弹窗，保持"测试中..."状态
                // 等待用户勾选结果后，再更新为"已完成"
            });
        } else {
            // 指令发送失败
            showModal('错误', data.message || '指令发送失败');
            showButtonStatus(itemId, false);
        }
    })
    .catch(error => {
        console.error('发送指令错误:', error);
        showModal('错误', '网络错误，请重试');
        showButtonStatus(itemId, false);
    });
}

// 处理旋转电机测试
function handleRotationMotorTest(itemId, testId) {
    if (!isTesting) {
        showModal('提示', '请先点击"开始测试"按钮');
        return;
    }
    
    const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
    if (!button) return;
    
    // 检查是否正在测试中
    const statusText = getButtonStatusElement(itemId);
    if (statusText && statusText.classList.contains('show')) {
        return; // 正在测试中，不重复点击
    }
    
    // 显示"测试中..."状态
    const itemName = button.getAttribute('data-item-name') || '测试项';
    updateButtonStatus(itemId, '测试中...');
    showButtonStatus(itemId, true);
    
    // 获取SSH连接信息
    const sshInfo = getSSHInfo();
    
    // 判断是旋转还是归零
    let angle;
    if (itemId === 'reset') {
        // 归零：固定使用角度0
        angle = 0;
    } else {
        // 旋转：从输入框获取角度
        const angleInput = document.querySelector('input[data-rotation-angle="true"]');
        if (!angleInput) {
            showModal('错误', '未找到角度输入框');
            showButtonStatus(itemId, false);
            return;
        }
        
        angle = parseInt(angleInput.value);
        if (isNaN(angle) || angle <= 0) {
            showModal('错误', '请输入有效的旋转角度（大于0的整数）');
            showButtonStatus(itemId, false);
            return;
        }
    }
    
    // 构建请求体
    const requestBody = { 
        item_id: itemId, 
        test_id: testId,
        angle: angle,  // 归零固定为0，旋转从输入框获取
        ssh_host: sshInfo.ssh_host,
        ssh_user: sshInfo.ssh_user
    };
    
    // 发送指令
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 指令发送成功，显示提示弹窗
            const actionName = itemId === 'rotate' ? '旋转' : '归零';
            const message = `请操作人员进行${actionName}测量，并选择正常/异常`;
            showModal('提示', message, function() {
                // 点击确认按钮后，关闭弹窗，保持"测试中..."状态
                // 等待用户勾选结果后，再更新为"已完成"
            });
        } else {
            // 指令发送失败
            showModal('错误', data.message || '指令发送失败');
            showButtonStatus(itemId, false);
        }
    })
    .catch(error => {
        console.error('发送指令错误:', error);
        showModal('错误', '网络错误，请重试');
        showButtonStatus(itemId, false);
    });
}

// 处理行走电机测试
function handleWalkingMotorTest(itemId, testId) {
    if (!isTesting) {
        showModal('提示', '请先点击"开始测试"按钮');
        return;
    }
    
    const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
    if (!button) return;
    
    // 检查是否正在测试中
    const statusText = getButtonStatusElement(itemId);
    if (statusText && statusText.classList.contains('show')) {
        return; // 正在测试中，不重复点击
    }
    
    // 获取距离输入框的值
    const distanceInput = document.querySelector('input[data-walking-distance="true"]');
    if (!distanceInput) {
        showModal('错误', '未找到距离输入框');
        return;
    }
    
    const distance = parseFloat(distanceInput.value);
    if (isNaN(distance) || distance <= 0) {
        showModal('错误', '请输入有效的移动距离（大于0的数字，单位：米）');
        return;
    }
    
    // 显示"测试中..."状态
    const itemName = button.getAttribute('data-item-name') || '测试项';
    updateButtonStatus(itemId, '测试中...');
    showButtonStatus(itemId, true);
    
    // 获取SSH连接信息
    const sshInfo = getSSHInfo();
    
    // 构建请求体
    const requestBody = { 
        item_id: itemId, 
        test_id: testId,
        distance: distance,  // 传递距离参数（米）
        ssh_host: sshInfo.ssh_host,
        ssh_user: sshInfo.ssh_user
    };
    
    // 发送指令
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 指令发送成功，显示提示弹窗
            const actionName = itemId === 'forward' ? '前进' : '后退';
            const message = `请操作人员进行${actionName}测量，并选择正常/异常`;
            showModal('提示', message, function() {
                // 点击确认按钮后，关闭弹窗，保持"测试中..."状态
                // 等待用户勾选结果后，再更新为"已完成"
            });
        } else {
            // 指令发送失败
            showModal('错误', data.message || '指令发送失败');
            showButtonStatus(itemId, false);
        }
    })
    .catch(error => {
        console.error('发送指令错误:', error);
        showModal('错误', '网络错误，请重试');
        showButtonStatus(itemId, false);
    });
}

// 处理测试项（所有TAB通用）
function handleTestItem(itemId, testId) {
    if (!isTesting) {
        showModal('提示', '请先点击"开始测试"按钮');
        return;
    }
    
    const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
    if (!button) return;
    
    // 检查是否正在测试中（通过状态文本判断）
    const statusText = getButtonStatusElement(itemId);
    if (statusText && statusText.classList.contains('show')) {
        return; // 正在测试中，不重复点击
    }
    
    // 获取按钮名称
    const itemName = button.getAttribute('data-item-name') || '测试项';
    
    // 语音测试：点击按钮后立即显示弹窗，不等待后端响应（因为后端执行时间很长）
    if (testId === 'voice' || itemId === 'voice_broadcast') {
        const message = '语音播报将在30秒内进行，请注意聆听，并人工勾选正常/异常';
        showModal('提示', message);
        startCountdownStatus(itemId, itemName);  // 立即开始倒计时30秒
    }
    
    // 获取SSH连接信息
    const sshInfo = getSSHInfo();
    
    // 发送指令（所有TAB都支持）
    fetch('/api/send_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            item_id: itemId, 
            test_id: testId,  // 传递当前测试类型
            ssh_host: sshInfo.ssh_host,
            ssh_user: sshInfo.ssh_user
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 指令发送成功，显示提示弹窗
            // 根据测试类型显示不同的提示语
            let message = '';
            // 按键测试、触边测试、显示屏测试使用相同的逻辑
            if (testId === 'button' || testId === 'touch' || testId === 'display') {
                // 触边测试：根据前触边/后触边显示不同的提示
                if (testId === 'touch') {
                    if (itemName.includes('后触边')) {
                        message = '请点击确定按钮后，再长按设备上后触边位置30秒';
                    } else if (itemName.includes('前触边')) {
                        message = '请点击确定按钮后，再长按设备上前触边位置30秒';
                    } else {
                        message = `请点击设备上${itemName}，完成后请点击确定，并勾选正常/异常`;
                    }
                } else if (testId === 'button') {
                    // 按键测试：急停按钮有特殊提示
                    if (itemId === 'front_right_emergency' || itemId === 'back_right_emergency' || 
                        itemId === 'front_left_emergency' || itemId === 'back_left_emergency') {
                        message = `请按下设备上${itemName}，完成后请点击确定，系统自动判断正常/异常`;
                    } else if (itemId === 'front_right_confirm') {
                        message = '请点击确定按钮后，长按设备右前确认按钮到测试结束';
                    } else if (itemId === 'back_right_confirm') {
                        message = '请点击确定按钮后，长按设备右后确认按钮到测试结束';
                    } else if (itemId === 'front_right_maintenance') {
                        message = '请点击确定按钮后，长按设备右前维修按钮到测试结束';
                    } else if (itemId === 'back_right_maintenance') {
                        message = '请点击确定按钮后，长按设备右后维修按钮到测试结束';
                    } else {
                        // 其他按键测试：请点击设备上{按钮名称}，完成后请点击确定，并勾选正常/异常
                        message = `请点击设备上${itemName}，完成后请点击确定，并勾选正常/异常`;
                    }
                } else {
                    // 显示屏测试：请点击设备上{按钮名称}，完成后请点击确定，并勾选正常/异常
                    message = `请点击设备上${itemName}，完成后请点击确定，并勾选正常/异常`;
                }
                // 点击确认后自动检查IO（监控30秒）
                showModal('提示', message, function() {
                    // 点击确认按钮后，开始倒计时并自动检查IO（30秒内轮询）
                    startCountdownStatus(itemId, itemName);  // 在确认后开始倒计时
                    checkButtonIO(itemId, testId);
                });
            } else {
                // 语音测试：已经在点击时显示了弹窗，这里不需要重复显示
                if (testId === 'voice' || itemId === 'voice_broadcast') {
                    // 弹窗和倒计时已经在点击按钮时显示，这里不需要处理
                } else {
                    // 其他测试：请查看{按钮名称}状态，完成后请点击确定按钮，并勾选正常/异常
                    message = `请查看${itemName}状态，完成后请点击确定按钮，并勾选正常/异常`;
                    showModal('提示', message, function() {
                        // 其他测试：点击确认按钮后，更新状态为"已完成"
                        updateButtonStatus(itemId, '已完成');
                        stopCountdownStatus(itemId);
                    });
                }
            }
        } else {
            // 如果命令不存在（某些测试项可能没有配置命令），也显示提示弹窗
            if (data.message && data.message.includes('无需发送命令')) {
                const itemName = button.getAttribute('data-item-name') || '测试项';
                // 根据测试类型显示不同的提示语
                let message = '';
                // 按键测试、触边测试、显示屏测试使用相同的逻辑
                if (testId === 'button' || testId === 'touch' || testId === 'display') {
                    // 触边测试：根据前触边/后触边显示不同的提示
                    if (testId === 'touch') {
                        if (itemName.includes('后触边')) {
                            message = '请点击确定按钮后，再长按设备上后触边位置30秒';
                        } else if (itemName.includes('前触边')) {
                            message = '请点击确定按钮后，再长按设备上前触边位置30秒';
                        } else {
                            message = `请点击设备上${itemName}，完成后请点击确定，并勾选正常/异常`;
                        }
                    } else if (testId === 'button') {
                        // 按键测试：急停按钮有特殊提示
                        if (itemId === 'front_right_emergency' || itemId === 'back_right_emergency' || 
                            itemId === 'front_left_emergency' || itemId === 'back_left_emergency') {
                            message = `请按下设备上${itemName}，完成后请点击确定，系统自动判断正常/异常`;
                        } else if (itemId === 'front_right_confirm') {
                            message = '请点击确定按钮后，长按设备右前确认按钮到测试结束';
                        } else if (itemId === 'back_right_confirm') {
                            message = '请点击确定按钮后，长按设备右后确认按钮到测试结束';
                        } else if (itemId === 'front_right_maintenance') {
                            message = '请点击确定按钮后，长按设备右前维修按钮到测试结束';
                        } else if (itemId === 'back_right_maintenance') {
                            message = '请点击确定按钮后，长按设备右后维修按钮到测试结束';
                        } else {
                            // 其他按键测试：请点击设备上{按钮名称}，完成后请点击确定，并勾选正常/异常
                            message = `请点击设备上${itemName}，完成后请点击确定，并勾选正常/异常`;
                        }
                    } else {
                        // 显示屏测试：请点击设备上{按钮名称}，完成后请点击确定，并勾选正常/异常
                        message = `请点击设备上${itemName}，完成后请点击确定，并勾选正常/异常`;
                    }
                    // 点击确认后自动检查IO（监控30秒）
                    showModal('提示', message, function() {
                        // 点击确认按钮后，开始倒计时并自动检查IO（30秒内轮询）
                        startCountdownStatus(itemId, itemName);  // 在确认后开始倒计时
                        checkButtonIO(itemId, testId);
                    });
                } else {
                    // 语音测试：已经在点击时显示了弹窗，这里不需要重复显示
                    if (testId === 'voice' || itemId === 'voice_broadcast') {
                        // 弹窗和倒计时已经在点击按钮时显示，这里不需要处理
                    } else {
                        // 其他测试：请查看{按钮名称}状态，完成后请点击确定按钮，并勾选正常/异常
                        message = `请查看${itemName}状态，完成后请点击确定按钮，并勾选正常/异常`;
                        showModal('提示', message, function() {
                            // 其他测试：点击确认按钮后，更新状态为"已完成"
                            updateButtonStatus(itemId, '已完成');
                            stopCountdownStatus(itemId);
                        });
                    }
                }
            } else {
                // 即使指令发送失败，对于按键测试、触边测试、显示屏测试也显示提示弹窗（允许继续测试）
                const itemName = button.getAttribute('data-item-name') || '测试项';
                if (testId === 'button' || testId === 'touch' || testId === 'display') {
                    // 即使SSH失败也显示提示，允许手动测试
                    let message = '';
                    // 触边测试：根据前触边/后触边显示不同的提示
                    if (testId === 'touch') {
                        if (itemName.includes('后触边')) {
                            message = '请点击确定按钮后，再长按设备上后触边位置30秒';
                        } else if (itemName.includes('前触边')) {
                            message = '请点击确定按钮后，再长按设备上前触边位置30秒';
                        } else {
                            message = `请点击设备上${itemName}，完成后请点击确定`;
                        }
                    } else if (testId === 'button') {
                        // 按键测试：急停按钮有特殊提示
                        if (itemId === 'front_right_emergency' || itemId === 'back_right_emergency' || 
                            itemId === 'front_left_emergency' || itemId === 'back_left_emergency') {
                            message = `请按下设备上${itemName}，完成后请点击确定，系统自动判断正常/异常`;
                        } else {
                            // 其他按键测试：请点击设备上{按钮名称}，完成后请点击确定
                            message = `请点击设备上${itemName}，完成后请点击确定`;
                        }
                    } else {
                        // 显示屏测试：请点击设备上{按钮名称}，完成后请点击确定
                        message = `请点击设备上${itemName}，完成后请点击确定`;
                    }
                    if (data.message && !data.message.includes('未知的测试项')) {
                        // 如果有错误信息，先显示警告，然后显示提示
                        console.warn('SSH指令发送失败，但允许继续测试:', data.message);
                    }
                    showModal('提示', message, function() {
                        // 点击确认按钮后，开始自动检查IO（监控30秒）
                        checkButtonIO(itemId, testId);
                    });
                } else {
                    // 其他测试：显示错误信息
                    if (data.message && !data.message.includes('未知的测试项')) {
                        showModal('错误', '指令发送失败: ' + data.message);
                        // 失败时隐藏状态提示
                        showButtonStatus(itemId, false);
                        stopCountdownStatus(itemId);
                    } else {
                        // 没有配置命令的测试项，显示提示弹窗
                        // 语音测试：特殊提示语
                        let message = '';
                        if (testId === 'voice' || itemId === 'voice_broadcast') {
                            // 语音测试：已经在点击时显示了弹窗，这里不需要重复显示
                            // 弹窗和倒计时已经在点击按钮时显示，这里不需要处理
                        } else {
                            // 其他测试：请查看{按钮名称}状态，完成后请点击确定按钮，并勾选正常/异常
                            message = `请查看${itemName}状态，完成后请点击确定按钮，并勾选正常/异常`;
                            showModal('提示', message, function() {
                                // 其他测试：点击确认按钮后，更新状态为"已完成"
                                updateButtonStatus(itemId, '已完成');
                                stopCountdownStatus(itemId);
                            });
                        }
                    }
                }
            }
        }
    })
    .catch(error => {
        console.error('发送指令错误:', error);
        // 语音测试：如果已经显示了弹窗，不需要再次显示
        if (testId === 'voice' || itemId === 'voice_broadcast') {
            // 语音测试已经在点击时显示了弹窗，这里不需要处理
            return;
        }
        // 对于按键测试、触边测试、显示屏测试，即使网络错误也显示提示，允许继续测试
        if (testId === 'button' || testId === 'touch' || testId === 'display') {
            const itemName = button.getAttribute('data-item-name') || '测试项';
            let message = '';
            // 触边测试：根据前触边/后触边显示不同的提示
            if (testId === 'touch') {
                if (itemName.includes('后触边')) {
                    message = '请点击确定按钮后，再长按设备上后触边位置30秒';
                } else if (itemName.includes('前触边')) {
                    message = '请点击确定按钮后，再长按设备上前触边位置30秒';
                } else {
                    message = `请点击设备上${itemName}，完成后请点击确定`;
                }
            } else {
                // 按键测试、显示屏测试：请点击设备上{按钮名称}，完成后请点击确定
                message = `请点击设备上${itemName}，完成后请点击确定`;
            }
            console.warn('网络错误，但允许继续测试:', error);
            showModal('提示', message, function() {
                // 点击确认按钮后，开始倒计时并自动检查IO（监控30秒）
                startCountdownStatus(itemId, itemName);  // 在确认后开始倒计时
                checkButtonIO(itemId, testId);
            });
        } else {
            showModal('错误', '发送指令失败');
            // 失败时隐藏状态提示
            showButtonStatus(itemId, false);
            stopCountdownStatus(itemId);
        }
    });
}

// 获取或创建按钮状态元素
function getButtonStatusElement(itemId) {
    // 支持多种按钮类型：test-button, ping-button, tof-test-button
    let button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
    if (!button) {
        button = document.querySelector(`.ping-button[data-item-id="${itemId}"]`);
    }
    if (!button) {
        button = document.querySelector(`.tof-test-button[data-item-id="${itemId}"]`);
    }
    if (!button) return null;
    
    const buttonArea = button.closest('.button-area');
    if (!buttonArea) return null;
    
    let statusElement = buttonArea.querySelector('.button-status');
    if (!statusElement) {
        statusElement = document.createElement('span');
        statusElement.className = 'button-status';
        statusElement.textContent = '测试中...';
        buttonArea.appendChild(statusElement);
    }
    
    return statusElement;
}

// 显示或隐藏按钮状态提示
function showButtonStatus(itemId, show, text) {
    const statusElement = getButtonStatusElement(itemId);
    if (statusElement) {
        if (show) {
            statusElement.classList.add('show');
            // 如果提供了文本，更新文本内容
            if (text) {
                statusElement.textContent = text;
            }
        } else {
            statusElement.classList.remove('show');
        }
    }
}

// 开始倒计时状态显示（{按钮名称}测试中...30s）
function startCountdownStatus(itemId, itemName) {
    const statusElement = getButtonStatusElement(itemId);
    if (!statusElement) return;
    
    const timeout = appConfig.ioCheckTimeout; // 30秒
    let remaining = timeout / 1000; // 转换为秒
    
    // 立即显示初始状态
    statusElement.textContent = `${itemName}测试中...${remaining}s`;
    statusElement.classList.add('show');
    
    // 存储倒计时定时器ID，以便后续清除
    if (!window.countdownTimers) {
        window.countdownTimers = {};
    }
    
    // 清除之前的倒计时（如果存在）
    if (window.countdownTimers[itemId]) {
        clearInterval(window.countdownTimers[itemId]);
    }
    
    // 开始倒计时（使用config.py的IO_CHECK_TIMEOUT参数）
    window.countdownTimers[itemId] = setInterval(() => {
        remaining--;
        if (remaining > 0) {
            statusElement.textContent = `${itemName}测试中...${remaining}s`;
        } else {
            // 倒计时结束，清除定时器
            clearInterval(window.countdownTimers[itemId]);
            delete window.countdownTimers[itemId];
            // 倒计时结束时，立即更新状态为"已完成"（确保显示更新）
            // 注意：超时处理函数也会被调用，但这里先更新显示确保同步
            statusElement.textContent = '已完成';
        }
    }, 1000);
}

// 停止倒计时
function stopCountdownStatus(itemId) {
    if (window.countdownTimers && window.countdownTimers[itemId]) {
        clearTimeout(window.countdownTimers[itemId]);
        delete window.countdownTimers[itemId];
    }
}

// 更新按钮状态文本
function updateButtonStatus(itemId, text) {
    const statusElement = getButtonStatusElement(itemId);
    if (statusElement) {
        statusElement.textContent = text;
        statusElement.classList.add('show');
    }
}

// 检查按键IO状态（按键测试专用，30秒内自动判断）
function checkButtonIO(itemId, testId) {
    const startTime = Date.now();
    const timeout = appConfig.ioCheckTimeout; // 从config.py的IO_CHECK_TIMEOUT获取（毫秒）
    
    const sshInfo = getSSHInfo();
    // 获取车型信息
    const urlParams = new URLSearchParams(window.location.search);
    const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
    
    // 获取按钮名称
    const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
    const itemName = button ? (button.getAttribute('data-item-name') || '测试项') : '测试项';
    
    let isCompleted = false; // 标记是否已完成（成功或超时）
    
    // 超时处理函数
    function handleTimeout() {
        if (isCompleted) return;
        isCompleted = true;
        // 停止倒计时
        stopCountdownStatus(itemId);
        // 倒计时结束后直接显示"已完成"，自动勾选异常，不显示弹窗
        setTestResult(itemId, 'abnormal', testId);
        
        // 更新按钮状态为"已完成"（将"测试中..."改为"已完成"）并常显示
        updateButtonStatus(itemId, '已完成');
        showButtonStatus(itemId, true);  // 确保"已完成"状态常显示
        
        // 检查是否所有测试项都完成了
        checkAllTestsCompleted();
    }
    
    // 设置超时定时器（与倒计时同步，使用config.py的IO_CHECK_TIMEOUT参数）
    const timeoutTimer = setTimeout(handleTimeout, timeout);
    
    // 只调用一次check_io，不轮询（避免重复执行rostopic echo指令）
    console.log('[前端调试] 开始检查IO状态（单次调用，不轮询）...');
    fetch('/api/check_io', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            item_id: itemId, 
            test_id: testId,
            ssh_host: sshInfo.ssh_host,
            ssh_user: sshInfo.ssh_user,
            vehicle_model: vehicleModel  // 传递车型信息
        })
    })
    .then(response => response.json())
    .then(data => {
        if (isCompleted) return; // 如果已经完成（超时），不再处理
        
        if (data.status === 'success') {
            isCompleted = true;
            clearTimeout(timeoutTimer);
            
            // 停止倒计时
            stopCountdownStatus(itemId);
            
            // 检测到数据，根据后端返回的test_status进行判断
            console.log('[前端调试] ========== 收到后端返回的测试结果 ==========');
            console.log('[前端调试] 完整数据:', JSON.stringify(data, null, 2));
            console.log('[前端调试] itemId:', itemId);
            console.log('[前端调试] test_status:', data.test_status, '(类型:', typeof data.test_status, ')');
            console.log('[前端调试] io_value:', data.io_value);
            console.log('[前端调试] expected_value:', data.expected_value);
            console.log('[前端调试] testId:', testId);
            
            // 打印预期结果和实际结果
            console.log(`[前端调试] 预期结果: ${data.expected_value || 0}`);
            console.log(`[前端调试] 实际结果: ${data.io_value}`);
            
            // 使用后端返回的test_status（normal或abnormal）
            // 确保test_status是字符串类型
            let testStatus = data.test_status;
            if (!testStatus || typeof testStatus !== 'string') {
                console.warn('[前端调试] ⚠️ test_status无效，使用默认值abnormal');
                testStatus = 'abnormal';
            } else {
                testStatus = testStatus.toLowerCase(); // 转换为小写，确保一致性
            }
            console.log(`[前端调试] 最终使用的testStatus: "${testStatus}" (类型: ${typeof testStatus})`);
            console.log(`[前端调试] testStatus === 'normal': ${testStatus === 'normal'}`);
            console.log(`[前端调试] testStatus === 'abnormal': ${testStatus === 'abnormal'}`);
            console.log('[前端调试] ===========================================');
            
            setTestResult(itemId, testStatus, testId);
            
            // 更新按钮状态为"已完成"（将"测试中..."改为"已完成"）并常显示
            updateButtonStatus(itemId, '已完成');
            showButtonStatus(itemId, true);  // 确保"已完成"状态常显示
            
            // 检查是否所有测试项都完成了
            checkAllTestsCompleted();
        } else if (data.status === 'error') {
            // 后端返回错误（比如30秒内未获取到数据）
            // 等待超时定时器统一处理
            console.log('[前端调试] 后端返回错误，等待超时处理:', data.message);
            // 注意：这里不设置isCompleted，让超时定时器统一处理
        }
    })
    .catch(error => {
        if (isCompleted) return; // 如果已经完成（超时），不再处理
        
        console.error('检查IO错误:', error);
        // 错误处理由超时定时器统一处理
    });
}

// 处理相机Ping测试
function handleCameraPing(itemId, testId, ipAddress) {
    // 检查是否已点击"开始测试"按钮
    if (!isTesting) {
        showModal('提示', '请先点击"开始测试"按钮');
        return;
    }
    
    if (!ipAddress || !ipAddress.trim()) {
        showModal('错误', '请输入IP地址');
        return;
    }
    
    // 验证IP地址格式
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipRegex.test(ipAddress.trim())) {
        showModal('错误', 'IP地址格式不正确');
        return;
    }
    
    const button = document.querySelector(`.ping-button[data-item-id="${itemId}"]`);
    if (!button) return;
    
    // 检查是否正在测试中
    const statusText = getButtonStatusElement(itemId);
    if (statusText && statusText.classList.contains('show')) {
        return; // 正在测试中，不重复点击
    }
    
    // 禁用Ping按钮
    button.disabled = true;
    
    // 获取设备名称
    const itemName = button.getAttribute('data-item-name') || '设备';
    
    // 开始10秒倒计时
    startCameraCountdown(itemId, itemName, 10);
    
    // 执行ping测试（后端会持续10秒）
    const startTime = Date.now();
    const pingTimeout = 10000; // 10秒超时
    
    fetch('/api/check_io', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            test_id: testId,
            ip_address: ipAddress.trim(),
            ssh_host: getSSHInfo().ssh_host,
            ssh_user: getSSHInfo().ssh_user
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('[相机测试] 收到后端响应:', data);
        
        if (data.status === 'success') {
            // 如果0%丢包（正常），立即勾选正常
            if (data.test_status === 'normal') {
                console.log('[相机测试] ✅ 0%丢包，立即勾选正常');
                // 停止倒计时
                stopCountdownStatus(itemId);
                
                // 立即设置测试结果为正常
                setTestResult(itemId, 'normal', testId);
                
                // 更新按钮状态为"已完成"（常显示，表示测试过）
                updateButtonStatus(itemId, '已完成');
                showButtonStatus(itemId, true);
                
                // 检查是否所有测试项都完成了
                checkAllTestsCompleted();
                
                // 重新启用Ping按钮
                button.disabled = false;
            } else {
                // 如果有丢包（异常），等待10秒后再勾选异常
                console.log('[相机测试] ❌ 有丢包，等待10秒后勾选异常');
                
                // 确保至少等待10秒（与倒计时同步）
                const elapsed = Date.now() - startTime;
                const remainingTime = Math.max(0, pingTimeout - elapsed);
                
                setTimeout(() => {
                    // 停止倒计时
                    stopCountdownStatus(itemId);
                    
                    // 设置测试结果为异常
                    setTestResult(itemId, 'abnormal', testId);
                    
                    // 更新按钮状态为"已完成"（常显示，表示测试过）
                    updateButtonStatus(itemId, '已完成');
                    showButtonStatus(itemId, true);
                    
                    // 检查是否所有测试项都完成了
                    checkAllTestsCompleted();
                    
                    // 重新启用Ping按钮
                    button.disabled = false;
                }, remainingTime);
            }
        } else {
            // 测试失败，等待10秒后再勾选异常
            console.log('[相机测试] ❌ 测试失败，等待10秒后勾选异常');
            
            // 确保至少等待10秒（与倒计时同步）
            const elapsed = Date.now() - startTime;
            const remainingTime = Math.max(0, pingTimeout - elapsed);
            
            setTimeout(() => {
                // 停止倒计时
                stopCountdownStatus(itemId);
                
                // 测试失败，自动标记为异常
                setTestResult(itemId, 'abnormal', testId);
                
                // 更新按钮状态为"已完成"（常显示，表示测试过）
                updateButtonStatus(itemId, '已完成');
                showButtonStatus(itemId, true);
                
                showModal('错误', data.message || 'Ping测试失败');
                
                // 重新启用Ping按钮
                button.disabled = false;
            }, remainingTime);
        }
    })
    .catch(error => {
        console.error('[相机测试] Ping测试错误:', error);
        
        // 错误情况，等待10秒后再勾选异常
        // 确保至少等待10秒（与倒计时同步）
        const elapsed = Date.now() - startTime;
        const remainingTime = Math.max(0, pingTimeout - elapsed);
        
        setTimeout(() => {
            // 停止倒计时
            stopCountdownStatus(itemId);
            
            // 测试失败，自动标记为异常
            setTestResult(itemId, 'abnormal', testId);
            
            // 更新按钮状态为"已完成"（常显示，表示测试过）
            updateButtonStatus(itemId, '已完成');
            showButtonStatus(itemId, true);
            
            showModal('错误', 'Ping测试失败');
            
            // 重新启用Ping按钮
            button.disabled = false;
        }, remainingTime);
    });
}

// 处理TOF测试（前TOF和后TOF）
function handleTofTest(itemId, testId) {
    // 检查是否已点击"开始测试"按钮
    if (!isTesting) {
        showModal('提示', '请先点击"开始测试"按钮');
        return;
    }
    
    const button = document.querySelector(`.tof-test-button[data-item-id="${itemId}"]`);
    if (!button) return;
    
    // 检查是否正在测试中
    const statusText = getButtonStatusElement(itemId);
    if (statusText && statusText.classList.contains('show')) {
        return; // 正在测试中，不重复点击
    }
    
    // 禁用测试按钮
    button.disabled = true;
    
    // 获取设备名称
    const itemName = button.getAttribute('data-item-name') || 'TOF设备';
    
    // 获取超时时间（从config获取，默认30秒）
    const timeoutSeconds = appConfig.ioCheckTimeout / 1000 || 30;
    
    // 开始30秒倒计时（使用与按键测试相同的倒计时方式）
    startCountdownStatus(itemId, itemName);
    
    // 获取SSH信息
    const sshInfo = getSSHInfo();
    
    // 执行TOF订阅测试
    const startTime = Date.now();
    const tofTimeout = timeoutSeconds * 1000; // 转换为毫秒
    
    console.log(`[TOF测试] 开始测试 ${itemName}，超时时间: ${timeoutSeconds}秒`);
    
    fetch('/api/check_io', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            test_id: testId,
            ssh_host: sshInfo.ssh_host,
            ssh_user: sshInfo.ssh_user
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(`[TOF测试] ${itemName} 收到后端响应:`, data);
        
        if (data.status === 'success') {
            // 停止倒计时
            stopCountdownStatus(itemId);
            
            // 根据test_status设置结果
            if (data.test_status === 'normal') {
                console.log(`[TOF测试] ✅ ${itemName} 订阅成功，收到数据，勾选正常`);
                setTestResult(itemId, 'normal', testId);
            } else {
                console.log(`[TOF测试] ❌ ${itemName} 订阅超时，未收到数据，勾选异常`);
                setTestResult(itemId, 'abnormal', testId);
            }
            
            // 更新按钮状态为"已完成"（常显示，表示测试过）
            updateButtonStatus(itemId, '已完成');
            showButtonStatus(itemId, true);
            
            // 恢复按钮文本和状态
            button.disabled = false;
            button.textContent = '测试';
            
            // 检查是否所有测试项都完成了
            checkAllTestsCompleted();
        } else {
            // 错误情况，等待超时后再勾选异常
            const elapsed = Date.now() - startTime;
            const remainingTime = Math.max(0, tofTimeout - elapsed);
            
            console.log(`[TOF测试] ❌ ${itemName} 测试失败，等待${remainingTime}ms后勾选异常`);
            
            setTimeout(() => {
                // 停止倒计时
                stopCountdownStatus(itemId);
                
                // 测试失败，自动标记为异常
                setTestResult(itemId, 'abnormal', testId);
                
                // 更新按钮状态为"已完成"（常显示，表示测试过）
                updateButtonStatus(itemId, '已完成');
                showButtonStatus(itemId, true);
                
                showModal('错误', data.message || `${itemName} 测试失败`);
                
                // 恢复按钮文本和状态
                button.disabled = false;
                button.textContent = '测试';
            }, remainingTime);
        }
    })
    .catch(error => {
        console.error(`[TOF测试] ${itemName} 测试错误:`, error);
        
        // 错误情况，等待超时后再勾选异常
        const elapsed = Date.now() - startTime;
        const remainingTime = Math.max(0, tofTimeout - elapsed);
        
        setTimeout(() => {
            // 停止倒计时
            stopCountdownStatus(itemId);
            
            // 测试失败，自动标记为异常
            setTestResult(itemId, 'abnormal', testId);
            
            // 更新按钮状态为"已完成"（常显示，表示测试过）
            updateButtonStatus(itemId, '已完成');
            showButtonStatus(itemId, true);
            
            showModal('错误', `${itemName} 测试失败`);
            
            // 恢复按钮文本和状态
            button.disabled = false;
            button.textContent = '测试';
        }, remainingTime);
    });
}

// 建立相机测试的SSH连接
function connectCameraSSH() {
    const sshInfo = getSSHInfo();
    if (!sshInfo.ssh_host) {
        console.warn('[相机测试] 未提供SSH主机地址，跳过连接');
        return;
    }
    
    // 如果已经连接，不重复连接
    if (window.cameraSSHConnected) {
        console.log('[相机测试] SSH连接已存在，跳过');
        return;
    }
    
    console.log('[相机测试] 正在建立SSH连接...');
    fetch('/api/camera/connect_ssh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ssh_host: sshInfo.ssh_host,
            ssh_user: sshInfo.ssh_user
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.cameraSSHConnected = true;
            console.log('[相机测试] ✅ SSH连接已建立:', data.message);
        } else {
            console.error('[相机测试] ❌ SSH连接失败:', data.message);
            window.cameraSSHConnected = false;
        }
    })
    .catch(error => {
        console.error('[相机测试] SSH连接错误:', error);
        window.cameraSSHConnected = false;
    });
}

// 断开相机测试的SSH连接
function disconnectCameraSSH() {
    const sshInfo = getSSHInfo();
    if (!sshInfo.ssh_host) {
        return;
    }
    
    if (!window.cameraSSHConnected) {
        return;
    }
    
    console.log('[相机测试] 正在断开SSH连接...');
    fetch('/api/camera/disconnect_ssh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ssh_host: sshInfo.ssh_host
        })
    })
    .then(response => response.json())
    .then(data => {
        window.cameraSSHConnected = false;
        console.log('[相机测试] 🔌 SSH连接已断开:', data.message);
    })
    .catch(error => {
        console.error('[相机测试] 断开SSH连接错误:', error);
        window.cameraSSHConnected = false;
    });
}

// 开始相机测试倒计时（10秒）
function startCameraCountdown(itemId, itemName, timeoutSeconds) {
    const statusElement = getButtonStatusElement(itemId);
    if (!statusElement) return;
    
    // 只显示"测试中..."，不显示动态倒计时
    statusElement.textContent = `${itemName}测试中...`;
    statusElement.classList.add('show');
    
    // 存储倒计时定时器ID（用于10秒后自动停止）
    if (!window.countdownTimers) {
        window.countdownTimers = {};
    }
    
    // 清除之前的倒计时（如果存在）
    if (window.countdownTimers[itemId]) {
        clearTimeout(window.countdownTimers[itemId]);
    }
    
    // 10秒后自动停止倒计时（但不改变显示，由结果处理函数来更新为"已完成"）
    window.countdownTimers[itemId] = setTimeout(() => {
        // 倒计时结束，清除定时器
        delete window.countdownTimers[itemId];
        // 注意：这里不更新状态，由结果处理函数来更新为"已完成"
    }, timeoutSeconds * 1000);
}

// 检查IO状态
function checkIOStatus(itemId) {
    // 轮询检查IO状态，使用配置的超时时间和间隔
    const startTime = Date.now();
    const timeout = appConfig.ioCheckTimeout;
    const interval = appConfig.ioCheckInterval;
    
    const checkInterval = setInterval(() => {
        fetch('/api/check_io', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                item_id: itemId, 
                test_id: 'light',
                ssh_host: getSSHInfo().ssh_host,
                ssh_user: getSSHInfo().ssh_user
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                clearInterval(checkInterval);
                // 设置测试结果
                setTestResult(itemId, data.test_status, testId);
                
                // 按钮保持置灰状态，不恢复
                const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
                if (button) {
                    // 按钮保持disabled状态，不显示文本，保持置灰样式
                    button.textContent = '';
                    button.disabled = true;
                }
                
                // 检查是否所有测试项都完成了
                checkAllTestsCompleted();
            } else if (Date.now() - startTime > timeout) {
                clearInterval(checkInterval);
                showModal('超时', `检查IO状态超时（${timeout / 1000}秒）`);
                const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
                if (button) {
                    // 超时后按钮保持置灰
                    button.textContent = '';
                    button.disabled = true;
                }
            }
        })
        .catch(error => {
            console.error('检查IO错误:', error);
            if (Date.now() - startTime > timeout) {
                clearInterval(checkInterval);
                showModal('错误', '检查IO状态失败');
                const button = document.querySelector(`.test-button[data-item-id="${itemId}"]`);
                if (button) {
                    // 失败时保持置灰
                    button.textContent = '';
                    button.disabled = true;
                }
            }
        });
    }, interval);
}

// 设置测试结果
function setTestResult(itemId, status, testId) {
    if (!currentTestId) return;
    
    // 如果没有传递testId，使用currentTestId
    const actualTestId = testId || currentTestId;
    
    console.log('[前端调试] setTestResult被调用:', {
        itemId: itemId,
        status: status,
        testId: testId,
        actualTestId: actualTestId,
        currentTestId: currentTestId
    });
    
    // 确保testResults[currentTestId]已初始化
    if (!testResults[currentTestId]) {
        testResults[currentTestId] = {};
    }
    
    // 保存结果
    testResults[currentTestId][itemId] = status;
    
    // 更新UI - 使用更精确的选择器，确保找到正确的复选框
    // 先尝试在当前测试区域中查找
    const testSection = document.querySelector(`.test-section[data-test-id="${actualTestId}"]`);
    let normalCheckbox, abnormalCheckbox;
    
    if (testSection) {
        normalCheckbox = testSection.querySelector(`input[name="${itemId}_result"][value="normal"]`);
        abnormalCheckbox = testSection.querySelector(`input[name="${itemId}_result"][value="abnormal"]`);
    }
    
    // 如果没找到，使用全局选择器
    if (!normalCheckbox || !abnormalCheckbox) {
        normalCheckbox = document.querySelector(`input[name="${itemId}_result"][value="normal"]`);
        abnormalCheckbox = document.querySelector(`input[name="${itemId}_result"][value="abnormal"]`);
    }
    
    console.log('[前端调试] 找到的复选框:', {
        normalCheckbox: normalCheckbox ? '存在' : '不存在',
        abnormalCheckbox: abnormalCheckbox ? '存在' : '不存在',
        status: status,
        'status === normal': status === 'normal',
        'status === abnormal': status === 'abnormal'
    });
    
    if (normalCheckbox && abnormalCheckbox) {
        // 先取消所有选中
        normalCheckbox.checked = false;
        abnormalCheckbox.checked = false;
        
        // 根据status设置对应的复选框
        if (status === 'normal') {
            normalCheckbox.setAttribute('data-auto-set', 'true');  // 标记为自动设置
            normalCheckbox.checked = true;
            abnormalCheckbox.checked = false;
            console.log('[前端调试] ✅ 勾选正常复选框，取消异常复选框');
        } else if (status === 'abnormal') {
            abnormalCheckbox.setAttribute('data-auto-set', 'true');  // 标记为自动设置
            normalCheckbox.checked = false;
            abnormalCheckbox.checked = true;
            console.log('[前端调试] ✅ 勾选异常复选框，取消正常复选框');
        } else {
            console.warn('[前端调试] ⚠️ 未知的status值:', status);
            return; // 如果status值无效，直接返回
        }
        
        // 验证设置是否成功
        console.log('[前端调试] 设置后的复选框状态:', {
            normalChecked: normalCheckbox.checked,
            abnormalChecked: abnormalCheckbox.checked,
            status: status
        });
        
        // 手动触发change事件，确保保存结果等逻辑能正确执行
        // 但由于有data-auto-set标记，bindResultCheckboxes中的事件监听器会跳过互斥逻辑
        
        // 验证最终状态并触发change事件
        setTimeout(() => {
            // 再次确认data-auto-set标记存在（防止被其他逻辑移除）
            if (status === 'normal') {
                normalCheckbox.setAttribute('data-auto-set', 'true');
            } else if (status === 'abnormal') {
                abnormalCheckbox.setAttribute('data-auto-set', 'true');
            }
            
            console.log('[前端调试] 最终复选框状态验证:', {
                normalChecked: normalCheckbox.checked,
                abnormalChecked: abnormalCheckbox.checked,
                status: status,
                '状态是否匹配': (status === 'normal' && normalCheckbox.checked) || (status === 'abnormal' && abnormalCheckbox.checked),
                'normalCheckbox data-auto-set': normalCheckbox.getAttribute('data-auto-set'),
                'abnormalCheckbox data-auto-set': abnormalCheckbox.getAttribute('data-auto-set')
            });
            
            // 触发change事件，确保保存结果等逻辑能正确执行
            // 注意：在触发事件前，确保data-auto-set标记存在
            if (status === 'normal' && normalCheckbox.checked) {
                // 再次确认标记存在
                normalCheckbox.setAttribute('data-auto-set', 'true');
                const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                normalCheckbox.dispatchEvent(changeEvent);
                console.log('[前端调试] ✅ 已触发正常复选框的change事件');
            } else if (status === 'abnormal' && abnormalCheckbox.checked) {
                // 再次确认标记存在
                abnormalCheckbox.setAttribute('data-auto-set', 'true');
                const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                abnormalCheckbox.dispatchEvent(changeEvent);
                console.log('[前端调试] ✅ 已触发异常复选框的change事件');
            }
            
            // 如果状态不匹配，强制修正
            if (status === 'normal' && !normalCheckbox.checked) {
                console.warn('[前端调试] ⚠️ 状态不匹配，强制修正为正常');
                normalCheckbox.setAttribute('data-auto-set', 'true');
                normalCheckbox.checked = true;
                abnormalCheckbox.checked = false;
                // 再次触发change事件
                const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                normalCheckbox.dispatchEvent(changeEvent);
            } else if (status === 'abnormal' && !abnormalCheckbox.checked) {
                console.warn('[前端调试] ⚠️ 状态不匹配，强制修正为异常');
                abnormalCheckbox.setAttribute('data-auto-set', 'true');
                normalCheckbox.checked = false;
                abnormalCheckbox.checked = true;
                // 再次触发change事件
                const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                abnormalCheckbox.dispatchEvent(changeEvent);
            }
            
            // 最终验证：确保复选框状态正确
            setTimeout(() => {
                const finalNormalChecked = normalCheckbox.checked;
                const finalAbnormalChecked = abnormalCheckbox.checked;
                console.log('[前端调试] 最终状态确认:', {
                    status: status,
                    normalChecked: finalNormalChecked,
                    abnormalChecked: finalAbnormalChecked,
                    '应该正常': status === 'normal' && finalNormalChecked,
                    '应该异常': status === 'abnormal' && finalAbnormalChecked
                });
                
                // 如果最终状态仍然不正确，再次强制修正
                if (status === 'normal' && !finalNormalChecked) {
                    console.error('[前端调试] ❌ 最终状态仍然不正确，最后一次强制修正为正常');
                    normalCheckbox.setAttribute('data-auto-set', 'true');
                    normalCheckbox.checked = true;
                    abnormalCheckbox.checked = false;
                } else if (status === 'abnormal' && !finalAbnormalChecked) {
                    console.error('[前端调试] ❌ 最终状态仍然不正确，最后一次强制修正为异常');
                    abnormalCheckbox.setAttribute('data-auto-set', 'true');
                    normalCheckbox.checked = false;
                    abnormalCheckbox.checked = true;
                }
            }, 100);
        }, 50);
        
        // 对于触边测试、显示屏测试和相机测试，设置结果后禁用复选框（不允许人工修改）
        if (actualTestId === 'touch' || actualTestId === 'display' || actualTestId === 'camera') {
            normalCheckbox.disabled = true;
            abnormalCheckbox.disabled = true;
        }
    } else {
        console.warn('[前端调试] ⚠️ 未找到复选框元素，itemId:', itemId);
    }
    
    // 实时更新测试报告（如果报告页面已打开）
    updateTestReportInRealTime();
}

// 检查所有测试项是否完成
function checkAllTestsCompleted() {
    if (!currentTestId) return;
    
    // 跳过测试报告TAB的检查
    if (currentTestId === 'test_report') return;
    
    const testSection = document.querySelector(`.test-section[data-test-id="${currentTestId}"]`);
    if (!testSection) return;
    
    // 确保testResults已初始化
    if (!testResults[currentTestId]) {
        testResults[currentTestId] = {};
    }
    
    // 获取所有测试项
    const testItems = testSection.querySelectorAll('.test-item');
    if (testItems.length === 0) {
        console.log(`[检查完成] ${currentTestId}: ⚠️ 没有测试项，不进行跳转（等待用户手动操作）`);
        // 没有测试项时不自动跳转，等待用户手动操作
        return;
    }
    
    console.log(`[检查完成] ${currentTestId}: 开始检查 ${testItems.length} 个测试项是否全部完成`);
    
    let allCompleted = true;
    const incompleteItems = [];
    
    testItems.forEach(item => {
        const itemId = item.getAttribute('data-item-id');
        if (!itemId) return; // 跳过没有ID的项
        
        // 检查是否有结果（normal或abnormal）
        const result = testResults[currentTestId][itemId];
        if (!result || (result !== 'normal' && result !== 'abnormal')) {
            allCompleted = false;
            incompleteItems.push(itemId);
        }
    });
    
    if (allCompleted && testItems.length > 0) {
        console.log(`[检查完成] ${currentTestId}: ✅ 所有测试项都已完成，1秒后跳转到下一个TAB`);
        // 所有测试项都完成了，延迟1秒后跳转到下一个TAB
        jumpToNextTab();
        // setTimeout(() => {
        //     jumpToNextTab();
        // }, 1000);
    } else {
        console.log(`[检查完成] ${currentTestId}: ❌ 还有未完成的测试项: [${incompleteItems.join(', ')}]`);
    }
}

// 跳转到下一个TAB
function jumpToNextTab() {
    const navItems = document.querySelectorAll('.nav-item');
    let currentIndex = -1;
    
    // 找到当前激活的TAB索引
    navItems.forEach((item, index) => {
        if (item.classList.contains('active')) {
            console.log("222item:", item, "index:", index)
            currentIndex = index;
        }
    });

    console.log("111currentIndex:", currentIndex)
    
    if (currentIndex < 0) {
        console.warn('[自动跳转] 未找到当前激活的TAB');
        return;
    }
    
    // 打印所有TAB的顺序，用于调试
    console.log('[自动跳转] 当前所有TAB顺序:');
    const allTabIds = [];
    navItems.forEach((item, idx) => {
        const testId = item.getAttribute('data-test-id');
        const isActive = item.classList.contains('active');
        const tabName = item.textContent.trim();
        console.log(`  [${idx}] ${testId} (${tabName}) ${isActive ? '(当前激活)' : ''}`);
        allTabIds.push(testId);
    });
    console.log(`[自动跳转] 当前TAB索引: ${currentIndex}, 当前TAB ID: ${navItems[currentIndex]?.getAttribute('data-test-id')}`);
    console.log(`[自动跳转] 所有TAB ID列表: [${allTabIds.join(', ')}]`);
    
    // 找到下一个非"测试报告"的TAB
    let nextIndex = currentIndex + 1;
    let nextNavItem = null;
    let nextTestId = null;
    
    // 从下一个索引开始查找，跳过"测试报告"TAB
    while (nextIndex < navItems.length) {
        const item = navItems[nextIndex];
        const testId = item.getAttribute('data-test-id');
        const tabName = item.textContent.trim();
        
        console.log(`[自动跳转] 检查索引 ${nextIndex}: testId=${testId} (${tabName})`);
        
        // 跳过"测试报告"TAB，只跳转到测试TAB
        if (testId && testId !== 'test_report') {
            nextNavItem = item;
            nextTestId = testId;
            console.log(`[自动跳转] ✅ 找到下一个测试TAB: ${nextTestId} (${tabName}) (索引 ${nextIndex})`);
            break;
        } else {
            console.log(`[自动跳转] ⏭️ 跳过TAB: ${testId} (${tabName}) (索引 ${nextIndex})`);
        }
        nextIndex++;
    }
    
    // 如果找到了下一个测试TAB
    if (nextNavItem && nextTestId) {
        console.log(`[自动跳转] 从 ${navItems[currentIndex].getAttribute('data-test-id')} 跳转到 ${nextTestId}`);
        
        // 移除所有活动状态
        navItems.forEach(nav => nav.classList.remove('active'));
        // 添加下一个TAB的活动状态
        nextNavItem.classList.add('active');
        
        // 更新当前测试ID
        currentTestId = nextTestId;
        
        // 加载下一个TAB的测试详情
        loadTestDetails(nextTestId);
        
        // 如果是按键测试，显示提示弹窗
        if (nextTestId === 'button') {
            setTimeout(() => {
                showModal('提示', '测试前请检查按钮为"抬起"状态');
            }, 500); // 延迟500ms，确保页面加载完成
        }
        // 如果是显示屏测试，显示提示弹窗
        else if (nextTestId === 'display') {
            setTimeout(() => {
                showModal('提示', '<span style="color: #ffffff;">请点击屏幕四角和中心点，判断屏幕点击是否正常/异常</span>');
            }, 500);
        }
        
        // 如果正在测试中，自动启用下一个TAB的复选框
        if (isTesting) {
            setTimeout(() => {
                const testSection = document.querySelector(`.test-section[data-test-id="${nextTestId}"]`);
                if (testSection) {
                    // 初始化下一个TAB的测试结果
                    if (!testResults[nextTestId]) {
                        testResults[nextTestId] = {};
                    }
                    
                    // 启用所有复选框
                    const resultCheckboxes = testSection.querySelectorAll('.result-checkbox');
                    resultCheckboxes.forEach(cb => {
                        cb.disabled = false;
                    });
                }
            }, 100);
        }
    } else {
        // 没有找到下一个测试TAB，说明所有测试都完成了，跳转到测试报告
        console.log('[自动跳转] 所有测试TAB已完成，跳转到测试报告');
        const reportNavItem = Array.from(navItems).find(item => item.getAttribute('data-test-id') === 'test_report');
        if (reportNavItem) {
            // 恢复测试报告TAB的点击功能（测试完成后允许查看报告）
            reportNavItem.style.pointerEvents = 'auto';
            reportNavItem.style.opacity = '1';
            reportNavItem.style.cursor = 'pointer';
            
            navItems.forEach(nav => nav.classList.remove('active'));
            reportNavItem.classList.add('active');
            currentTestId = 'test_report';
            loadTestReport(); // 刷新显示最新结果（内部会调用resetStartTestButton(false)）
        } else {
            showModal('完成', '所有测试已完成！');
            isTesting = false;
            const startTestBtn = document.querySelector('.start-test-btn');
            if (startTestBtn) {
                startTestBtn.textContent = '开始测试';
                startTestBtn.disabled = false;
            }
        }
    }
}

// 创建复选框标签
function createCheckboxLabel(name, value, text) {
    const label = document.createElement('label');
    label.className = 'checkbox-label';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.name = name;
    checkbox.value = value;
    checkbox.className = 'status-checkbox';
    
    const span = document.createElement('span');
    span.textContent = text;
    
    label.appendChild(checkbox);
    label.appendChild(span);
    
    return label;
}

// 绑定结果复选框事件（正常/异常互斥选择）
function bindResultCheckboxes(testSection) {
    const resultCheckboxes = testSection.querySelectorAll('.result-checkbox');
    resultCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // 检查是否是程序自动设置（通过data-auto-set属性标记）
            const isAutoSet = this.getAttribute('data-auto-set') === 'true';
            if (isAutoSet) {
                // 如果是程序自动设置，移除标记并跳过互斥逻辑
                this.removeAttribute('data-auto-set');
                return;
            }
            
            if (!this.disabled && this.checked) {
                const name = this.getAttribute('name');
                const itemId = name.replace('_result', '').replace('_normal', '').replace('_abnormal', '');
                const value = this.value; // 'normal' 或 'abnormal'
                
                // 获取测试ID
                const testId = testSection ? testSection.getAttribute('data-test-id') : currentTestId;
                
                // 互斥选择：取消同组的其他选项
                const sameNameCheckboxes = testSection.querySelectorAll(`input[name="${name}"]`);
                sameNameCheckboxes.forEach(cb => {
                    if (cb !== this) {
                        cb.checked = false;
                    }
                });
                
                // 如果是举升电机测试、旋转电机测试或行走电机测试，勾选后禁用所有相关复选框
                if (testId === 'lift_motor' || testId === 'rotation_motor' || testId === 'walking_motor') {
                    const normalCheckbox = document.querySelector(`input[name="${itemId}_result"][value="normal"]`);
                    const abnormalCheckbox = document.querySelector(`input[name="${itemId}_result"][value="abnormal"]`);
                    
                    if (normalCheckbox) normalCheckbox.disabled = true;
                    if (abnormalCheckbox) abnormalCheckbox.disabled = true;
                    
                    // 更新状态为"已完成"
                    updateButtonStatus(itemId, '已完成');
                    showButtonStatus(itemId, true);
                }
                
                // 保存结果
                if (currentTestId) {
                    // 确保testResults[currentTestId]已初始化
                    if (!testResults[currentTestId]) {
                        testResults[currentTestId] = {};
                    }
                    testResults[currentTestId][itemId] = value;
                    console.log(`[保存结果] ${currentTestId}.${itemId} = ${value}`);
                    
                    // 更新按钮状态为"已完成"并常显示（用户手动勾选后）
                    updateButtonStatus(itemId, '已完成');
                    showButtonStatus(itemId, true);  // 确保"已完成"状态常显示
                    
                    // 检查是否所有测试项都完成了
                    checkAllTestsCompleted();
                }
                
                // 如果是灯光测试，选择正常或异常后，自动发送关闭所有灯的指令
                // 注意：每个灯光测试项选择后只发送一次关闭所有灯指令，避免重复发送
                if (testId === 'light') {
                    // 检查该测试项是否已经发送过关闭所有灯指令
                    if (!lightTestItemIds.has(itemId)) {
                        // 标记该测试项已发送关闭所有灯指令
                        lightTestItemIds.add(itemId);
                        
                        // 获取SSH连接信息
                        const sshInfo = getSSHInfo();
                        
                        // 发送关闭所有灯的指令
                        fetch('/api/send_command', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ 
                                item_id: 'turn_off_all_lights',  // 特殊ID，用于标识关闭所有灯指令
                                test_id: 'light',
                                ssh_host: sshInfo.ssh_host,
                                ssh_user: sshInfo.ssh_user
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                console.log(`[灯光测试] ${itemId}选择${value}后，关闭所有灯指令发送成功`);
                            } else {
                                console.warn(`[灯光测试] ${itemId}选择${value}后，关闭所有灯指令发送失败:`, data.message);
                            }
                        })
                        .catch(error => {
                            console.error(`[灯光测试] ${itemId}选择${value}后，关闭所有灯指令发送错误:`, error);
                        });
                    } else {
                        console.log(`[灯光测试] ${itemId}已发送过关闭所有灯指令，跳过重复发送`);
                    }
                }
                
                // 更新按钮状态为"已完成"并常显示（用户手动勾选后）
                updateButtonStatus(itemId, '已完成');
                showButtonStatus(itemId, true);  // 确保"已完成"状态常显示
                
                // 检查是否所有测试项都完成了
                checkAllTestsCompleted();
            }
        });
    });
}

// 加载测试报告
function loadTestReport() {
    // 隐藏所有测试部分
    document.querySelectorAll('.test-section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // 显示测试报告部分
    const reportSection = document.getElementById('testReportSection');
    if (reportSection) {
        reportSection.classList.remove('hidden');
    }
    
    // 重置开始测试按钮（跳转到测试报告时还原为"开始测试"）
    // 注意：不清空测试开始时间，因为测试已经进行，只是查看报告
    resetStartTestButton(false);
    
    // 恢复测试报告TAB的点击功能（测试完成后允许查看报告）
    const navItems = document.querySelectorAll('.nav-item');
    const reportNavItem = Array.from(navItems).find(item => item.getAttribute('data-test-id') === 'test_report');
    if (reportNavItem) {
        reportNavItem.style.pointerEvents = 'auto';
        reportNavItem.style.opacity = '1';
        reportNavItem.style.cursor = 'pointer';
    }
    
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search);
    const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
    const hostname = urlParams.get('hostname') || '';
    
    // 填充报告信息
    updateReportInfo(vehicleModel, hostname);
    
    // 获取测试结果
    console.log('当前测试结果:', testResults);
    fetch('/api/test_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_results: testResults,
            vehicle_model: vehicleModel,
            hostname: hostname,
            app_version: systemInfo.APP_VERSION || '', // 传递APP_VERSION
            tester: testerName, // 传递测试人员名称
            test_time: testStartTime || '' // 传递测试开始时间
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('报告数据:', data);
        if (data.status === 'success') {
            renderTestReport(data.data, data.title);
        } else {
            showModal('错误', '加载测试报告失败');
        }
    })
    .catch(error => {
        console.error('加载测试报告失败:', error);
        showModal('错误', '加载测试报告失败');
    });
}

// 更新报告信息
function updateReportInfo(vehicleModel, hostname) {
    // 型号
    const modelElement = document.getElementById('reportModel');
    if (modelElement) {
        modelElement.textContent = vehicleModel || '-';
    }
    
    // 软件版本（从系统信息中获取APP_VERSION）
    const versionElement = document.getElementById('reportVersion');
    if (versionElement) {
        versionElement.textContent = systemInfo.APP_VERSION || '-';
    }
    
    // 设备序列号（从hostname获取）
    const serialElement = document.getElementById('reportSerialNumber');
    if (serialElement) {
        serialElement.textContent = hostname || '-';
    }
    
    // 测试时间（使用点击"开始测试"时记录的时间戳，如果没有则显示"-"）
    const testTimeElement = document.getElementById('reportTestTime');
    if (testTimeElement) {
        if (testStartTime) {
            testTimeElement.textContent = testStartTime;
        } else {
            testTimeElement.textContent = '-';
        }
    }
    
    // 测试人员（可编辑输入框，默认张三）
    const testerElement = document.getElementById('reportTester');
    if (testerElement) {
        // 检查是否已经是输入框
        if (testerElement.tagName === 'INPUT') {
            testerElement.value = testerName;
        } else {
            // 创建输入框
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'tester-input';
            input.value = testerName;
            input.placeholder = '请输入测试人员';
            input.addEventListener('blur', function() {
                testerName = this.value || '张三';
                // 保存到localStorage
                localStorage.setItem('testerName', testerName);
            });
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    this.blur();
                }
            });
            testerElement.parentNode.replaceChild(input, testerElement);
            input.id = 'reportTester';
        }
    }
    
    // 从localStorage加载测试人员名称
    const savedTesterName = localStorage.getItem('testerName');
    if (savedTesterName) {
        testerName = savedTesterName;
        const testerInput = document.getElementById('reportTester');
        if (testerInput && testerInput.tagName === 'INPUT') {
            testerInput.value = testerName;
        }
    }
}

// 渲染测试报告
function renderTestReport(reportData, title) {
    const tableBody = document.getElementById('reportTableBody');
    if (!tableBody) return;
    
    // 清空表格
    tableBody.innerHTML = '';
    
    // 填充数据
    reportData.forEach(row => {
        const tr = document.createElement('tr');
        
        const categoryTd = document.createElement('td');
        categoryTd.textContent = row.category;
        tr.appendChild(categoryTd);
        
        const itemTd = document.createElement('td');
        itemTd.textContent = row.item;
        tr.appendChild(itemTd);
        
        const resultTd = document.createElement('td');
        resultTd.textContent = row.result;
        resultTd.style.textAlign = 'center'; // 测试结果居中显示
        // 根据结果设置样式
        if (row.result === '正常') {
            resultTd.className = 'result-normal';
        } else if (row.result === '异常') {
            resultTd.className = 'result-abnormal';
        } else {
            resultTd.className = 'result-untested';
        }
        tr.appendChild(resultTd);
        
        tableBody.appendChild(tr);
    });
}

// 实时更新测试报告（如果报告页面已打开）
function updateTestReportInRealTime() {
    const reportSection = document.getElementById('testReportSection');
    if (reportSection && !reportSection.classList.contains('hidden')) {
        // 报告页面已打开，实时刷新
        const urlParams = new URLSearchParams(window.location.search);
        const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
        const hostname = urlParams.get('hostname') || '';
        
    fetch('/api/test_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_results: testResults,
            vehicle_model: vehicleModel,
            hostname: hostname,
            app_version: systemInfo.APP_VERSION || '', // 传递APP_VERSION
            tester: testerName, // 传递测试人员名称
            test_time: testStartTime || '' // 传递测试开始时间
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                renderTestReport(data.data, data.title);
            }
        })
        .catch(error => {
            console.error('实时更新测试报告失败:', error);
        });
    }
}

// 下载测试报告
function downloadTestReport() {
    const urlParams = new URLSearchParams(window.location.search);
    const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
    const hostname = urlParams.get('hostname') || '';
    
    fetch('/api/download_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_results: testResults,
            vehicle_model: vehicleModel,
            hostname: hostname,
            app_version: systemInfo.APP_VERSION || '', // 传递APP_VERSION
            tester: testerName, // 传递测试人员名称
            test_time: testStartTime || '' // 传递测试开始时间
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            return response.json().then(data => {
                throw new Error(data.message || '下载失败');
            });
        }
    })
    .then(blob => {
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // 生成文件名，使用测试开始时间戳（如果有），否则使用当前时间
        let timeStr;
        if (testStartTime) {
            // 将格式从 "2026-01-13 11:13:20" 转换为 "2026-01-13_11-13-20"（文件名中不能有冒号）
            timeStr = testStartTime.replace(/ /g, '_').replace(/:/g, '-');
        } else {
            // 如果没有测试开始时间，使用当前时间
            const now = new Date();
            timeStr = now.getFullYear() + '-' + 
                     String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                     String(now.getDate()).padStart(2, '0') + '_' +
                     String(now.getHours()).padStart(2, '0') + '-' + 
                     String(now.getMinutes()).padStart(2, '0') + '-' + 
                     String(now.getSeconds()).padStart(2, '0');
        }
        a.download = `机器人静态测试报告_${vehicleModel}_${timeStr}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('下载报告失败:', error);
        showModal('错误', '下载报告失败: ' + error.message);
    });
}

// 云端同步（上传到飞书云文档）
function uploadToCloud() {
    const urlParams = new URLSearchParams(window.location.search);
    const vehicleModel = urlParams.get('vehiclemodel') || 'X100';
    const hostname = urlParams.get('hostname') || '';
    
    // 显示上传中提示
    const cloudSyncBtn = document.getElementById('cloudSyncBtn');
    if (cloudSyncBtn) {
        cloudSyncBtn.disabled = true;
        cloudSyncBtn.textContent = '上传中...';
    }
    
    // 先获取报告文件并保存到本地
    fetch('/api/download_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_results: testResults,
            vehicle_model: vehicleModel,
            hostname: hostname,
            app_version: systemInfo.APP_VERSION || '',
            tester: testerName,
            test_time: testStartTime || '' // 传递测试开始时间
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            return response.json().then(data => {
                throw new Error(data.message || '获取报告失败');
            });
        }
    })
    .then(blob => {
        // 生成文件名，使用测试开始时间戳（如果有），否则使用当前时间
        let timeStr;
        if (testStartTime) {
            // 将格式从 "2026-01-13 11:13:20" 转换为 "2026-01-13_11-13-20"（文件名中不能有冒号）
            timeStr = testStartTime.replace(/ /g, '_').replace(/:/g, '-');
        } else {
            // 如果没有测试开始时间，使用当前时间
            const now = new Date();
            timeStr = now.getFullYear() + '-' + 
                     String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                     String(now.getDate()).padStart(2, '0') + '_' +
                     String(now.getHours()).padStart(2, '0') + '-' + 
                     String(now.getMinutes()).padStart(2, '0') + '-' + 
                     String(now.getSeconds()).padStart(2, '0');
        }
        const cloudname = `机器人静态测试报告_${vehicleModel}_${timeStr}.xlsx`;
        const cloudsize = blob.size; // 获取文件大小（字节）
        
        console.log(`[云端同步] 文件名: ${cloudname}, 大小: ${cloudsize}字节`);
        
        // 第一步：保存文件到本地report文件夹
        const formData = new FormData();
        formData.append('file', blob, cloudname);
        formData.append('cloudname', cloudname);
        
        return fetch('/api/save_report', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(saveResult => {
            if (saveResult.status !== 'success') {
                throw new Error(saveResult.message || '保存文件失败');
            }
            
            console.log(`[云端同步] 文件已保存到本地: ${saveResult.file_path}`);
            
            // 第二步：执行上传脚本
            return fetch('/api/upload_to_cloud', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cloudname: saveResult.cloudname,
                    cloudsize: saveResult.cloudsize
                })
            });
        });
    })
    .then(response => response.json())
    .then(data => {
        if (cloudSyncBtn) {
            cloudSyncBtn.disabled = false;
            cloudSyncBtn.textContent = '云端同步';
        }
        
        if (data.status === 'success') {
            const cloudUrl = 'https://thundersoft.feishu.cn/drive/folder/K5RAfwXaNl0Mc2dmp5dcpmFinKb';
            showModal('成功', '报告已成功上传到云端！\n' + (data.message || ''), null, cloudUrl);
        } else {
            showModal('错误', '上传失败: ' + (data.message || '未知错误'));
        }
    })
    .catch(error => {
        console.error('云端同步失败:', error);
        if (cloudSyncBtn) {
            cloudSyncBtn.disabled = false;
            cloudSyncBtn.textContent = '云端同步';
        }
        showModal('错误', '云端同步失败: ' + error.message);
    });
}

// 绑定复选框事件
function bindCheckboxEvents(container, itemId) {
    const checkboxes = container.querySelectorAll('.status-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const name = this.getAttribute('name');
            const value = this.value;
            
            const sameNameCheckboxes = container.querySelectorAll(`input[name="${name}"]`);
            
            if (this.checked) {
                sameNameCheckboxes.forEach(cb => {
                    if (cb !== this) {
                        cb.checked = false;
                    }
                });
                
                // 保存结果
                if (currentTestId) {
                    testResults[currentTestId][itemId] = value;
                    setTestResult(itemId, value);
                }
                
                // 检查是否所有测试项都完成了
                checkAllTestsCompleted();
            }
        });
    });
}

// 收集测试结果
function collectTestResults() {
    return {
        testId: currentTestId,
        results: testResults[currentTestId] || {}
    };
}
