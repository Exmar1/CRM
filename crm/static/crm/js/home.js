
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                    }
            }
    }
    return cookieValue;
}


function toggleTaskForm() {
    const taskForm = document.getElementById('task-form');
    const taskFormElement = document.getElementById('task-form-element');

    if (taskForm) {
            if (taskForm.style.display === 'none' || taskForm.style.display === '') {
                    taskForm.style.display = 'block';
                    console.log('Форма открыта');
            } else {
                    taskForm.style.display = 'none';
                    if (taskFormElement) {
                            taskFormElement.reset();
                    }
                    console.log('Форма закрыта');
            }
    } else {
            console.error('Элемент формы не найден');
    }
}


function deleteTaskConfirm(event, taskId) {
    event.preventDefault();

    if (!taskId) {
            alert("Ошибка: ID задачи не найден.");
            return;
    }

    if (confirm("Вы уверены, что хотите удалить задачу?")) {
            fetch(`/task/${taskId}/delete/`, {
                    method: "DELETE",
                    headers: {
                            "X-CSRFToken": getCookie('csrftoken')
                    }
            })
            .then(response => {
                    if (response.ok) {
                            window.location.reload();
                    } else {
                            alert("Ошибка при удалении задачи.");
                    }
            });
    }
}


function updateStats() {
    fetch('/get_stats/')
            .then(response => response.json())
            .then(data => {
                    document.querySelector('[data-stat="new"] .number').textContent = data.new;
                    document.querySelector('[data-stat="in_progress"] .number').textContent = data.in_progress;
                    document.querySelector('[data-stat="completed"] .number').textContent = data.completed;
                    document.querySelector('[data-stat="total"] .number').textContent = data.total;
                    console.log('Статистика обновлена');
            })
            .catch(error => {
                    console.error('Ошибка при обновлении статистики:', error);
            });
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM загружен, инициализация скриптов');

    
    const openFormBtn = document.getElementById('open-form-btn');
    const addTaskBtn = document.querySelector('.add-task-btn');
    
    
    const statusFilter = document.getElementById('status-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const sortFilter = document.getElementById('sort-filter');
    const tabs = document.querySelectorAll('.tab');

    
    updateStats();

    if (openFormBtn) {
        openFormBtn.addEventListener('click', function (e) {
                e.preventDefault();
                toggleTaskForm();
                console.log('Клик по кнопке открытия формы');
        });
    }
  
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', function (e) {
                e.preventDefault();
                toggleTaskForm();
                console.log('Клик по кнопке плюсик');
        });
    }

     
     const taskFormElement = document.getElementById('task-form-element');

    
    if (taskFormElement) {
        taskFormElement.addEventListener('submit', function(e) {
            e.preventDefault();

            
            if (taskFormElement.dataset.submitting === "true") {
                console.log('Форма уже отправляется');
                return;
            }
            
            
            taskFormElement.dataset.submitting = "true";

            console.log('Отправка формы задачи');

            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.text();
                }
                throw new Error('Ошибка при отправке формы');
            })
            .then(html => {
                const emptyList = document.querySelector('.empty-list');
                if (emptyList) {
                    emptyList.remove();
                    
                    if (!document.getElementById('task-list')) {
                        const tasksContainer = document.querySelector('.tasks-container');
                        const taskList = document.createElement('ul');
                        taskList.id = 'task-list';
                        tasksContainer.appendChild(taskList);
                    }
                }
                
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const newTask = temp.firstElementChild;
                
                document.getElementById('task-list').appendChild(newTask);
                
                updateStats();
                
                taskFormElement.reset();
                toggleTaskForm();
                console.log('Задача успешно добавлена');
            })
            .catch(error => {
                console.error('Ошибка:', error);
            })
            .finally(() => {
            
                taskFormElement.dataset.submitting = "false";
            });
        });
    }

    
    const cancelBtn = document.getElementById('cancel-task-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleTaskForm(); 
            console.log('Клик по кнопке отмены');
        });
    }

    // Функция применения фильтров
    function applyFilters() {
        const statusValue = statusFilter ? statusFilter.value : '';
        const priorityValue = priorityFilter ? priorityFilter.value : '';
        const sortValue = sortFilter ? sortFilter.value : '';
        
        const tasks = document.querySelectorAll('#task-list .task-item');
        console.log('Применение фильтров:', { statusValue, priorityValue, sortValue });
        
        // Сначала отфильтруем задачи
        tasks.forEach(task => {
            let display = true;
            
            // Фильтр по статусу
            if (statusValue && statusValue !== '') {
                const statusElement = task.querySelector('.status-badge');
                if (statusElement && !statusElement.classList.contains('status-' + statusValue)) {
                    display = false;
                }
            }
            
            // Фильтр по приоритету
            if (priorityValue && priorityValue !== '') {
                if (!task.classList.contains('priority-' + priorityValue)) {
                    display = false;
                }
            }
            
            task.style.display = display ? '' : 'none';
        });
        
        // Затем отсортируем видимые задачи
        if (sortValue) {
            const taskList = document.getElementById('task-list');
            if (taskList) {
                const items = Array.from(taskList.children).filter(item => item.style.display !== 'none');
                
                items.sort((a, b) => {
                    if (sortValue === 'deadline') {
                        const dateA = a.querySelector('.deadline')?.getAttribute('data-date') || '';
                        const dateB = b.querySelector('.deadline')?.getAttribute('data-date') || '';
                        return dateA.localeCompare(dateB);
                    } else if (sortValue === 'priority') {
                        const priorityClasses = ['priority-high', 'priority-medium', 'priority-low'];
                        const priorityA = priorityClasses.findIndex(cls => a.classList.contains(cls));
                        const priorityB = priorityClasses.findIndex(cls => b.classList.contains(cls));
                        return priorityA - priorityB;
                    } else if (sortValue === 'name') {
                        const nameA = a.querySelector('h3')?.textContent || '';
                        const nameB = b.querySelector('h3')?.textContent || '';
                        return nameA.localeCompare(nameB);
                    }
                    return 0;
                });
                
                // Переставляем элементы в DOM
                items.forEach(item => {
                    taskList.appendChild(item);
                });
            }
        }
    }

    // Обработчики фильтров
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
    
    if (priorityFilter) {
        priorityFilter.addEventListener('change', applyFilters);
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', applyFilters);
    }

    // Обработчики вкладок
    if (tabs.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Активация выбранной вкладки
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                const today = new Date().toISOString().split('T')[0]; // Текущая дата в формате YYYY-MM-DD
                const tasks = document.querySelectorAll('#task-list .task-item');
                console.log('Клик по вкладке:', filter);
                
                tasks.forEach(task => {
                    const deadlineEl = task.querySelector('.deadline');
                    if (deadlineEl) {
                        const deadline = deadlineEl.getAttribute('data-date');
                        
                        if (filter === 'all') {
                            task.style.display = '';
                        } else if (filter === 'today') {
                            task.style.display = deadline === today ? '' : 'none';
                        } else if (filter === 'upcoming') {
                            task.style.display = deadline > today ? '' : 'none';
                        }
                    }
                });
            });
        });
    }
});