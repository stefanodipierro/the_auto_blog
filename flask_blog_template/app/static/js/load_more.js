let page = 1;

    window.onscroll = function() {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        // User is at the bottom. Load more posts.
        page++;
        fetch('/load_more/' + page)
          .then(response => response.json())
          .then(data => {
            // Add the new posts to the page.
            for (let post of data) {
              let postElement = createPostElement(post);  // You will need to implement this function.
              document.getElementById('posts-container').appendChild(postElement);
            }
          });
      }
    };

    function createPostElement(post) {
      // Create a new post card.
      let card = document.createElement('div');
      card.className = 'card';
      card.style.width = '18rem';

      // Create the image.
      let img = document.createElement('img');
      img.src = post.images[0];
      img.className = 'card-img-top';
      img.alt = '...';
      card.appendChild(img);

      // Create the card body.
      let body = document.createElement('div');
      body.className = 'card-body';

      // Add the title.
      let title = document.createElement('h5');
      title.className = 'card-title';
      title.textContent = post.title;
      body.appendChild(title);

      // Add the description.
      let text = document.createElement('p');
      text.className = 'card-text';
      text.textContent = post.description;
      body.appendChild(text);

      // Add the stretched link.
      let link = document.createElement('a');
      link.href = '/post/' + post.id;
      link.className = 'stretched-link';
      body.appendChild(link);

      // Add the body to the card.
      card.appendChild(body);

      return card;
    }