$(document).ready(() => {
  const $loginForm = $("#loginForm");
  const $signupForm = $("#signupForm");
  const $switchForm = $("#switchForm");
  const $formTitle = $("#formTitle");
  const $formDescription = $("#formDescription");
  const $message = $("#message");

  let isLoginFrom = true;
  function toggleForm() {
    isLoginFrom = !isLoginFrom;
    $loginForm.toggle();
    $signupForm.toggle();

    if (isLoginFrom) {
      $formTitle.text("Log In");
      $formDescription.text("Enter your credentials to access your account");
      $switchForm.text("Need an account? Sign up");
    } else {
      $formTitle.text("Sign up");
      $formDescription.text("Create a new account to get started");
      $switchForm.text("Already have an account? Log in");
    }
    $message.empty().removeClass("success error");
  }
  $switchForm.on("click", toggleForm);
  function handleSubmit(event, isLogin) {
    event.preventDefault();

    const loginData = JSON.stringify({
      email: $("#loginEmail").val(),
      password: $("#loginPassword").val(),
    });
    const signupData = JSON.stringify({
      name: $("#signupName").val(),
      email: $("#signupEmail").val(),
      password: $("#signupPassword").val(),
    });

    $.ajax({
      url: isLogin ? "/logIn" : "/signUp",
      method: "POST",
      data: isLogin ? loginData : signupData,
      contentType: "application/json",
      success: (response) => {
        if (response.token) {
          $message
            .text(response.message)
            .addClass("success")
            .removeClass("error");
          localStorage.setItem("token", response.token);
          console.log("Token saved: ", localStorage.getItem("token"));
          document.cookie = `token=${response.token}; path=/;`;
          window.location.href = `/dashboard`;
        } else {
          $message
            .text(response.message)
            .addClass("error")
            .removeClass("success");
        }
      },
      error: () => {
        $message
          .text("An error occurred. Please try again.")
          .addClass("error")
          .removeClass("success");
      },
    });
  }

  $loginForm.on("submit", (event) => {
    handleSubmit(event, true);
  });

  $signupForm.on("submit", (event) => {
    handleSubmit(event, false);
  });
});
