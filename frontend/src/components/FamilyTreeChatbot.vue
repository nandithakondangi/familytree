<template>
  <div ref="chatbotRootEl" class="flex flex-col h-full bg-slate-400/40 dark:bg-slate-700/40 backdrop-blur-lg rounded-xl shadow-xl">
    <div ref="messageAreaEl" class="flex-grow h-0 overflow-y-auto p-3 text-sm">
      <div v-for="(message, index) in messages" :key="index" :class="['mb-2', message.sender === 'user' ? 'text-right' : 'text-left']">
        <span :class="['inline-block p-2 rounded-lg max-w-xs shadow-md', message.sender === 'user' ? 'bg-blue-500/80 dark:bg-blue-600/80 backdrop-blur-sm text-white' : 'bg-gray-400/70 dark:bg-slate-600/70 backdrop-blur-sm text-gray-800 dark:text-gray-200']">
          {{ message.text }}
        </span>
      </div>
       <div ref="chatEnd"></div> </div>

    <div class="flex p-3 border-t border-white/30 dark:border-slate-600/50">
      <input
        type="text"
        v-model="currentMessage"
        @keyup.enter="sendMessage"
        placeholder="Ask about the family tree..."
        class="flex-grow px-3 py-2 bg-white/50 dark:bg-slate-600/60 backdrop-blur-sm border border-gray-300/50 dark:border-slate-500/50 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent text-sm text-gray-800 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400"
      />
      <button
        @click="sendMessage"
        :disabled="!currentMessage.trim()"
        class="px-6 py-2 bg-indigo-600/80 dark:bg-indigo-500/80 backdrop-blur-sm text-white font-medium rounded-r-lg hover:bg-indigo-700/90 dark:hover:bg-indigo-400/90 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-white/20 dark:focus:ring-offset-slate-700/40 transition duration-150 ease-in-out shadow-md disabled:opacity-60 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script>
import { nextTick, ref, onMounted, onUpdated } from 'vue';

export default {
  name: 'FamilyTreeChatbot', // Renamed to a multi-word name
  setup() {
    const chatbotRootEl = ref(null);
    const messageAreaEl = ref(null);
    const chatEnd = ref(null);

    const logHeights = (lifecycleHookName) => {
      if (chatbotRootEl.value && messageAreaEl.value) {
        console.log(`[Chatbot - ${lifecycleHookName}] Root height: ${chatbotRootEl.value.offsetHeight}px, Message Area height: ${messageAreaEl.value.offsetHeight}px`);
      } else {
        console.log(`[Chatbot - ${lifecycleHookName}] Elements not yet available for height logging.`);
      }
    };

    onMounted(() => {
      logHeights('Mounted');
    });

    onUpdated(() => {
      logHeights('Updated');
    });

    const state = ref({
      messages: [], // Array to hold chat messages { sender: 'user' | 'bot', text: '...' }
      currentMessage: '',
    });
  

    const sendMessage = () => {
      if (state.value.currentMessage.trim()) {
        const userMessage = state.value.currentMessage.trim();
        state.value.messages.push({ sender: 'user', text: userMessage });
        state.value.currentMessage = '';
        scrollToEnd(); // Scroll to the latest message

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
          state.value.messages.push({ sender: 'bot', text: botReply });
          scrollToEnd(); // Scroll to the latest message
        })
        .catch(error => {
          console.error('Error with chatbot API:', error);
          state.value.messages.push({ sender: 'bot', text: `Error: ${error.message}` });
           scrollToEnd(); // Scroll to the latest message
        });
      }
    };

    const scrollToEnd = () => {
      nextTick(() => {
        if (chatEnd.value) {
          chatEnd.value.scrollIntoView({ behavior: 'smooth' });
        }
      });
    };

    return {
      chatbotRootEl,
      messageAreaEl,
      chatEnd,
      messages: state.value.messages, // Expose for template v-for
      currentMessage: state.value.currentMessage, // Expose for template v-model
      sendMessage,
    };
  },
};
</script>

<style scoped>
</style>
