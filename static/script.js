document.addEventListener('DOMContentLoaded', function () {
  // Process button click handler
  document.getElementById('process-btn').addEventListener('click', function () {
    const processingIndicator = document.getElementById('processing-indicator');
    const resultsSection = document.getElementById('results');
    processingIndicator.classList.remove('hidden');
    resultsSection.style.display = 'none';
  });

  // Star rating system
  let selectedRating = 0;
  const stars = document.querySelectorAll(".star");

  stars.forEach((star) => {
    star.addEventListener("click", function () {
      selectedRating = parseInt(this.getAttribute("data-value"));
      updateStars(selectedRating);
      const feedbackText = document.getElementById("feedback-text");
      feedbackText.style.display = selectedRating <= 2 ? 'block' : 'none';
    });

    star.addEventListener("mouseenter", function () {
      const value = parseInt(this.getAttribute("data-value"));
      updateStars(value, true);
    });

    star.addEventListener("mouseleave", function () {
      updateStars(selectedRating);
    });
  });

  function updateStars(rating, isHover = false) {
    stars.forEach((star) => {
      const value = parseInt(star.getAttribute("data-value"));
      star.textContent = value <= rating ? "★" : "☆";
      star.style.color = (value <= rating) ? "#ffc107" : (isHover ? "#ccc" : "#ffc107");
    });
  }

  // Feedback submission
  document.getElementById("submit-feedback").addEventListener("click", function () {
    const feedbackMessage = document.getElementById("feedback-message");

    if (selectedRating === 0) {
      feedbackMessage.textContent = 'Please select a rating first';
      feedbackMessage.style.color = 'red';
      return;
    }

    feedbackMessage.textContent = 'Thank you for your feedback!';
    feedbackMessage.style.color = 'green';

    const feedbackData = {
      rating: selectedRating,
      comment: document.getElementById("feedback-text").value,
      newsContent: document.querySelector('.content-box p').textContent,
      prediction: document.querySelector('.tag-fake, .tag-real').textContent
    };

    console.log('Feedback data:', feedbackData);
  });

  // Auto-expand textarea
  document.getElementById('feedback-text').addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
  });

  // YES/NO feedback buttons
  const yesBtn = document.getElementById("yes-btn");
  const noBtn = document.getElementById("no-btn");
  const feedbackSummary = document.getElementById("vote-summary");
  const newsText = document.querySelector(".content-box p")?.textContent;

  if (yesBtn && noBtn && newsText) {
    let votes = JSON.parse(localStorage.getItem("userVotes") || "{}");

    function saveVote(news, vote) {
      votes[news] = vote;
      localStorage.setItem("userVotes", JSON.stringify(votes));
      showVoteSummary(vote);
    }

    function showVoteSummary(vote) {
      feedbackSummary.innerText =
        vote === "yes"
          ? "✅ Most users agreed this news is correct."
          : "❌ Most users said this news is not correct.";
      feedbackSummary.style.display = "block";
    }

    // Load previous vote
    if (votes[newsText]) {
      showVoteSummary(votes[newsText]);
    }

    yesBtn.addEventListener("click", () => saveVote(newsText, "yes"));
    noBtn.addEventListener("click", () => saveVote(newsText, "no"));
  }
});
