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
      ]);
  }

  onMount(() => {
      fetchChatHistory();
      
      socket = io('http://localhost:5000');

      socket.on('connect', () => {
          console.log('Socket connected');
      });

      socket.on('new_message', (data: { message: string, response: string }) => {
          console.log('New message received:', data);
          // Update chat history reactively
          chatHistory = [...chatHistory, { type: 'user', text: data.message }, { type: 'bot', text: data.response }];

          // Scroll to the bottom of chat after new message
          setTimeout(() => {
              const chatBox = document.querySelector('.chat-box');
              if (chatBox) {
                  chatBox.scrollTop = chatBox.scrollHeight;
              }
          }, 100);
      });
  });

  function sendMessage() {
      if (message.trim() !== '' && socket?.connected) {
          console.log('Sending message:', message);
          socket.emit('send_message', { message });
        /*   chatHistory = [...chatHistory, { type: 'user', text: message }]; // Update immediately */
          message = '';
      }
  }

  function handleKeypress(event: KeyboardEvent) {
      if (event.key === 'Enter') {
          sendMessage();
      }
  }
</script>

<main class="container">
  <h1>Real-Time Socket.io Chat</h1>
  <div class="input-group mb-3">
    <input bind:value={message} class="form-control" placeholder="Type a message" on:keypress={handleKeypress} />
    <button class="btn btn-primary" on:click={sendMessage}>Send</button>
  </div>

  <div class="chat-box mb-3">
    {#each chatHistory as { type, text }}
      <div class={`message ${type}`}>
        {#if type === 'user'}
          <strong>User:</strong> {text}
        {:else}
          <strong>Bot:</strong> {text}
        {/if}
      </div>
    {/each}
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
    border: 1px solid #ccc;
    padding: 10px;
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
