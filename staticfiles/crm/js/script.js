document.addEventListener("DOMContentLoaded", function () {
	document.querySelectorAll(".task-item").forEach(item => {
			item.addEventListener("click", function () {
					let taskId = this.getAttribute("data-task-id");

					fetch(`/task/${taskId}/`)
							.then(response => response.json())
							.then(data => {
									document.getElementById("task-title").innerText = data.name;
									document.getElementById("task-description").innerText = data.description;
									document.getElementById("task-status").innerText = data.status_display;

									document.getElementById("task-menu").style.display = "block";
							})
							.catch(error => console.error("Ошибка загрузки данных:", error));
			});
	});
});


