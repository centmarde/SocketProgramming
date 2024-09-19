<script lang="ts">
  import { onMount } from 'svelte';
  import { io, Socket } from 'socket.io-client';

  let socket: Socket;
  let message = '';
  let chatHistory: { type: string; text: string }[] = [];

  async function fetchChatHistory() {
      const response = await fetch('http://localhost:5000/messages');
      const data = await response.json();
      chatHistory = data.flatMap((msg) => [
        { type: 'user', text: msg.message },
        { type: 'bot', text: msg.response }
      ]).reverse(); // Reverse to show most recent at the top
  }

  onMount(() => {
      fetchChatHistory();
      
      socket = io('http://localhost:5000');

      socket.on('connect', () => {
          console.log('Socket connected');
      });

      socket.on('new_message', (data: { message: string, response: string }) => {
          console.log('New message received:', data);
          // Prepend new messages to the chat history
          chatHistory = [
            { type: 'user', text: data.message },
            { type: 'bot', text: data.response },
            ...chatHistory
          ];

          // Scroll to the top of chat after new message
          setTimeout(() => {
              const chatBox = document.querySelector('.chat-box');
              if (chatBox) {
                  chatBox.scrollTop = 0; // Scroll to the top
              }
          }, 100);
      });
  });

  function sendMessage() {
      if (message.trim() !== '' && socket?.connected) {
          console.log('Sending message:', message);
          socket.emit('send_message', { message });
          message = ''; // Clear the input field after sending
      }
  }

  function handleKeypress(event: KeyboardEvent) {
      if (event.key === 'Enter') {
          sendMessage();
      }
  }

  function clearChat() {
      socket.emit('clear_chat'); 
      window.location.reload();
  }
</script>
<br><br><br><br><br><br><br>
<main class="container">
  <div class="row">
    <div class="col-12"> <h1>Socket.AI Chat</h1>
      <div class="input-group mb-3">
        <input bind:value={message} class="form-control" placeholder="Type a message" on:keypress={handleKeypress} />
        <button class="btn btn-primary" on:click={sendMessage}>Send</button>
        <button class="btn btn-danger" on:click={clearChat}>Clear Chat</button>
      </div>
    
      <div class="chat-box mb-3">
        <h5>Chat History</h5>
        {#each chatHistory as { type, text }}
          <div class={`message ${type}`}>
            {#if type === 'user'}
            {text}<strong> :User</strong> 
            {:else}
              <strong>Bot:</strong> {text}
            {/if}
          </div>
        {/each}
      </div></div>
  </div>
 
</main>

<style>
  h1 {
    text-align: center;
    margin-bottom: 20px;
  }
  .chat-box {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ebeaea;
    background-color: aliceblue;
    padding: 2px;
    border-radius: 5px;
  }
  .message {
    margin-bottom: 10px;
  }
  .message.user {
    text-align: right;
  }
  .message.bot {
    text-align: left;
  }
</style>
