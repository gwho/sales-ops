// Shared quiz widget for the teaching workspace.
// Markup contract:
// <div class="quiz" data-quiz>
//   <p class="quiz-question">...</p>
//   <div class="quiz-options">
//     <button class="quiz-option" data-correct="false">...</button>
//     <button class="quiz-option" data-correct="true">...</button>
//   </div>
//   <p class="quiz-feedback" hidden></p>
// </div>
// One option per quiz should have data-correct="true". Clicking any option
// locks the quiz, marks the chosen option, reveals the correct one if the
// learner missed it, and writes feedback text.

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-quiz]").forEach((quiz) => {
    const options = quiz.querySelectorAll(".quiz-option");
    const feedback = quiz.querySelector(".quiz-feedback");

    options.forEach((option) => {
      option.addEventListener("click", () => {
        if (quiz.hasAttribute("data-answered")) return;
        quiz.setAttribute("data-answered", "true");

        const chosenCorrect = option.dataset.correct === "true";

        options.forEach((opt) => {
          if (opt.dataset.correct === "true") {
            opt.classList.add("is-correct");
          } else if (opt === option) {
            opt.classList.add("is-incorrect");
          }
        });

        if (feedback) {
          feedback.hidden = false;
          feedback.textContent = chosenCorrect
            ? "Correct."
            : "Not quite — the correct answer is highlighted above.";
          feedback.classList.add(chosenCorrect ? "is-correct" : "is-incorrect");
        }
      });
    });
  });
});
