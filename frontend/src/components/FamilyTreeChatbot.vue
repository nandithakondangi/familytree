<template>
  <div class="flex flex-col h-64 bg-indigo-50 rounded-lg">
    <div class="flex-grow overflow-y-auto p-3 text-sm">
      <div v-for="(message, index) in messages" :key="index" :class="['mb-2', message.sender === 'user' ? 'text-right' : 'text-left']">
        <span :class="['inline-block p-2 rounded-lg max-w-xs', message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-800']">
          {{ message.text }}
        </span>
      </div>
       <div ref="chatEnd"></div> </div>

    <div class="flex p-3 border-t border-gray-200">
      <input
        type="text"
        v-model="currentMessage"
        @keyup.enter="sendMessage"
        placeholder="Ask about the family tree..."
        class="flex-grow px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
      />
      <button
        @click="sendMessage"
        :disabled="!currentMessage.trim()"
        class="px-6 py-2 bg-indigo-600 text-white font-medium rounded-r-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';

export default {
  name: 'FamilyTreeChatbot', // Renamed to a multi-word name
  data() {
    return {
      messages: [], // Array to hold chat messages { sender: 'user' | 'bot', text: '...' }
      currentMessage: '',
    };
  },
  methods: {
    sendMessage() {
      if (this.currentMessage.trim()) {
        const userMessage = this.currentMessage.trim();
        this.messages.push({ sender: 'user', text: userMessage });
        this.currentMessage = '';
        this.scrollToEnd(); // Scroll to the latest message

        // TODO: Send userMessage to backend chatbot API
        // Replace with your actual backend endpoint
        fetch('/api/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage }),
        })
        .then(response => {
          if (!response.ok) {
            throw new Error('Chatbot API failed.');
          }
          return response.json(); // Assuming backend returns JSON with a 'reply' field
        })
        .then(data => {
          const botReply = data.reply || 'Sorry, I could not process your request.';
          this.messages.push({ sender: 'bot', text: botReply });
          this.scrollToEnd(); // Scroll to the latest message
        })
        .catch(error => {
          console.error('Error with chatbot API:', error);
          this.messages.push({ sender: 'bot', text: `Error: ${error.message}` });
           this.scrollToEnd(); // Scroll to the latest message
        });
      }
    },
    scrollToEnd() {
      nextTick(() => {
        const chatEnd = this.$refs.chatEnd;
        if (chatEnd) {
          chatEnd.scrollIntoView({ behavior: 'smooth' });
        }
      });
    },
  },
};
</script>

<style scoped>
/* Scoped styles for the chatbot if needed */
</style>
