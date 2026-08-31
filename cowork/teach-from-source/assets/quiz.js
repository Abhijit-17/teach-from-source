/* Quiz behavior — pairs with .quiz styles in lesson.css.
   Copied into ./assets/quiz.js on workspace init; every lesson with a quiz
   loads it via <script src="../assets/quiz.js" defer></script>.

   Markup contract:
   <div class="quiz" data-answer="b">
     <p class="q">Question text? <a class="cite" href="...">[p. 118]</a></p>
     <button data-key="a">Option one</button>
     <button data-key="b">Option two</button>
     <div class="explain">Why b is right, with locator.</div>
   </div>

   Feedback is border + written explanation, never colour alone. */

document.addEventListener('click', function (e) {
  var btn = e.target.closest('.quiz button');
  if (!btn || btn.disabled) return;

  var quiz = btn.closest('.quiz');
  var answer = quiz.dataset.answer;
  var correct = btn.dataset.key === answer;

  btn.classList.add(correct ? 'correct' : 'wrong');
  quiz.querySelectorAll('button').forEach(function (b) {
    if (b.dataset.key === answer) b.classList.add('correct');
    b.disabled = true;
  });
  quiz.classList.add('answered');

  // Record for spaced re-testing: lessons can read this back next visit.
  try {
    var log = JSON.parse(localStorage.getItem('quiz-log') || '[]');
    log.push({
      lesson: location.pathname.split('/').pop(),
      quiz: quiz.id || null,
      correct: correct,
      at: new Date().toISOString()
    });
    localStorage.setItem('quiz-log', JSON.stringify(log));
  } catch (_) { /* file:// or storage disabled — quiz still works */ }
});
