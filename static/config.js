// 配置页面JavaScript

let vehicleTypes = [];
let allVehicleModels = [];

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadVehicleTypes();
    
    // 设备类型选择变化时，加载对应的具体型号
    document.getElementById('vehicleType').addEventListener('change', function() {
        const selectedType = this.value;
        if (selectedType) {
            loadVehicleModels(selectedType);
        } else {
            // 清空车辆型号下拉框
            const vehicleModelSelect = document.getElementById('vehicleModel');
            vehicleModelSelect.innerHTML = '<option value="">请先选择设备类型</option>';
            vehicleModelSelect.disabled = true;
        }
    });
    
    // 进入测试按钮点击事件
    document.getElementById('startTestBtn').addEventListener('click', function() {
        startTest();
    });
    
    // 加载历史配置按钮点击事件
    document.getElementById('loadHistoryBtn').addEventListener('click', function() {
        loadHistoryConfig();
    });
});

// 加载设备类型列表
function loadVehicleTypes() {
    fetch('/api/vehicle_types')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                vehicleTypes = data.vehicle_types;
                allVehicleModels = data.all_models;
                
                // 填充设备类型下拉框
                const vehicleTypeSelect = document.getElementById('vehicleType');
                vehicleTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    vehicleTypeSelect.appendChild(option);
                });
                
                console.log('[配置页面] 设备类型加载成功:', vehicleTypes);
            } else {
                console.error('[配置页面] 加载设备类型失败:', data.message);
                alert('加载设备类型失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('[配置页面] 加载设备类型错误:', error);
            alert('加载设备类型时发生错误');
        });
}

