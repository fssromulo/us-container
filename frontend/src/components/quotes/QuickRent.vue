<template>
  <div>
    <SingleCustomerSearch
      :displaySearchMode="true"
      @selected_single_customer="selectSingleCustomer"
      @success="selectSingleCustomer"
    />

    <CreateCustomer
      :stepsEnabled="false"
      :creating="true"
      customerEmailNote="will not send email"
      @validForm="createCustomer"
      :forceReset="true"
    ></CreateCustomer>
    <hr />
    <div
      class="grid grid-cols-12 gap-2 p-fluid"
      v-for="(currentOrder, index) in state.lineItems"
      :key="index"
    >
      <div
        class="col-span-12 mb-4 field"
        v-if="
          currentOrder.inventory_title &&
          currentOrder.inventory_title.length > 0
        "
      >
        <div class="text-align-center">
          Container Release Number : {{ currentOrder.inventory_title }}
        </div>
      </div>
      <div class="col-span-12 mb-2 lg:col-span-3 field">
        <label for="state" class="font-medium text-900 dark:text-0"
          >Container</label
        >
        <Select
          v-model="currentOrder.product_id"
          placeholder="Container"
          optionLabel="label"
          optionValue="value"
          class="p-component p-inputtext-fluid"
          :options="
            filteredContainerPricess.map((container) => {
              return { value: container.id, label: container.title }
            })
          "
        />
      </div>

      <div
        :class="{
          field: true,
          'mb-2': true,
          'lg:col-span-3': true,
          'col-span-6': true
        }"
      >
        <label for="state" class="font-medium text-900 dark:text-0"
          >Monthly Price</label
        >
        <InputNumber
          mode="currency"
          currency="USD"
          locale="en-US"
          v-model="currentOrder.monthly_price"
          class="p-component p-inputtext-fluid"
        />
      </div>

      <div
        :class="{
          field: true,
          'mb-2': true,
          'lg:col-span-3': true,
          'col-span-6': true
        }"
      >
        <label for="shipping" class="font-medium text-900 dark:text-0"
          >Drop off</label
        >
        <InputNumber
          mode="currency"
          currency="USD"
          locale="en-US"
          @input="updateShipping(index)"
          class="p-component p-inputtext-fluid"
          v-model="currentOrder.shipping_revenue"
        />
      </div>
      <div
        :class="{
          field: true,
          'mb-2': true,
          'lg:col-span-3': true,
          'col-span-6': true
        }"
      >
        <label for="shipping" class="font-medium text-900 dark:text-0"
          >Pickup price</label
        >
        <InputNumber
          mode="currency"
          currency="USD"
          locale="en-US"
          @input="updateShipping(index)"
          class="p-component p-inputtext-fluid"
          v-model="currentOrder.pick_up"
        />
      </div>

      <div
        :class="{
          field: true,
          'mb-2': true,
          'lg:col-span-3': true,
          'col-span-6': true
        }"
      >
        <label for="shipping" class="font-medium text-900 dark:text-0"
          >Shipping Cost</label
        >
        <InputNumber
          mode="currency"
          currency="USD"
          locale="en-US"
          v-model="currentOrder.shipping_cost"
          class="p-component p-inputtext-fluid"
        />
      </div>
      <div
        :class="{
          field: true,
          'mb-2': true,
          'lg:col-span-2': true,
          'col-span-6': true
        }"
      >
        <label for="shipping" class="font-medium text-900 dark:text-0"
          >Door orientation</label
        >
        <Select
          v-model="currentOrder.door_orientation"
          class="p-component p-inputtext-fluid"
          :options="[
            { value: 'Facing Cab', label: 'Facing Cab' },
            { value: 'Opposite of Cab', label: 'Opposite of Cab' }
          ]"
          optionLabel="label"
          optionValue="value"
        />
      </div>
      <div
        :class="{
          field: true,
          'col-span-6': true,
          'lg:col-span-2': true
        }"
      >
        <Button
          label="Attach Container"
          class="mt-6 p-button-text bg-100 dark:bg-700"
          @click="attachContainer(index)"
        ></Button>
      </div>

      <div
        v-if="state.lineItems.length > 1"
        :class="{
          field: true,
          'col-span-1': true,
          'md:col-span-1': true
        }"
      >
        <Button
          type="button"
          icon="pi pi-trash text-md"
          class="m-1 mt-6 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          @click="removeLineItem(index)"
        ></Button>
      </div>
      <div
        v-if="index + 1 == state.lineItems.length"
        class="col-span-12 text-center t-3 md:col-span-12"
      >
        <Button
          type="button"
          icon="pi pi-plus text-md"
          class="m-1 mt-6 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
          @click="addOrderLine"
        ></Button>
      </div>
    </div>
    <hr />
    <div class="grid grid-cols-12 gap-4">
      <div class="col-span-12 mt-2 tex-center">
        <div class="flex flex-col items-center mb-2">
          <label> Tax Exempt </label>
          <ToggleSwitch v-model="state.taxExempt" />
        </div>
        <div class="flex flex-col items-center">
          <div
            :class="{
              field: true
            }"
          >
            <label for="shipping" class="mr-2 font-medium text-900 dark:text-0"
              >Override Tax</label
            >
            <InputNumber
              mode="currency"
              currency="USD"
              locale="en-US"
              @keydown="state.taxModified = true"
              v-model="state.modifiedOrderTax"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-12 gap-4">
      <div class="col-span-12 mt-2">
        <div v-if="!$isPublic" class="flex flex-wrap justify-center">
          <UpdateOrderSettings @updatedAttributes="setAttributes" />
        </div>
      </div>

      <div class="col-span-4 mt-2">
        <label for="state" class="mb-2 mr-2 font-medium text-900 dark:text-0"
          >Delivered On (Rent started on)</label
        >
        <DatePicker
          style="width: 210px"
          showIcon
          showButtonBar
          v-model="state.delivered_at"
          dateFormat="mm/dd/y"
          id="delivered_on"
          class="text-xl"
        ></DatePicker>
      </div>
      <div class="col-span-4 mt-2">
        <label for="state" class="mb-2 mr-2 font-medium text-900 dark:text-0"
          >Ended On (Optional)</label
        >
        <DatePicker
          class="text-xl"
          style="width: 210px"
          showIcon
          showButtonBar
          v-model="state.ended_on"
          dateFormat="mm/dd/y"
        >
        </DatePicker>
      </div>
      <div class="col-span-4 mt-2">
        <div class="flex flex-col items-center">
          <label>
            {{ state.pickUpPaid ? "Pickup Paid" : "Pickup Not Paid" }}
          </label>
          <ToggleSwitch v-model="state.pickUpPaid" />
        </div>
      </div>

      <div class="col-span-12 mt-4 xl:col-span-6">
        <label for="state" class="mb-2 font-medium text-900 dark:text-0"
          >Order Fees</label
        >
        <div
          class="grid grid-cols-12 gap-4 no-gutters"
          v-for="(fee, index) in state.orderFees"
          :key="index"
        >
          <div class="col-span-4 mb-4 field xl:col-span-4">
            <Select
              v-model="fee.fee_type"
              placeholder="Fee Type"
              optionLabel="label"
              optionValue="value"
              :options="feeTypeOptions"
            />
          </div>
          <div
            :class="{
              field: true,
              'col-span-4': true,
              'xl:col-span-4': true
            }"
          >
            <InputNumber
              mode="currency"
              currency="USD"
              locale="en-US"
              v-model="fee.fee"
            />
          </div>
          <div
            v-if="state.orderFees.length > 1"
            :class="{
              field: true,
              'col-span-1 ml-12': true,
              'xl:col-span-1': true
            }"
          >
            <Button
              type="button"
              icon="pi pi-trash text-xl"
              class="m-1 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
              @click="removeLineFee(index)"
            ></Button>
          </div>
          <div
            v-if="index + 1 == state.orderFees.length"
            :class="{
              field: true,
              'col-span-1': true,
              'ml-4': state.orderFees.length > 1,
              'ml-12': state.orderFees.length === 1,
              'xl:col-span-1': true
            }"
          >
            <Button
              type="button"
              icon="pi pi-plus text-xl"
              class="m-1 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
              @click="addFeeLine"
            ></Button>
          </div>
        </div>
      </div>
      <div class="col-span-12 mt-4 xl:col-span-6">
        <label for="state" class="font-medium text-900 dark:text-0"
          >Misc. Costs</label
        >
        <div
          class="grid grid-cols-12 gap-4"
          v-for="(fee, index) in state.miscCosts"
          :key="index"
        >
          <div class="col-span-4 mb-4 field xl:col-span-3">
            <Select
              v-model="fee.misc_type"
              placeholder="Misc Type"
              optionLabel="label"
              optionValue="value"
              :options="miscCostOptionList"
            />
          </div>
          <div
            :class="{
              field: true,
              'col-span-4': true,
              'xl:col-span-4': true
            }"
          >
            <InputNumber
              mode="currency"
              currency="USD"
              locale="en-US"
              v-model="fee.misc"
            />
          </div>
          <div
            v-if="state.miscCosts.length > 1"
            :class="{
              field: true,
              'col-span-1  ml-12': true,
              'xl:col-span-1': true
            }"
          >
            <Button
              type="button"
              icon="pi pi-trash text-xl"
              class="m-1 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
              @click="removeLineMiscCost(index)"
            ></Button>
          </div>
          <div
            v-if="index + 1 == state.miscCosts.length"
            :class="{
              field: true,
              'col-span-1': true,
              'xl:col-span-1': true,
              'ml-4': state.miscCosts.length > 1,
              'ml-12': state.miscCosts.length === 1
            }"
          >
            <Button
              type="button"
              icon="pi pi-plus text-xl"
              class="m-1 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
              @click="addMiscCostLine"
            ></Button>
          </div>
        </div>
        <label for="state" class="mb-2 font-medium text-900"
          >First payment</label
        >
        <div
          :class="{
            field: true,
            'col-span-4': true,
            'xl:col-span-4': true
          }"
        >
          <InputNumber
            mode="currency"
            currency="USD"
            locale="en-US"
            disabled
            v-model="firstPaymentComputed"
          />
        </div>

        <div>
          <br />
          <div class="mb-4 field">
            <Textarea
              class="w-full ml-2 mr-2"
              v-model="state.notes"
              :autoResize="true"
              rows="2"
              placeholder="Other Notes"
              label="Notes"
              cols="10"
            />
          </div>
        </div>
      </div>

      <div class="col-span-12 text-center">
        <div
          class="flex flex-wrap justify-center mt-4 field-checkbox"
          v-if="state.selectedPaymentMethod !== 'Credit Card'"
        >
          <Button
            :label="`Add Rental`"
            :disabled="state.payButtonDisabled"
            :loading="state.loading"
            style="max-width: 250px"
            @click="addQuickRental"
            class="p-button-primary p-button-rounded p-button-lg"
          ></Button>
        </div>
      </div>
    </div>

    <Dialog
      v-model:visible="state.attachContainerDialog"
      dismissableMask
      closeOnEscape
      :modal="true"
      :breakpoints="{
        '2000px': '80vw',
        '1400px': '80vw',
        '1200px': '80vw',
        '992px': '85vw',
        '600px': '100vw',
        '480px': '100vw',
        '320px': '100vw'
      }"
    >
      <template #header>
        <div class="flex items-stretch">
          <div class="flex">
            <p class="text-3xl">Attach Container</p>
          </div>
        </div>
      </template>
      <AttachContainer
        @onUpdate="updateOrder"
        :returnContainerId="true"
        :selectedContainers="state.selectedContainers"
        :close="() => (state.attachContainerDialog = false)"
      />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, watch, inject } from "vue"
  import { useToast } from "primevue/usetoast"
  import CreateCustomer from "../invoicing/create/CreateCustomer.vue"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useContainerPrices } from "@/store/modules/pricing"
  import { useUsers } from "@/store/modules/users"
  import CustomerApi from "@/api/customers"
  import PriceService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import PaymentFields from "@/components/invoicing/payment/PaymentFields.vue"
  import OrderSummary from "../invoicing/summary/OrderSummary.vue"
  import UpdateOrderSettings from "../invoicing/create/UpdateOrderSettings.vue"

  import AttachContainer from "../inventory/AttachContainer.vue"
  import Cart from "@/service/Cart"
  import { useTaxes } from "@/store/modules/taxes"
  import SingleCustomerSearch from "../invoicing/SingleCustomerSearch.vue"
  import { useCustomerHelper } from "@/store/modules/customerHelper"

  const customerHelper = useCustomerHelper()
  const $fc = inject("$formatCurrency")
  const $route = inject("$route")
  const $isPublic = inject("$isPublic")

  const taxStore = useTaxes()
  const userStore = useUsers()
  const pricingStore = useContainerPrices()
  const customerStore = useCustomerOrder()
  const customerApi = new CustomerApi()
  const toast = useToast()
  const priceService = new PriceService()
  const pricingApi = new PricingApi()
  const cartService = new Cart()

  const emit = defineEmits(["hide"])
  const remainingBalanceCalc = computed(() => {
    const balances = totalOwed.value.total
    return Number(balances - state.partialPayAmount).toFixed(2)
  })
  const postalZipText = computed(() => {
    return userStore.cms?.account_country &&
      userStore.cms?.account_country == "Canada"
      ? "Postal Code"
      : "Zip Code"
  })

  const { quotesList, pageSize, isPickup } = defineProps({
    quotesList: {
      type: Object,
      default: () => ({})
    },
    isPickup: {
      type: Boolean,
      default: () => false
    },
    pageSize: {
      type: Number,
      default: () => 20
    }
  })

  const selectSingleCustomer = async (single_customer_id) => {
    state.singleCustomerId = single_customer_id
    const { data, error } = await customerApi.singleCustomer(single_customer_id)
    if (error.value == undefined) {
      customerHelper.setDisabled(true)
      customerHelper.first_name = data.value.first_name
      customerHelper.last_name = data.value.last_name
      customerHelper.company_name = data.value.company_name
      customerHelper.customer_email = data.value.customer_contacts[0].email
      customerHelper.customer_phone = data.value.customer_contacts[0].phone

      customerHelper.street_address =
        data.value.customer_contacts[0].customer_address.street_address
      customerHelper.city =
        data.value.customer_contacts[0].customer_address.city
      customerHelper.state =
        data.value.customer_contacts[0].customer_address.state
      customerHelper.zip = data.value.customer_contacts[0].customer_address.zip
      customerHelper.county =
        data.value.customer_contacts[0].customer_address.county
      customerHelper.setIncreaseVersion()
    }
  }

  const firstPaymentComputed = computed(() => {
    let total = 0
    let totalOrderTax = 0
    let taxRate = 0 // this will just grab the first container's state tax rate
    let totalTaxFeesAmt = 0
    let totalNonTaxFeesAmt = 0

    state.lineItems.forEach((item) => {
      let productInfo = selectedContainerPriceInfo(item.product_id)
      if (productInfo !== undefined && productInfo !== null) {
        item.product_state = productInfo.location.state
      }
      total += item.monthly_price + item.shipping_revenue + item.pick_up

      if (taxRate === 0) {
        taxRate =
          taxStore.taxes.find((s) => s.state === item.product_state)?.rate || 0
      }
    })

    state.orderFees.forEach((fee) => {
      const currentFee = customerStore.feeTypes.filter((type) => {
        return type.id == fee.fee_type
      })
      if (currentFee.length > 0) {
        let cFee = currentFee[0]
        if (cFee?.is_taxable) {
          totalTaxFeesAmt += fee.fee
        } else {
          totalNonTaxFeesAmt += fee.fee
        }
      }
    })
    return total + totalNonTaxFeesAmt + totalTaxFeesAmt + state.modifiedOrderTax
  })

  const title = computed(() => {
    let title = isPickup ? "Customer location:" : "Shipping to:"
    const addr = customerStore.address
    title += ` ${addr.city} ${addr.state} ${addr.zip}`
    return title
  })

  const showOrderStatusDropdown = computed(() => {
    return userStore?.cms?.feature_flags?.select_status_on_order_creation
  })

  const updateShipping = (index) => {
    let lineItem = state.lineItems[index]
    if (lineItem.shipping_revenue == 0 || lineItem.pick_up == 0) return
    console.log("Here")
    if (lineItem.shipping_revenue > lineItem.pick_up)
      state.lineItems[index]["pick_up"] = lineItem.shipping_revenue
    if (lineItem.pick_up > lineItem.shipping_revenue)
      state.lineItems[index]["shipping_revenue"] = lineItem.pick_up
  }

  const totalOwed = computed(() => {
    let total = 0
    let totalOrderTax = 0
    let taxRate = 0 // this will just grab the first container's state tax rate
    let totalTaxFeesAmt = 0
    let totalNonTaxFeesAmt = 0

    state.lineItems.forEach((item) => {
      let productInfo = selectedContainerPriceInfo(item.product_id)
      if (productInfo !== undefined && productInfo !== null) {
        item.product_state = productInfo.location.state
      }
      total += item.monthly_price + item.shipping_revenue + item.pick_up

      if (taxRate === 0) {
        taxRate =
          taxStore.taxes.find((s) => s.state === item.product_state)?.rate || 0
      }
    })

    state.orderFees.forEach((fee) => {
      const currentFee = customerStore.feeTypes.filter((type) => {
        return type.id == fee.fee_type
      })
      if (currentFee.length > 0) {
        let cFee = currentFee[0]
        if (cFee?.is_taxable) {
          totalTaxFeesAmt += fee.fee
        } else {
          totalNonTaxFeesAmt += fee.fee
        }
      }
    })
    total += totalTaxFeesAmt

    totalOrderTax = cartService.roundIt(total * taxRate, 2)

    state.totalOrderTax = totalOrderTax
    total += totalNonTaxFeesAmt
    if (!state.taxModified) state.modifiedOrderTax = state.totalOrderTax

    return {
      subTotal: total,
      totalOrderTax: totalOrderTax,
      total: total + state.modifiedOrderTax,
      modifiedOrderTax: state.modifiedOrderTax
    }
  })

  const setAttributes = (attributes) => {
    state.orderAttributes = attributes
  }

  const bankFee = computed(() => {
    return state.partialPayAmount * 0.035
  })
  const transactionTypeChanged = async (transactionType) => {
    console.log(transactionType)
    state.paymentType = transactionType.paymentType
    state.paymentNotes = transactionType.notes
    state.paid_at = transactionType.paid_at
  }
  const addQuickRental = async () => {
    state.loading = true
    state.creating = true
    let paymentObj = {}

    const order = {
      customer_id: state.selectedCustomer.id,
      first_name: customerStore.customer.first_name,
      last_name: customerStore.customer.last_name,
      email: customerStore.customer.email,
      phone: customerStore.customer.phone,
      zip: customerStore.address.zip,
      street_address: customerStore.address.street_address,
      state: customerStore.address.state,
      city: customerStore.address.city,
      county: customerStore.address.county,
      billing_zip: customerStore.billing_address.zip,
      billing_street_address: customerStore.billing_address.street_address,
      billing_state: customerStore.billing_address.state,
      billing_city: customerStore.billing_address.city,
      billing_county: customerStore.billing_address.county,
      company_name: customerStore.customer.company_name,
      single_customer_id: state.singleCustomerId,
      ended_on: state.ended_on,
      started_on: state.delivered_at,
      order: {
        paid_at: state.paid_at,
        delivered_at: state.delivered_at,
        ended_on: state.ended_on,
        pick_up_paid: state.pickUpPaid,
        type: "RENT",
        tax: state.modifiedOrderTax,
        attributes: state.orderAttributes,
        total_price: totalOwed.value.total
      },
      line_items: state.lineItems.map((item) => {
        let selectedContainerPrice = selectedContainerPriceInfo(item.product_id)

        let attributes = {}
        selectedContainerPrice?.container_product_attributes.forEach((el) => {
          if (el.container_attribute["name"] == "High Cube") {
            attributes["high_cube"] = true
          }

          if (el.container_attribute["name"] == "Double Door") {
            attributes["double_door"] = true
          }

          if (el.container_attribute["name"] == "Portable") {
            attributes["portable"] = true
          }
        })

        return {
          attributes: attributes,
          container_size: selectedContainerPrice?.container_size,
          condition: selectedContainerPrice?.condition,
          product_state: selectedContainerPrice?.location.state,
          product_city: selectedContainerPrice?.location.city,
          product_id: item.product_id,
          monthly_owed: item.monthly_price,
          price: item.price,
          shipping: item.shipping_revenue,
          pickup: item.pick_up,
          shipping_cost: item.shipping_cost,
          inventory_id: item.inventory_id,
          door_orientation: item.door_orientation
        }
      }),
      fees: state.orderFees.map((fee) => {
        return {
          fee_type: fee.fee_type,
          fee: fee.fee
        }
      }),
      misc_costs: state.miscCosts.map((cost) => {
        return {
          misc_type: cost.misc_type,
          misc: cost.misc
        }
      }),
      payment: paymentObj,
      tax_exempt: state.taxExempt,
      note: state.notes
    }
    const { data, error } = await customerApi.createQuickRent(order)

    if (error.value) {
      state.loading = false
      if (error.value.response) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: error.value.response.data.detail,
          group: "br",
          life: 5000
        })
      } else {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "There was an error creating or paying the order",
          group: "br",
          life: 5000
        })
      }
      return
    }

    state.savedDislpayId = data.value.order[0].display_order_id
    // await saveTransactionTypes(data.value.order[0].id, state.partialPayAmount)
    toast.add({
      severity: "success",
      summary: "Success",
      detail: "Order created",
      group: "br",
      life: 5000
    })
    emit("hide")

    $route.push({
      name: "invoices_with_id",
      query: { forceRefresh: true },
      params: { id: data.value.order[0].display_order_id }
    })
    state.loading = false
  }

  const saveTransactionTypes = async (orderId, amount) => {
    state.loading = true
    let tType = {
      payment_type:
        state.selectedPaymentMethod.toLowerCase() === "credit card"
          ? "CC"
          : state.paymentType,
      order_id: orderId,
      rent_period_ids: [],
      notes: state.paymentNotes,
      amount: amount
    }

    const { data, error } = await customerApi.addTransactionType(tType)
    if (data.value) {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Payment means saved successful",
        group: "br",
        life: 2000
      })
    }
    emit("transactionTypeSaved", {})
    state.loading = false
  }

  const createCustomer = async (valid) => {
    state.hasValidCustomer = valid
  }

  const searchCustomer = async () => {
    state.loading = true
    state.retrievedCustomers = []
    const searchUrl = constructSearchUrl()

    const { data, error } = await customerApi.customerSearch(searchUrl)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading customers",
        group: "br",
        life: 5000
      })
      state.loading = false
      return
    }
    if (data.value.length === 0) {
      toast.add({
        severity: "info",
        summary: "Info",
        detail: "No customers found",
        group: "br",
        life: 5000
      })
      state.loading = false
      return
    }

    state.retrievedCustomers = data.value
      .map((dt) => {
        let order = dt.order[0]
        if (!order) {
          return null
        }
        return {
          id: dt.id,
          first_name: dt.first_name || "",
          last_name: dt.last_name || "",
          email: dt.email || "",
          phone: dt.phone || "",
          street_address: order.address.street_address || "",
          zip: order.address.zip || "",
          state: order.address.state || "",
          city: order.address.city || "",
          county: order.address.county || ""
        }
      })
      .filter((dt) => dt !== null)
    state.loading = false
  }

  const constructSearchUrl = () => {
    let filters = {}
    filters[state.searchType] = state.search

    const filteredNulls = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v != null)
    )

    const searchParams = new URLSearchParams(Object.entries(filteredNulls))
    return searchParams.toString()
  }

  const filteredContainerPricess = computed(() => {
    return pricingStore.containerPrices
  })

  const selectedContainerPriceInfo = (product_id) => {
    console.log(product_id)
    let containerPrice = filteredContainerPricess.value.filter((e) => {
      return e.id === product_id
    })[0]
    console.log(containerPrice)
    return containerPrice
  }

  const addOrderLine = () => {
    state.lineItems.push({
      price: 0,
      shipping_revenue: 0,
      shipping_cost: 0,
      monthly_price: 0,
      pick_up: 0,
      product_id: filteredContainerPricess.value[0]?.id,
      inventory_id: null,
      inventory_title: "",
      product_state: "",
      attributes: {
        standard: false,
        high_cube: false,
        dimensions: "",
        double_door: false
      },
      container_size: "",
      condition: ""
    })
  }

  const removeLineItem = (index) => {
    //customerStore
    console.log(customerStore.customer)
    console.log(customerStore.address)
    state.lineItems.splice(index, 1)
  }

  const removeLineFee = (index) => {
    state.orderFees.splice(index, 1)
  }

  const addFeeLine = () => {
    state.orderFees.push({
      fee_type: "",
      fee: 0
    })
  }

  const addMiscCostLine = () => {
    state.miscCosts.push({
      misc_type: "",
      misc: 0
    })
  }

  const removeLineMiscCost = (index) => {
    state.miscCosts.splice(index, 1)
  }

  const checkObjectsAreSame = (obj1, obj2) => {
    const keys1 = Object.keys(obj1)
    const keys2 = Object.keys(obj2)
    if (keys1.length !== keys2.length) {
      return false
    }
    for (const key of keys1) {
      if (!keys2.includes(key)) {
        return false
      }
      const value1 = obj1[key]
      const value2 = obj2[key]
      if (typeof value1 === "object" && typeof value2 === "object") {
        if (!areObjectsEqual(value1, value2)) {
          return false
        }
      } else {
        if (value1 !== value2) {
          return false
        }
      }
    }
    return true
  }
  const attachContainer = async (index) => {
    state.selectedLineItem = index
    state.attachContainerDialog = true
  }
  const updateOrder = async (inventory) => {
    state.lineItems[state.selectedLineItem].inventory_id =
      inventory.inventory_id
    state.lineItems[state.selectedLineItem].product_id =
      filteredContainerPricess.value.filter((price) => {
        return price.title === inventory.title
      })[0]?.id || ""

    state.selectedContainers = state.selectedContainers.filter((e) => {
      return state.lineItems[state.selectedContainers]?.inventory_id !== e
    })
    state.selectedContainers.push(inventory.inventory_id)
    state.lineItems[state.selectedLineItem].inventory_title =
      inventory.inventory_title
    state.selectedLineItem = null
    state.attachContainerDialog = false
  }

  const feeTypes = computed(() => {
    return customerStore.feeTypes?.filter((type) => !type.is_archived)
  })

  const feeTypeOptions = computed(() => {
    return customerStore.feeTypes
      ?.filter((type) => !type.is_archived)
      .map((type) => {
        return {
          label: type.is_taxable
            ? `${type.name} (Is Taxed)`
            : `${type.name} (Not Taxed)`,
          value: type.id
        }
      })
  })
  // [
  //   { label: "LATE", value: "LATE" },
  //   { label: "CREDIT_CARD", value: "CREDIT_CARD" },
  //   { label: "RUSH", value: "RUSH" },
  // ];
  const state = reactive({
    pickUpPaid: true,
    hasValidCustomer: false,
    searchType: "name",
    search: "",
    isPartial: false,
    paid_at: new Date(),
    partialPayAmount: 0,
    loading: false,
    ended_on: null,
    delivered_at: new Date(),
    paymentMethod: ["Credit Card", "Other"],
    selectedPaymentMethod: "Other",
    paymentType: "Cash",
    retrievedCustomers: [],
    selectedCustomer: {},
    orderId: "",
    attachContainerDialog: false,
    costTypeOptions: [],
    selectedLineItem: null,
    selectedContainers: [],
    paymentNotes: "",
    notes: "",
    taxExempt: false,
    savedDislpayId: "",
    orderFees: [
      {
        fee_type: "",
        fee: 0
      }
    ],
    miscCosts: [
      {
        misc_type: "",
        misc: 0
      }
    ],
    lineItems: [],
    creating: false,
    totalOrderTax: 0,
    modifiedOrderTax: 0,
    taxModified: false,
    orderAttributes: {},
    singleCustomerId: null
  })
  const fetchOptions = async () => {
    try {
      // Assuming customerApi.getAllCostTypes() returns a promise
      const { data } = await customerApi.getAllCostTypes()
      state.costTypeOptions = data.value
    } catch (error) {
      console.error(error)
    }
  }
  const miscCostOptionList = computed(() => {
    return state.costTypeOptions.map((option) => ({
      label: option.name,
      value: option.id
    }))
  })
  const resetPartialPaiedAmt = () => {
    state.partialPayAmount = totalOwed.value.total
  }
  watch(
    () => state.isPartial,
    (newVal) => {
      resetPartialPaiedAmt()
    }
  )
  watch(
    () => totalOwed.value.subTotal,
    (newVal) => {
      resetPartialPaiedAmt()
    }
  )
  watch(
    () => state.delivered_at,
    (newVal) => {
      if (newVal == null || newVal == "") state.delivered_at = new Date()
    }
  )
  watch(
    () => state.selectedCustomer,
    async (newVal) => {
      customerStore.setCustomer({
        first_name: newVal.first_name,
        last_name: newVal.last_name,
        email: newVal.email,
        phone: newVal.phone
      })
      customerStore.setAddress({
        zip: newVal.zip,
        street_address: newVal.street_address,
        state: newVal.state,
        city: newVal.city,
        county: newVal.county
      })
    }
  )

  watch(
    () => state.selectedPaymentMethod,
    async (newVal) => {
      if (newVal.toLowerCase() === "other") {
        state.paymentType = "Cash"
      } else {
        state.paymentType = "Credit Card"
      }
      resetPartialPaiedAmt()
    }
  )
  watch(
    () => state.modifiedOrderTax,
    () => {
      resetPartialPaiedAmt()
    }
  )

  watch(
    () => state.delivered_at,
    async (newVal) => {
      let data_request = {
        current_date: state.delivered_at,
        rent_due_on_day: state.delivered_at.getDate()
      }

      const { data, error } = await customerApi.getRentOnDueDate(data_request)
      state.rent_due_date = new Date(data.value[0])
    }
  )

  watch(
    () => state.taxExempt,
    async (newVal) => {
      if (newVal) {
        state.modifiedOrderTax = 0.0
        state.taxModified = true
      } else {
        state.modifiedOrderTax = state.totalOrderTax
        state.taxModified = false
      }
    }
  )
  onMounted(async () => {
    customerStore.setCustomer({})
    // customerStore.setAddress({});
    if (userStore.cms?.default_selling_states !== undefined)
      customerStore.setAddress({
        state: userStore.cms?.default_selling_states[0] || ""
      })

    await fetchOptions()

    if (pricingStore.containerPrices.length === 0) {
      const { data } = await pricingApi.getContainerPricing()
      const prices = data.value.map((p) => priceService.dtoContainerPricing(p))
      pricingStore.setContainerPrices(prices)
    }
    if (pricingStore.accessoryPrices.length === 0) {
      const { data } = await pricingApi.getProduct()
      const prices = data.value.map((p) => priceService.dtoProductPricing(p))
      pricingStore.setAccessoryPrices(prices)
    }

    addOrderLine()

    let data_request = {
      current_date: state.delivered_at,
      rent_due_on_day: state.delivered_at.getDate()
    }

    const { data, error } = await customerApi.getRentOnDueDate(data_request)

    state.rent_due_date = new Date(data.value[0])
  })
</script>
