<template>
  <div id="printableContent">
    <header>
      <div class="logo" stly="max-width: 80px">
        <img
          :src="logo_image_src"
          style="background-color: white; max-width: 80px"
        />
      </div>
      <div class="company-name">
        <h1>{{ companyName }}</h1>
      </div>
    </header>

    <section>
      <h2>
        {{ invoice_po }}
      </h2>
      <h4>Billing and Payment Statement</h4>
      <p><strong>Customer Information:</strong></p>
      <p>Name: {{ customerDetail.name }}</p>
      <p>Email: {{ customerDetail.email }}</p>
      <p>Billing Address: {{ customerDetail.address }}</p>
      <p><strong>Container Information:</strong></p>

      <div
        v-for="(lineItem, index) in order.line_items"
        :key="index"
        class="mb-1 border-b-1 border-gray-300"
      >
        <p><strong>Container Type:</strong> {{ lineItem.abrev_title }}</p>
        <p
          ><strong>Container #:</strong>
          {{ lineItem.inventory?.container_number || "Not available" }}</p
        >
        <p
          ><strong>Container Location:</strong>
          {{
            customerDetail.delivery_address == ""
              ? lineItem.inventory_address[0]?.full_address_computed
              : customerDetail.delivery_address
          }}</p
        >
      </div>
      <!---->
      <div v-if="usersStore.cms?.is_only_auto_pay_allowed">
        <p> Only autopay allowed </p>
      </div>
      <div v-if="orderCustomerProfileId" class="autopay-info">
        <p>Last 4 Digits of Card on File: {{ order.last_card_digits }}</p>
      </div>
      <div
        v-if="
          orderCustomerProfileId == null &&
          usersStore.cms?.rent_options.always_auto_pay != true
        "
        class="autopay-info"
      >
        <p>Not enrolled in autopay, please call (979) 798-2629</p>
      </div>

      <p
        v-if="orderDetail.amount_due == 0"
        class="status-message status-current"
      >
        Status: Current
      </p>
      <p v-else> Status: Overdue </p>
      <p><strong>Invoice Information:</strong></p>
      <table>
        <tbody>
          <tr>
            <th>Total Amount Due</th>
            <th>Start Date</th>
            <th>Paid Thru</th>
            <th>Move Out</th>
          </tr>
          <tr>
            <td>{{ $fc(orderDetail.amount_due) }}</td>
            <td>{{ orderDetail.start_date }}</td>
            <td>{{ orderInfo.paid_thru }}</td>
            <td></td> </tr
        ></tbody>
      </table>
      <p><strong>Transaction History:</strong></p>
      <table>
        <tbody>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
          </tr>
          <template
            v-for="transaction in statementList"
            :key="JSON.stringify(transaction)"
          >
            <tr>
              <td>{{ transaction.date }}</td>
              <td>{{ transaction.description }}</td>
              <td
                style="color: red"
                v-if="transaction?.description.includes('PAYMENT')"
                >{{ transaction.amount }}</td
              >
              <td v-else> {{ transaction.amount }} </td>
            </tr>
          </template>
        </tbody>
      </table>
      <p>
        Total Amount Due:
        <strong>{{ $fc(order.calculated_rent_balance) }}</strong>
      </p>
    </section>
  </div>
  <div class="mt-8">
    <button class="print-button" @click="print">Print</button>
  </div>
</template>

<script setup>
  import { computed, onMounted } from "vue"
  import { useUsers } from "@/store/modules/users"
  import CustomerApi from "@/api/customers"

  import { inject } from "vue"
  const $fc = inject("$formatCurrency")

  const customerApi = new CustomerApi()
  const usersStore = useUsers()

  const {
    transactionList,
    customerDetail,
    orderDetail,
    companyName,
    orderInfo,
    orderCustomerProfileId,
    order,
    pdf_url
  } = defineProps({
    transactionList: {
      type: Array,
      required: true
    },
    customerDetail: {
      type: Object,
      required: true
    },
    orderDetail: {
      type: Object,
      required: true
    },
    companyName: {
      type: String,
      required: true
    },
    orderInfo: {
      type: Object,
      required: true
    },
    orderCustomerProfileId: {
      type: String,
      required: true
    },
    order: {
      type: Object,
      default: {}
    },
    pdf_url: {
      type: String,
      default: ""
    }
  })
  const callback = () => {
    // console.log("Printing");
  }

  const statementList = computed(() => {
    return transactionList.sort((a, b) => new Date(a.date) - new Date(b.date))
  })

  onMounted(() => {
    transactionList.sort((a, b) => new Date(a.date) - new Date(b.date))
  })

  const logo_image_src = computed(() => {
    return usersStore?.cms?.logo_settings?.logo_path
  })
  const has_zero_tax = computed(() => {
    const zero_tax_pmt = transactionList.filter((transaction) => {
      return transaction.tax == 0
    })
    return zero_tax_pmt.length > 0
  })

  // make the following a computed
  // Invoice #{{ order.display_order_id }} | PO #{{
  //           order.purchase_order_number
  //         }}
  const invoice_po = computed(() => {
    // only display PO if it exists
    return `Invoice #${order.display_order_id} ${
      order.purchase_order_number ? `| PO #${order.purchase_order_number}` : ""
    }`
  })

  const print = async () => {
    let { data, error } = await customerApi.generateRentalStatemenPdf(order.id)
    if (data.value) {
      console.log(data.value.pdf_url)
      window.open(data.value.pdf_url, "_blank").focus()
    }
  }
</script>
<style scoped>
  body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
  }
  header {
    background-color: #333;
    color: #fff;
    text-align: center;
    padding: 1em 0;
  }

  section {
    margin: 20px;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }

  th,
  td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
  }

  th {
    background-color: #333;
    color: #fff;
  }

  h2 {
    color: #333;
  }

  p {
    margin-bottom: 10px;
  }

  button {
    padding: 10px 20px;
    background-color: #333;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-right: 10px;
  }

  button:hover {
    background-color: #555;
  }

  .autopay-info {
    margin-top: 20px;
    margin-bottom: 10px;
  }

  .autopay-button {
    display: inline-block;
    padding: 10px 20px;
    background-color: #28a745;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }

  .autopay-button:hover {
    background-color: #218838;
  }

  .status-message {
    margin-top: 20px;
    font-weight: bold;
  }

  .status-current {
    color: #28a745;
  }

  .status-overdue {
    color: #dc3545;
  }

  .company-name {
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .logo {
    position: absolute;
  }

  .logo img {
    width: 80px;
  }

  header {
    display: flex;
    align-items: center;
    position: relative;
  }
</style>
