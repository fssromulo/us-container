<template>
  <div v-for="c in ccOrder">
    {{ c.date }} {{ c.amount }}
    <template v-if="c.approved">
      <span>Approved</span>
    </template>

    <template v-if="c.errorMessage">
      <span>{{ `${c.errorMessage}` }}</span>
    </template>
  </div>
</template>

<script setup>
  import { computed, inject } from "vue"
  import { dfa } from "@/service/DateFormat.js"
  const $fc = inject("$formatCurrency")

  const props = defineProps({
    order: {
      type: Object,
      required: true
    }
  })

  const ccOrder = computed(() => {
    return props.order.credit_card.map((c) => {
      const authorizeProviderMessage =
        c.response_from_gateway?.transactionResponse?.messages
      let approved = false
      let message = ""
      if (authorizeProviderMessage?.length) {
        approved = authorizeProviderMessage[0].code === "1"
      }

      return {
        amount: $fc(
          c?.response_from_gateway?.payment_amount ||
            c.response_from_gateway?.auth_amount
        ),
        date: `${dfa(c.created_at)} | ${c.card_type} | ${c.merchant_name}`,
        approved: c.response_from_gateway?.result_code === "A" || approved,
        declined: c.response_from_gateway?.result_code !== "A" || !approved,
        result: c.response_from_gateway?.result || message,
        errorMessage: c.response_from_gateway?.errorMessage
      }
    })
  })
</script>
