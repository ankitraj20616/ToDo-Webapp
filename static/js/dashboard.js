$(document).ready(function () {
  lucide.createIcons();
  fetchTodos();

  //ADD NEW TODO
  $("#addTodoForm").on("submit", function (e) {
    e.preventDefault();
    const newTodo = $("#newTodo").val().trim();
    if (!newTodo) return;

    $.ajax({
      url: "/insertToDo",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ content: newTodo }),
      success: function () {
        $("#newTodo").val("");
        fetchTodos();
      },
      error: function (err) {
        console.log("Error in adding todo: ", err);
      },
    });
  });

  //DELETE TODO
  $(document).on("click", ".delete-btn", function () {
    const todoId = $(this).closest(".todo-item").data("id");
    $.ajax({
      url: `/deleteTodo?_id=${todoId}`,
      method: "DELETE",
      success: function () {
        fetchTodos();
      },
      error: function (err) {
        console.log("Error deleting todo: ", err);
      },
    });
  });

  //Start Editing todo
  $(document).on("click", ".edit-btn", function () {
    const $todoItem = $(this).closest(".todo-item");
    const currentText = $todoItem.find(".todo-text").text();
    const $editTemplate = $(
      document.getElementById("editTemplate").content.cloneNode(true)
    );
    $editTemplate.find(".edit-input").val(currentText);

    $todoItem.html($editTemplate);
    $todoItem.find(".edit-input").focus();

    // Re-initialize Lucide icons for the new buttons
    lucide.createIcons();
  });
  //CANCEL EDIT
  $(document).on("click", ".cancel-btn", function () {
    fetchTodos();
  });

  // Confirm edit
  $(document).on("click", ".confirm-btn", function () {
    const $todoItem = $(this).closest(".todo-item");
    const todoId = $todoItem.data("id");
    const newContent = $todoItem.find(".edit-input").val().trim();

    if (!newContent) return;

    $.ajax({
      url: `/updateTodo?_id=${todoId}`,
      method: "PUT",
      contentType: "application/json",
      data: JSON.stringify({ content: newContent }),
      success: function () {
        fetchTodos();
      },
      error: function (err) {
        console.error("Error updating todo:", err);
      },
    });
  });

  $("#logoutButton").on("click", function () {
    localStorage.removeItem("token");
    window.location.href = "/";
  });

  function fetchTodos() {
    $.ajax({
      url: "/readTodos",
      method: "GET",
      success: function (data) {
        renderTodos(data.todo);
      },
      error: function (err) {
        console.log("Error fetching todos: ", err);
      },
    });
  }

  function renderTodos(todos) {
    console.log("Fetched Data: ", todos);
    const $todoList = $("#todoList");
    $todoList.empty();
    todos.forEach((todo) => {
      const $todoTemplate = $(
        document.getElementById("todoTemplate").content.cloneNode(true)
      );

      const $todoItem = $todoTemplate.find(".todo-item");
      $todoItem.attr("data-id", todo._id);
      $todoItem.find(".todo-text").text(todo.content);

      $todoList.append($todoTemplate);
    });
    lucide.createIcons();
  }
});
