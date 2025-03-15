// Открытие деталей задачи
function openTaskDetails(taskId) {
	fetch(`/task-details/${taskId}/`)
			.then(response => response.json())
			.then(data => {
					document.getElementById("task-title").textContent = data.name;
					document.getElementById("task-description").textContent = data.description;
					document.getElementById("task-status").textContent = data.status;
					document.getElementById("task-menu").style.display = "block";
			})
			.catch(error => console.error("Ошибка загрузки данных:", error));
}

// Закрытие деталей задачи
function closeTaskDetails() {
	document.getElementById("task-menu").style.display = "none";
}

// Удаление задачи
function deleteTask(event, taskId) {
	event.stopPropagation(); // Останавливаем всплытие события, чтобы не открывалось меню
	
	fetch(`/delete-task/${taskId}/`, { 
			method: "POST", 
			headers: { 
					"X-CSRFToken": getCSRFToken() 
			} 
	})
	.then(response => {
			if (response.ok) {
					document.getElementById(`task-${taskId}`).remove();
			} else {
					console.error("Ошибка при удалении задачи.");
			}
	})
	.catch(error => console.error("Ошибка:", error));
}

// Функция для получения CSRF-токена из cookies
function getCSRFToken() {
	let cookieValue = null;
	let cookies = document.cookie.split("; ");
	for (let cookie of cookies) {
			if (cookie.startsWith("csrftoken=")) {
					cookieValue = cookie.split("=")[1];
					break;
			}
	}
	return cookieValue;
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
	// Открывает форму добавления задачи
	const openFormBtn = document.getElementById('open-form-btn');
	if (openFormBtn) {
			openFormBtn.addEventListener('click', function() {
					var form = document.getElementById('task-form');
					form.style.display = form.style.display === 'none' ? 'block' : 'none';
			});
	}

	// Обработка успешной отправки формы
	document.body.addEventListener("htmx:afterRequest", function(event) {
			if (event.detail.successful) {
					let formContainer = document.getElementById("task-form");  
					let formElement = document.getElementById("task-form-element");  

					if (formElement) {
							formElement.reset(); 
					}
					if (formContainer) {
							formContainer.style.display = "none"; 
					}
			}
	});
});