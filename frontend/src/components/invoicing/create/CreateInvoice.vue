<template>
  <div
    class="grid grid-cols-12 gap-4 formfrid p-fluid"
    style="max-width: 900px"
  >
    <div v-if="stepsEnabled" class="md:col-span-2">
      <ul class="p-0 m-0 list-none bg-0 dark:bg-900">
        <li v-for="(step, i) in state.steps" :key="i" class="flex p-4 mb-2">
          <div
            @click="state.selectedStep = i"
            class="flex flex-col items-center"
            style="width: 2rem"
          >
            <span
              :class="{
                'bg-green-500 text-0 dark:text-900 flex items-center justify-center rounded-full':
                  state.selectedStep === i,
                'bg-0 dark:bg-900 text-blue-500 border-blue-500 border-2 rounded-full flex items-center justify-center rounded-full':
                  state.selectedStep !== i
              }"
              style="min-width: 2rem; min-height: 2rem"
            >
              <i v-if="state.selectedStep === i" class="pi pi-check"></i>
              {{ state.selectedStep !== i ? i + 1 : "" }}
            </span>
            <div
              class="h-full bg-300 dark:bg-500"
              style="width: 2px; min-height: 4rem"
            ></div>
          </div>
          <div class="ml-4" @click="state.selectedStep = i">
            <div class="mb-2 font-medium text-900 dark:text-0">{{
              step.label
            }}</div>
            <span class="leading-normal text-700 dark:text-100"></span>
          </div>
        </li>
      </ul>
    </div>

    <div class="col-12">
      <create-customer
        :adminCreation="adminCreation"
        :customerOrderProp="state.customerOrder"
        :stepsEnabled="stepsEnabled"
        customerEmailNote="will send email"
      />
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <template v-if="state.selectedStep === 2 || !stepsEnabled">
          <div
            v-if="adminCreation"
            class="col-span-12 mb-4 border border-t"
          ></div>
          <CreateLineItem
            v-if="adminCreation"
            :customerOrderProp="state.customerOrder"
          />
          <p v-if="!adminCreation" class="col-span-6 col-start-7 mb-4 text-2xl">
            Cart
          </p>
          <RentalCart
            v-if="!adminCreation && state.customerOrder.type == 'RENT'"
            :cart="customerStore.cart.containers"
          />
          <PurchaseCart
            v-if="!adminCreation && state.customerOrder.type == 'PURCHASE'"
            :cart="customerStore.cart.containers"
          />
          <AccessoryCart
            v-if="
              !adminCreation && state.customerOrder.type == 'PURCHASE_ACCESSORY'
            "
            :cart="customerStore.cart.containers"
          />
          <RentToOwnCart
            v-if="!adminCreation && state.customerOrder.type == 'RENT_TO_OWN'"
            :cart="customerStore.cart.containers"
          />
          <div v-if="adminCreation" class="col-span-5 mb-4 ml-4 field">
            <label for="notes" class="font-medium text-900 dark:text-0"
              >Notes</label
            >
            <Textarea id="notes" :autoResize="true" ::rows="5"></Textarea>
          </div>
        </template>
      </div>
      <div class="flex justify-end mt-4">
        <Button
          v-if="state.selectedStep < 3 && state.selectedStep > 0"
          @click="state.selectedStep--"
          label="Previous step"
          class="w-auto p-button-secondary"
        ></Button>
        <Button
          v-if="state.selectedStep < 2 && stepsEnabled"
          @click="state.selectedStep++"
          label="Next step"
          class="w-auto ml-4 p-button-success"
        ></Button>
        <Button
          v-if="state.selectedStep === 2 && stepsEnabled"
          label="Create Invoice"
          icon="pi pi-file"
          class="w-auto ml-4 p-button-primary"
          @click="createInvoice()"
        ></Button>
      </div>
    </div>
  </div>
  <div class="flex flex-wrap justify-center">
    <Button
      label="Back to quote"
      icon="pi pi-times"
      class="w-auto ml-4 p-button-warning"
      @click="cancel()"
    ></Button>
    <Button
      label="Create Invoice"
      icon="pi pi-file"
      class="w-auto ml-4 p-button-primary"
      @click="createInvoice()"
    ></Button>
  </div>
</template>

<script setup>
  import StateService from "@/service/StateService"
  import { reactive, onMounted, inject } from "vue"
  import CreateCustomer from "./CreateCustomer.vue"
  import CreateLineItem from "./CreateLineItem.vue"
  import PurchaseCart from "@/components/cart/PurchaseCart.vue"
  import AccessoryCart from "@/components/cart/AccessoryCart.vue"
  import RentalCart from "@/components/cart/RentalCart.vue"
  import RentToOwnCart from "@/components/cart/RentToOwnCart.vue"
  import CartService from "@/service/Cart"
  import cloneDeep from "lodash.clonedeep"
  import { useCustomerOrder } from "@/store/modules/customerOrder"

  const customerStore = useCustomerOrder()
  const cartService = new CartService()

  const defaultLineItem = {
    container: null,
    quantity: null,
    revenue: null,
    shipping_revenue: null,
    tax: null,
    total: null,
    door_orientation: "Facing cab"
  }
  const emptyCustomerOrder = {
    first_name: "",
    last_name: "",
    email: ""
  }

  const stateService = new StateService()
  const $formatCurrency = inject("$formatCurrency")
  const $isObjectPopulated = inject("$isObjectPopulated")
  const { customerOrderProp, cart, stepsEnabled, adminCreation } = defineProps([
    "customerOrderProp",
    "cart",
    "stepsEnabled",
    "adminCreation"
  ])

  const state = reactive({
    selectedStep: 0,
    isTaxable: true,
    containerAge: false,
    stateService: null,
    statesList: [],
    state: null,
    isDeliveryAddress: true,
    customerOrder: cloneDeep(emptyCustomerOrder),
    selectedCategory: { name: "Rental", code: "rental" },
    steps: [
      { label: "Customer Info", icon: "pi pi-user" },
      { label: "Address", icon: "pi pi-box" },
      { label: "Containers", icon: "pi pi-check" }
    ],
    categorys: [
      { name: "Rental", code: "rental" },
      { name: "Rent to Own", code: "rto" },
      { name: "Sale", code: "purchase" }
    ]
  })

  if (cart) {
    state.customerOrder = cartService.dtoCartToOrder(cart)
  }

  onMounted(() => {
    state.statesList = stateService.getStates()
    if ($isObjectPopulated(customerOrderProp)) {
      state.customerOrder = cloneDeep(customerOrderProp)
    }
  })

  const cancel = () => {
    state.customerOrder = cloneDeep(emptyCustomerOrder)
    state.selectedStep = 0
    customerStore.emptyContainerCart()
    customerStore.setCreateOrderStatus("NOT_STARTED")
  }

  const createInvoice = () => {
    console.log(state.customerOrder)
  }
</script>

<style></style>
