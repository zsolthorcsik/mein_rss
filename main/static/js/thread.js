
function showThreadSelectionPopup(topicId, topicName) {
  // Show the popup
  document.getElementById("threadSelectionPopup").style.display = "block";

  // Get the threadList element
  const threadList = document.getElementById("threadList");

  // AJAX request to fetch the user's threads
  // Replace the URL with the appropriate endpoint or view in your Django app
  fetch("/get_user_threads/")
    .then(response => response.json())
    .then(data => {
      // Clear the existing thread list items
      threadList.innerHTML = "";

      // Populate the thread list
      data.forEach(thread => {
        // Create a list item for each thread
        const listItem = document.createElement("li");
        listItem.textContent = thread.name;

        // Create a plus button
        const plusButton = document.createElement("button");
        plusButton.textContent = "+";
        plusButton.addEventListener("click", () => {
          // Function to associate the topic with the selected thread
          addToThread(thread.id, topicId, topicName);
        });

        // Append the plus button to the list item
        listItem.appendChild(plusButton);

        // Append the list item to the thread list
        threadList.appendChild(listItem);
      });
    })
    .catch(error => {
      console.error("Error:", error);
    });
}

function addToThread(threadId, topicId, topicName) {
  // AJAX request to associate the topic with the selected thread
  // Replace the URL with the appropriate endpoint or view in your Django app  
  console.log(topicId, topicName, threadId);
  fetch(`/add_topic_to_thread/${threadId}/`, {    
    method: "POST",
    body: JSON.stringify({ topicId: topicId, topicName: topicName }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken, // Include the CSRF token for Django
    },
  })
    .then(response => response.json())
    .then(data => {
      // Handle the response or perform any necessary actions
      console.log("Topic added to thread:", data.threadId);
    })
    .catch(error => {
      console.error("Error:", error);
    });
}
