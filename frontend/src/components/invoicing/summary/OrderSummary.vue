<template>
  <div class="flex flex-col flex-auto">
    <p class="text-2xl mt-4" v-if="props.totalTax != 0">
      Sub Total:
      {{ $fc(props.subTotal) }}
    </p>
    <p class="text-2xl" v-if="props.totalTax != 0 && props.totalCartRTO == 0">
      {{ taxText }}
      {{ $fc(props.totalTax) }}
    </p>
    <p class="text-2xl" v-if="props.isCreditCardPayment">
      Convenience Fee (3.5%):
      {{ $fc(props.bankFee) }}
    </p>

    <hr v-if="props.totalTax != 0" />
    <p class="text-2xl mb-4" v-if="props.totalCartRTO == 0">
      Total:
      {{ $fc(total) }}
    </p>
  </div>
</template>

<script setup>
  import { inject, computed } from "vue"

  const $fc = inject("$formatCurrency")

  const props = defineProps({
    taxModified: {
      type: Boolean,
      default: false
    },
    subTotal: {
      type: Number,
      default: 0
    },
    totalTax: { type: Number, default: 0 },
    totalCartRTO: { type: Number, default: 0 },
    bankFee: { type: Number, default: 0 },
    isCreditCardPayment: { type: Boolean, default: false }
  })

  const total = computed(() => {
    let total = props.subTotal + props.totalTax
    if (props.isCreditCardPayment) total += props.bankFee
    return total
  })

  const taxText = computed(() => {
    return props.taxModified ? "Overriden Tax:" : "Sales Tax:"
  })
</script>
