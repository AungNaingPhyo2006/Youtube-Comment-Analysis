function fetchData() {
    const input = document.getElementById('videoUrl').value.trim();
      if (!input) {
       alert('Please enter a valid YouTube video URL.');
      return; 
      }
     const youtubeRegex = /^https:\/\/www\.youtube\.com\/watch\?v=[\w-]{11}$/;
    //  const youtubeRegex = /^https:\/\/www\.youtube\.com\/watch\?v=[a-zA-Z0-9_-]{11}$/;
      if (!youtubeRegex.test(input)) {
          alert('Please enter a valid YouTube video URL starting with "https://www.youtube.com/watch?v="');
          return; 
      }


      document.getElementById('loading').style.display = 'block';
      document.getElementById('results').style.display = 'none';
      document.getElementById('analysis').style.display = 'none'; 



      const videoUrl = document.getElementById('videoUrl').value;
      fetch(`http://127.0.0.1:5000/api/comments/${encodeURIComponent(videoUrl)}`)
          .then(response => response.json())
          .then(data => {
             console.log('data=>', data.positive_comments)
              document.getElementById('loading').style.display = 'none';
              document.getElementById('results').style.display = 'block';
              document.getElementById('analysis').style.display = 'block'; 

              const avgPolarityPercentage = (data.average_polarity * 100).toFixed(2);
              document.getElementById('videoTitle').innerText = `Video Title: ${data.title}`;
              document.getElementById('avgPolarity').innerText = `Average Polarity: ${avgPolarityPercentage}%`;
              document.getElementById('positiveCount').innerText = `Positive Comments Count: ${data.positive_comments_count}`;
              document.getElementById('negativeCount').innerText = `Negative Comments Count: ${data.negative_comments_count}`;
              document.getElementById('neutralCount').innerText = `Neutral Comments Count: ${data.neutral_comments_count}`;
              document.getElementById('chart').src = `data:image/png;base64,${data.chart}`;

              populateCommentList('positiveCommentsList', data.positive_comments);
              populateCommentList('negativeCommentsList', data.negative_comments);
              populateCommentList('neutralCommentsList', data.neutral_comments);

          })
          .catch(error => {
              document.getElementById('loading').style.display = 'none';
              document.getElementById('results').style.display = 'none';
              document.getElementById('analysis').style.display = 'none'; 

              console.error('Error:', error);
          });
  }

  function populateCommentList(elementId, comments) {
    const list = document.getElementById(elementId);
    list.innerHTML = ''; // Clear any existing content

    comments.forEach(comment => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `<strong class="comment-author">${comment.author}</strong>: ${comment.text}`; // Format as "Author: Comment"
        list.appendChild(listItem);
    });
}

  function clearInput() {
      document.getElementById('videoUrl').value = '';
      document.getElementById('loading').style.display = 'none';
      document.getElementById('results').style.display = 'none';
      document.getElementById('analysis').style.display = 'none';

  }

  document.addEventListener('DOMContentLoaded', () => {
    const heading = document.getElementById('animated-heading');
    const text = heading.innerText;
    heading.innerHTML = ''; 

    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char === ' ') {
            heading.innerHTML += ' '; // Preserve spaces
        } else {
            heading.innerHTML += `<span>${char}</span>`;
        }
    }

    heading.classList.add('dancing-text');

    const inputField = document.getElementById('videoUrl');

    inputField.addEventListener('focus', () => {
        heading.classList.add('no-animation');
    });

    inputField.addEventListener('blur', () => {
        heading.classList.remove('no-animation');
    });
});
