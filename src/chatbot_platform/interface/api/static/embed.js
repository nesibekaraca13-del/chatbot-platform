(function () {
  var currentScript = document.currentScript;
  var origin = new URL(currentScript.src).origin;

  var button = document.createElement("button");
  button.setAttribute("aria-label", "Sohbeti aç/kapat");
  button.textContent = "💬";
  button.style.cssText =
    "position:fixed;bottom:20px;right:20px;width:56px;height:56px;border-radius:50%;" +
    "background:#0d6efd;color:#fff;border:none;font-size:24px;cursor:pointer;" +
    "box-shadow:0 2px 8px rgba(0,0,0,0.3);z-index:2147483647;";

  var frame = document.createElement("iframe");
  frame.src = origin + "/static/widget.html";
  frame.title = "Chatbot";
  frame.style.cssText =
    "position:fixed;bottom:88px;right:20px;width:360px;height:520px;max-width:calc(100vw - 40px);" +
    "max-height:calc(100vh - 120px);border:none;border-radius:12px;" +
    "box-shadow:0 4px 16px rgba(0,0,0,0.3);z-index:2147483647;display:none;";

  var isOpen = false;
  button.addEventListener("click", function () {
    isOpen = !isOpen;
    frame.style.display = isOpen ? "block" : "none";
  });

  document.body.appendChild(frame);
  document.body.appendChild(button);
})();
