<template>
  <div>
    <div class="chat-container col-12">
      <div class="chat-messages">
        <div v-for="item in state.chat_messages" :class="getClass(item)">
          <div class="message-content">{{ item.body }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed, inject, onMounted, watch, reactive } from "vue"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"

  const customerApi = new CustomerApi()
  const toast = useToast()

  const props = defineProps({
    customer_phone: {
      type: String,
      required: false,
      default: ""
    }
  })

  const getSeverity = (item) => {
    if (item.from.includes(props.customer_phone)) {
      return "success"
    } else {
      return "error"
    }
  }

  const getClass = (item) => {
    if (item.from.includes(props.customer_phone)) {
      return { sent: true, message: true }
    } else {
      return { received: false, message: true }
    }
  }

  const state = reactive({
    chat_messages: []
  })

  onMounted(async () => {
    const { data, error } = await customerApi.getChatLog(props.customer_phone)
    if (error.value == undefined) {
      state.chat_messages = data.value
      if (state.chat_messages.length == 0) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "No messages could be retrieved.",
          life: 3000,
          group: "br"
        })
      }
    } else {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error retrieving messages",
        life: 3000,
        group: "br"
      })
    }
  })
</script>

<style>
  .chat-container {
    margin: 20px auto;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    background-color: white;
  }
  .chat-messages {
    height: 400px;
    overflow-y: auto;
    padding: 20px;
  }
  .message {
    margin-bottom: 15px;
    max-width: 80%;
  }
  .message-content {
    padding: 10px;
    border-radius: 18px;
    display: inline-block;
  }
  .sent {
    text-align: right;
  }
  .sent .message-content {
    background-color: #0084ff;
    color: white;
  }
  .received .message-content {
    background-color: green;
    color: black;
  }
</style>