// 根据设备类型加载具体型号列表
function loadVehicleModels(vehicleType) {
    fetch(`/api/vehicle_models?type=${encodeURIComponent(vehicleType)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const vehicleModels = data.vehicle_models;
                
                // 填充车辆型号下拉框
                const vehicleModelSelect = document.getElementById('vehicleModel');
                vehicleModelSelect.innerHTML = '<option value="">请选择车辆型号</option>';
                
                vehicleModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    vehicleModelSelect.appendChild(option);
                });
                
                // 启用车辆型号下拉框
                vehicleModelSelect.disabled = false;
                
                console.log('[配置页面] 车辆型号加载成功:', vehicleModels);
            } else {
                console.error('[配置页面] 加载车辆型号失败:', data.message);
                alert('加载车辆型号失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('[配置页面] 加载车辆型号错误:', error);
            alert('加载车辆型号时发生错误');
        });
}

// 显示弹窗
function showModal(title, message, onConfirm) {
    const modal = document.getElementById('configModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalClose = document.getElementById('modalClose');
    const modalConfirm = document.getElementById('modalConfirm');
    
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    
    // 清除之前的事件监听器
    const newCloseBtn = modalClose.cloneNode(true);
    modalClose.parentNode.replaceChild(newCloseBtn, modalClose);
    
    const newConfirmBtn = modalConfirm.cloneNode(true);
    modalConfirm.parentNode.replaceChild(newConfirmBtn, modalConfirm);
    
    // 添加新的事件监听器
    newCloseBtn.addEventListener('click', function() {
        modal.classList.remove('show');
        if (onConfirm) onConfirm();
    });
    
    newConfirmBtn.addEventListener('click', function() {
        modal.classList.remove('show');
        if (onConfirm) onConfirm();
    });
    
    // 点击背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('show');
            if (onConfirm) onConfirm();
        }
    });
    
    modal.classList.add('show');
}

// 显示加载弹窗
function showLoadingModal(message) {
    const modal = document.getElementById('configLoadingModal');
    const loadingMessage = document.getElementById('loadingMessage');
    loadingMessage.textContent = message || '检测中，请稍后...';
    modal.classList.add('show');
}

// 隐藏加载弹窗
function hideLoadingModal() {
    const modal = document.getElementById('configLoadingModal');
    modal.classList.remove('show');
}

// 开始测试（先检测车辆ID，再跳转到测试页面）
function startTest() {
    const vehicleId = document.getElementById('vehicleId').value.trim();
    const vehicleIp = document.getElementById('vehicleIp').value.trim();
    const vehicleModel = document.getElementById('vehicleModel').value;
    
    // 验证必填项
    if (!vehicleId) {
        showModal('提示', '请输入车辆ID');
        document.getElementById('vehicleId').focus();
        return;
    }
    
    if (!vehicleIp) {
        showModal('提示', '请输入车辆IP地址');
        document.getElementById('vehicleIp').focus();
        return;
    }
    
    if (!vehicleModel) {
        showModal('提示', '请选择车辆型号');
        document.getElementById('vehicleModel').focus();
        return;
    }
    
    // 显示加载提示（在页面A）
    showLoadingModal('检测车辆ID中，请稍后...');
    
    // 检测车辆ID
    checkVehicleId(vehicleId, vehicleIp, vehicleModel);
}

// 检测车辆ID
function checkVehicleId(vehicleId, vehicleIp, vehicleModel) {
    console.log('[配置页面] 开始检测车辆ID:', { vehicleId, vehicleIp, vehicleModel });
    
    fetch('/api/check_vehicle_id', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            vehicle_id: vehicleId,
            ssh_host: vehicleIp,
            ssh_user: null,  // 使用默认配置
            ssh_password: null  // 使用默认配置
        })
    })
    .then(response => {
        console.log('[配置页面] HTTP响应状态:', response.status, response.statusText);
        
        // 检查响应是否成功
        if (!response.ok) {
            // 尝试解析错误响应
            return response.json().then(data => {
                throw new Error(data.message || `HTTP错误: ${response.status}`);
            }).catch(() => {
                throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
            });
        }
        
        return response.json();
    })
    .then(data => {
        console.log('[配置页面] 收到响应数据:', data);
        
        // 隐藏加载弹窗
        hideLoadingModal();
        
        if (data.status === 'error') {
            // 检测失败，在页面A显示错误提示
            console.error('[配置页面] 检测失败:', data.message);
            showModal('错误', data.message || '检测车辆ID失败，请检查网络连接和IP地址');
            return;
        }
        
        if (data.status === 'success') {
            if (data.matched) {
                // 匹配成功，保存配置并跳转到页面B
                console.log('[配置页面] 车辆ID匹配成功，HOSTNAME:', data.hostname);
                saveConfig();
                
                // 构建URL，添加showSuccess参数，让页面B显示成功提示
                const url = `/api/devicetest?hostname=${encodeURIComponent(vehicleId)}&vehiclemodel=${encodeURIComponent(vehicleModel)}&carip=${encodeURIComponent(vehicleIp)}&showSuccess=1&hostnameDetected=${encodeURIComponent(data.hostname)}`;
                console.log('[配置页面] 跳转到测试页面:', url);
                window.location.href = url;
            } else {
                // 匹配失败，在页面A显示错误提示
                console.log('[配置页面] 车辆ID不匹配，输入的ID:', vehicleId, '获取的HOSTNAME:', data.hostname);
                showModal('错误', '您输入的车辆ID与设备不匹配，请重新输入');
            }
        } else {
            // 未知的响应状态
            console.error('[配置页面] 未知的响应状态:', data);
            showModal('错误', '检测车辆ID时收到未知响应，请重试');
        }
    })
    .catch(error => {
        // 隐藏加载弹窗
        hideLoadingModal();
        
        console.error('[配置页面] 检测车辆ID错误:', error);
        // 在页面A显示错误提示
        showModal('错误', '检测车辆ID时发生错误: ' + (error.message || error.toString()));
    });
}

// 加载历史配置（从localStorage读取）
function loadHistoryConfig() {
    const historyConfig = localStorage.getItem('robotTestConfig');
    if (historyConfig) {
        try {
            const config = JSON.parse(historyConfig);
            
            // 填充表单
            if (config.vehicleId) {
                document.getElementById('vehicleId').value = config.vehicleId;
            }
            if (config.vehicleIp) {
                document.getElementById('vehicleIp').value = config.vehicleIp;
            }
            if (config.vehicleType) {
                document.getElementById('vehicleType').value = config.vehicleType;
                // 触发change事件以加载对应的车辆型号
                document.getElementById('vehicleType').dispatchEvent(new Event('change'));
                
                // 等待车辆型号加载完成后再设置值
                setTimeout(() => {
                    if (config.vehicleModel) {
                        document.getElementById('vehicleModel').value = config.vehicleModel;
                    }
                }, 500);
            }
            
            console.log('[配置页面] 历史配置加载成功:', config);
        } catch (error) {
            console.error('[配置页面] 解析历史配置失败:', error);
            alert('加载历史配置失败');
        }
    } else {
        alert('没有找到历史配置');
    }
}

// 保存配置到localStorage（在跳转前保存）
function saveConfig() {
    const config = {
        vehicleId: document.getElementById('vehicleId').value.trim(),
        vehicleIp: document.getElementById('vehicleIp').value.trim(),
        vehicleType: document.getElementById('vehicleType').value,
        vehicleModel: document.getElementById('vehicleModel').value
    };
    
    localStorage.setItem('robotTestConfig', JSON.stringify(config));
    console.log('[配置页面] 配置已保存:', config);
}
