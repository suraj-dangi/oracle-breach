window.addEventListener('DOMContentLoaded', e => {
  const searchElement = document.getElementById('domainInput');
  const resultElement = document.getElementById('result');

  // Handle Enter key press
  searchElement.addEventListener('keypress', e => {
      if (e.key === 'Enter') checkDomain();
  });

  async function checkDomain() {
      const domain = searchElement.value.trim();

      if (!domain) {
          showResult('Please enter a domain name', true);
          return;
      }

      try {
          // Send request to server
          const response = await fetch('/search', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: `domain=${encodeURIComponent(domain)}`
          });

          const data = await response.json();

          if (data.error) {
              showResult(`Error: ${data.error}`, true);
              return;
          }

          let resultHTML = '';

          if (data.found) {
              resultHTML = `<strong>${domain}</strong> appears in the breach list.<p>Please follow the recommendations given below.</p>`;
              resultElement.className = 'breach';
          } else {
              resultHTML = `<strong>${domain}</strong> does not appear in the breach list.`;
              resultElement.className = 'safe';
          }

          // Show partial matches if any
          if (data.partial_matches && data.partial_matches.length > 0) {
              resultHTML += `
                  <div class="partial-matches">
                      <p>Similar domains found in the database:</p>
                      <pre>${data.partial_matches.join('\n')}</pre>
                  </div>
              `;
          }

          resultElement.innerHTML = resultHTML;
          resultElement.style.display = 'block';

      } catch (error) {
          showResult('An error occurred while checking the domain', true);
          console.error('Error:', error);
      }
  }

  function showResult(message, isError) {
      resultElement.innerHTML = message;
      resultElement.className = isError ? 'breach' : 'safe';
      resultElement.style.display = 'block';
  }
}, {once: true});
