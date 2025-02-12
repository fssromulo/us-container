<template>
<div class="grid grid-cols-12 gap-4 formfrid p-fluid" style="max-width: 90vw">
  <div class="col-span-12 mt-4">
    <input type="hidden" name="campaign_url" v-model="state.campaign_url" id="campaign_url" class="campaign_url" />
    <input type="hidden" name="referral_source" v-model="state.referral_source" id="referral_source"
      class="referral_source" />
    <create-customer :adminCreation="false" :customerOrder="state.initialCusotmerOrder" :stepsEnabled="false"
      :disableAddressFields="true" :isPickupAddress="cartService.isPickupAddress(formattedCart)"
      :creating="state.creating" customerEmailNote="will send email"
      :address="prop.address" :customer="prop.customer" @validForm="createInvoice" />
    <div v-if="!$isPublic" class="flex flex-wrap justify-center">
      <p class="mb-4 text-2xl">Order Options</p>
    </div>
    <div v-if="!$isPublic && taxExemptVisible" class="col-span-12">
      <div class="flex flex-wrap justify-center mb-4">
        <div class="grid grid-cols-12 gap-4 mt-1 mr-4 p-fluid">
          <label> Tax Exempt </label>
        </div>
        <toggleSwitch v-model="state.taxExempt" />
      </div>
    </div>
    <div v-if="!$isPublic" class="col-span-12 ">
      <UpdateOrderSettings :showOrderStatus="showOrderStatusDropdown"
        :showShippingContainerToggle="state.customerOrder.type !== 'RENT'" @updatedAttributes="setAttributes"
        @updateFirstPaymentStrategy="updateFirstPaymentStrategy" @savePaymentStrategyNote="savePaymentStrategyNote" />
    </div>
    <div v-if="!$isPublic" class="flex flex-wrap justify-center mt-4">
      <div class="grid grid-cols-12 gap-2" v-for="c in state.cart">
        <div class="col-span-3 mt-8 text-xl" v-if="customerStore.cart['containers'].length && isRental">
          {{ c.container_size }}'
        </div>
        <div class="col-span-12 mt-8 text-xl md:col-span-3" v-else>
          {{ c.title }}
        </div>
        <div v-if="showFullRevenue" :class="{
              field: true,
              'mb-4': true,
              'col-span-4': true,
              'md:col-span-3': state.customerOrder.type === 'PURCHASE' || state.customerOrder.type === 'PURCHASE_ACCESSORY',
              'md:col-span-5': state.customerOrder.type === 'RENT',
            }">
          <label for="state" class="font-medium text-900 dark:text-0">Price </label>
          <InputNumber v-if="c.revenue != undefined" mode="currency" currency="USD" locale="en-US" v-model="c.revenue"
            class="p-inputtext-fluid" @keydown.enter="resetPriceIfSmaller()" @keydown.tab="resetPriceIfSmaller" />
          <InputNumber v-else mode="currency" currency="USD" class="p-inputtext-fluid" locale="en-US"
            v-model="c.price" />
        </div>
        <div v-if="showMonthlyRent" :class="{
              field: true,
              'mb-4': true,
              'col-span-4': true,
              'md:col-span-3': state.customerOrder.type === 'PURCHASE' || state.customerOrder.type === 'PURCHASE_ACCESSORY',
              'md:col-span-5': state.customerOrder.type === 'RENT',
            }">
          <label for="state" class="font-medium text-900 dark:text-0">Monthly Price</label>
          <InputNumber mode="currency" currency="USD" locale="en-US" class="p-inputtext-fluid" v-model="c.monthly_owed"
            :disabled="c.type === 'RENT_TO_OWN'" @keydown.enter="resetPriceIfSmaller()"
            @keydown.tab="resetPriceIfSmaller" />
        </div>

        <div :class="{
              field: true,
              'mb-4': true,
              'col-span-4': true,
              'md:col-span-3': state.customerOrder.type === 'PURCHASE' || state.customerOrder.type === 'PURCHASE_ACCESSORY',
              'md:col-span-6': state.customerOrder.type === 'RENT',
            }">
          <label for="shipping" class="font-medium text-900 dark:text-0">{{
            shippingText
            }}</label>

          <InputNumber mode="currency" currency="USD" locale="en-US" class="p-inputtext-fluid"
            v-model="c.shipping_revenue" @keydown.enter="resetPriceIfSmaller()" @keydown.tab="resetPriceIfSmaller" />
        </div>
      </div>
    </div>
    <div class="flex flex-wrap justify-center mt-4">
      <p class="mb-4 text-2xl">Cart</p>
    </div>
    <div class="flex flex-wrap justify-center mt-4" v-for="(currentCart, index) in customerStore.cart.cartTypes.sort(
          (a, b) => {
            if (a.property < b.property) return 1;
            else return -1;
          }
        )" :key="index">
      <!-- <p
          class="text-2xl"
          v-if="customerStore.cart[currentCart.property].length"
        >
          {{ currentCart.note }}
        </p> -->
      <br />
      <p class="mt-1 text-2xl" v-if="customerStore.cart[currentCart.property].length">
        {{ currentCart.header }}
      </p>

      <RentalCart v-if="customerStore.cart[currentCart.property].length && isRental" :verticalTable="smAndSmaller"
        :columnsFieldMap="currentCart.fieldsMap" :cart="
            cartService.displayCart(
              cloneDeep(
                cartService.dtoProductToCart(
                  customerStore.cart[currentCart.property], down_payment_strategy
                )
              )
            )
          " :showContainerPlusShipping="state.attributes.show_subtotal_only" :showConvenienceFee="false"
        :showTax="state.customerOrder.line_items[0].tax > 0" :inCreateInvoiceWizard="true"
        :showAbbrevTitleWContainerNumber="userStore?.cms?.rent_options?.show_abbrev_title_w_container_number"
        />
      <PurchaseCart v-if="customerStore.cart[currentCart.property].length && isPurchase" :verticalTable="smAndSmaller"
        :columnsFieldMap="currentCart.fieldsMap" :cart="
            cartService.displayCart(
              cloneDeep(
                cartService.dtoProductToCart(
                  customerStore.cart[currentCart.property], down_payment_strategy
                )
              )
            )
          " :showContainerPlusShipping="state.attributes.show_subtotal_only" :showConvenienceFee="false"
        :showTax="state.customerOrder.line_items[0].tax > 0" :inCreateInvoiceWizard="true" />
        <AccessoryCart v-if="customerStore.cart[currentCart.property].length && isAccessory" :verticalTable="smAndSmaller"
        :columnsFieldMap="currentCart.fieldsMap" :cart="
            cartService.displayCart(
              cloneDeep(
                cartService.dtoProductToCart(
                  customerStore.cart[currentCart.property], down_payment_strategy
                )
              )
            )
          " :showContainerPlusShipping="state.attributes.show_subtotal_only" :showConvenienceFee="false"
        :showTax="state.customerOrder.line_items[0].tax > 0" :inCreateInvoiceWizard="true" />
      <RentToOwnCart v-if="customerStore.cart[currentCart.property].length && isRentToOwn" :verticalTable="smAndSmaller"
        :columnsFieldMap="currentCart.fieldsMap" :cart="
            cartService.displayCart(
              cloneDeep(
                cartService.dtoProductToCart(
                  customerStore.cart[currentCart.property], down_payment_strategy
                )
              )
            )
          " :showContainerPlusShipping="state.attributes.show_subtotal_only" :showConvenienceFee="false"
        :showTax="state.customerOrder.line_items[0].tax > 0" :inCreateInvoiceWizard="true" />
    </div>
    <div class="flex flex-wrap justify-center mt-4">
      <div>
        <p class="mt-4 text-2xl" v-if="cartService.getTotalTax(state.cart) != 0">
          Sub Total:
          {{
          $fc(
          cartService.getCartTotal(
          state.cart,
          down_payment_strategy
          )
          )
          }}
        </p>
        <p class="text-2xl" v-if="
              cartService.getTotalTax(state.cart) != 0 &&
              cartService.getTotalCartRTO(state.cart) == 0 &&
              state.taxExempt == false
            ">
          Sales Tax:
          {{ $fc(cartService.getTotalTax(state.cart)) }}
        </p>
        <hr v-if="cartService.getTotalTax(state.cart) != 0" />
        <p class="mb-4 text-2xl" v-if="cartService.getTotalCartRTO(state.cart) == 0">
          Total:
          {{
          $fc(
          cartService.getCartTotal(
          state.cart,
          down_payment_strategy
          ) + cartService.getTotalTax(state.cart)
          )
          }}
        </p>
        <!-- <p class="mb-4 text-2xl" v-else>
            Total 30 Days Price:
            {{
              $fc(
                cartService.getCartTotal(state.cart) +
                  cartService.getTotalTax(state.cart)
              )
            }}
          </p> -->
        <p class="mb-4 text-2xl" v-if="cartService.getTotalCartRTO(state.cart) != 0">
          Total RTO Price:
          {{ $fc(cartService.getTotalCartRTO(state.cart)) }}
        </p>
      </div>
    </div>
  </div>
</div>
<div v-if="invoiceSendingOptions.email && invoiceSendingOptions.sms" class="flex flex-wrap justify-center mt-4">
  <label>How do you want to send this invoice?</label>
</div>
<div v-if="invoiceSendingOptions.email && invoiceSendingOptions.sms" class="flex flex-wrap justify-center mt-4">
  <div class="mr-4">
    <Checkbox v-model="sendEmailCheckbox" :binary="true"></Checkbox> Email
  </div>
  <div class="mr-4">
    <Checkbox v-model="sendSMSCheckbox" :binary="true"></Checkbox> SMS
  </div>
  <div class="mr-4">
    <Checkbox v-model="selectAll" :binary="true"></Checkbox> Both
  </div>
</div>
<div class="flex flex-wrap justify-center mt-4">
  <Button label="Create Order" icon="pi pi-file" :loading="state.loading" :class="
        smAndSmaller
          ? 'w-full p-button-primary mt-2'
          : 'ml-4 w-auto p-button-primary'
      " @click="state.creating = true"></Button>
  <Button v-if="$isPublic" label="Email Quote" icon="pi pi-send" :loading="state.loading" :class="
        smAndSmaller
          ? 'w-full p-button-secondary mt-2'
          : 'ml-4 w-auto p-button-secondary'
      " @click="state.creating = true"></Button>
  <Button label="Cancel" icon="pi pi-times" :class="
        smAndSmaller
          ? 'w-full p-button-warning mt-2'
          : 'ml-4 w-auto p-button-warning'
      " @click="cancel()"></Button>
</div>
<Message v-if="state.errors" life="3000" severity="error">All fields required</Message>
</template>

<script setup>
import StateService from "@/service/StateService";
import { reactive, onMounted, onUnmounted, inject, computed, watch } from "vue";
import CreateCustomer from "./CreateCustomer.vue";
import PurchaseCart from "@/components/cart/PurchaseCart.vue";
import AccessoryCart from "@/components/cart/AccessoryCart.vue";
import RentalCart from "@/components/cart/RentalCart.vue";
import RentToOwnCart from "@/components/cart/RentToOwnCart.vue";


import UpdateOrderSettings from "./UpdateOrderSettings.vue";
import CartService from "@/service/Cart";
import CustomerApi from "@/api/customers";
import { useToast } from "primevue/usetoast";

import cloneDeep from "lodash.clonedeep";
import { useCustomerOrder } from "@/store/modules/customerOrder";
import { emptyCustomerOrder } from "../../../utils/constants";
import { breakpointsTailwind, useBreakpoints } from "@vueuse/core";
import { useUsers } from "@/store/modules/users";
import { useTaxes } from "@/store/modules/taxes";
import { accountMap } from "../../../utils/accountMap";
import { useInvoiceHelper } from "@/store/modules/invoiceHelper";
import { useDownpaymentStrategyStore } from "@/store/modules/downpaymentStrategyHelper";
import QuoteGenerationService from "@/service/QuoteGeneration";
import TaxService from "@/service/Tax";

const downpaymentStrategyStore = useDownpaymentStrategyStore();

const invoiceHelperStore = useInvoiceHelper();

const $fc = inject("$formatCurrency");

const taxStore = useTaxes();
const $isPublic = inject("$isPublic");

const breakpoints = useBreakpoints(breakpointsTailwind);
const smAndSmaller = breakpoints.isSmallerOrEqual("sm");

const customerStore = useCustomerOrder();
const customerApi = new CustomerApi();
const cartService = new CartService();
const toast = useToast();
const quoteGenerationService = new QuoteGenerationService();

const stateService = new StateService();
const $isObjectPopulated = inject("$isObjectPopulated");
const $route = inject("$route");
const $ability = inject("$ability");

const userStore = useUsers();

const taxService = new TaxService();


const prop = defineProps({
  customerOrder: {
    type: Object,
    default: {}
  },
  address: {
    type: Object,
    default: null
  },
  customer: {
    type: Object,
    default: null
  },
  dupplicationMode: {
    type: Boolean,
    default: null
  },
  overridden_user_id: {
    type: String,
    default: null
  }
});

const taxExemptVisible = computed(() => {
  if(customerStore?.publicCms?.tax_exempt_toggle != undefined && customerStore?.publicCms?.tax_exempt_toggle == true){
    return true;
  } else {
    return false;
  }
})

const down_payment_strategy = computed(() => {
  if(state.first_payment_strategy == '' || !state.first_payment_strategy)
    return userStore?.cms?.rent_options.down_payment_strategy;
  else {
    return state.first_payment_strategy;
  }
});
const defaultPublicOrderStatus = computed(() => {
  return userStore?.cms?.default_public_order_status || 'Invoiced';
})

const showOrderStatusDropdown = computed(() => {
  return userStore?.cms?.feature_flags?.select_status_on_order_creation;
});

const invoiceSendingOptions = computed(() => {
  const options = userStore?.cms?.invoice_sending_options || {};
  return {
    email: options.email || false,
    sms: options.sms || false,
  };
});

const showFullRevenue = computed(() => {
  return state.cart?.every(
    (c) =>
      c.type == "PURCHASE" ||
      c.product_type == "CONTAINER_ACCESSORY" ||
      c.type == "RENT_TO_OWN"
  );
});

const isRentToOwn = computed(() => {
  return state.cart?.every((c) => c.type == "RENT_TO_OWN");
});

const isRental = computed(() => {
  return state.cart?.every((c) => c.type == "RENT");
});

const isPurchase = computed(() => {
  return state.cart?.every((c) => c.type == "PURCHASE");
});

const isAccessory= computed(() => {
  return state.cart?.every((c) => c.type == "PURCHASE_ACCESSORY");
});

const shippingText = computed(() => {
  return isRental.value ? "Drop off / Pickup" : "Shipping";
});


const isDelivery = computed(() => {
  return state.cart?.every((c) => c.shipping_revenue > 0);
});

const formattedCart = computed(() => {
  let cart = [];
  for (var i = 0; i < customerStore.cart.cartTypes.length; i++) {
    cart = cart.concat(
      customerStore.cart[customerStore.cart.cartTypes[i].property]
    );
  }
  return cart;
});

const showMonthlyRent = computed(() => {
  return state.cart?.every((c) => c.type == "RENT" || c.type == "RENT_TO_OWN");
});

const sendEmailCheckbox = reactive(false);
const sendSMSCheckbox = reactive(false);

const selectAll = computed({
  get() {
    return sendEmailCheckbox.value && sendSMSCheckbox.value;
  },
  set(value) {
    sendEmailCheckbox.value = value;
    sendSMSCheckbox.value = value;
  },
});

const messageType = computed(() => {
  const { email, sms } = invoiceSendingOptions;

  if (email && !sms) return 'E';
  if (sms && !email) return 'S';

  if (sendEmailCheckbox.value && sendSMSCheckbox.value) return 'A';
  if (sendEmailCheckbox.value) return 'E';
  if (sendSMSCheckbox.value) return 'S';

  return 0;
});

const state = reactive({
  selectedStep: 0,
  attributes: {},
  statesList: [],
  creating: false,
  loading: false,
  errors: false,
  customerOrder: cloneDeep(emptyCustomerOrder),
  cart: null,
  updatedCart: [],
  originalCart: null,
  selectedStatus: null,
  originalCart: null,
  first_payment_strategy: "",
  first_payment_strategy_note: "",
  campaign_url:"",
  referral_source:"",
  taxExempt: false,
  saved_order: null
});

if (formattedCart.value.length > 0) {
  const cart = cloneDeep(cartService.dtoProductToCart(formattedCart.value, down_payment_strategy.value));
  state.cart = cart;
  state.originalCart = cloneDeep(cart);
}

if (formattedCart.value.length > 0) {
  let cart = cartService.dtoProductToCart(formattedCart.value, down_payment_strategy.value);
  const customerOrder = cartService.dtoCartToOrder(cart);
  customerStore.setCustomer(customerOrder);
}

onMounted(() => {
  state.statesList = stateService.getStates();
  if ($isObjectPopulated(prop.customerOrder)) {
    state.customerOrder = cloneDeep(prop.customerOrder);
  }
  state.originalCart = cloneDeep(state.cart);

  document.addEventListener('click', resetPriceIfSmaller);

});

onUnmounted(() => {
  document.removeEventListener('click', resetPriceIfSmaller);
});

const resetPriceIfSmaller = () => {
  if($ability.can('update', 'decrease-cart_line_item_price')){
    return
  }
  for(var j = 0; j < state.cart.length; j++) {
    let element = state.cart[j];
    for (var i = 0; i < state.originalCart.length; i++) {
      if (i == j) {
        if (element.revenue < state.originalCart[i].revenue) {
          element.revenue = state.originalCart[i].revenue;
        }
        if (element.shipping_revenue < state.originalCart[i].shipping_revenue) {
          element.shipping_revenue = state.originalCart[i].shipping_revenue;
        }
        if (element.monthly_owed < state.originalCart[i].monthly_owed) {
          element.monthly_owed = state.originalCart[i].monthly_owed;
        }
      }
    }
  };
};

const setAttributes = (attributes) => {
  state.attributes = attributes;
};

const savePaymentStrategyNote = (note) => {
  state.first_payment_strategy_note = note;
}

const updateFirstPaymentStrategy = (first_payment_strategy) => {
  state.first_payment_strategy = first_payment_strategy;
  downpaymentStrategyStore.setDownpaymentStrategy(first_payment_strategy)
}

const cancel = () => {
  state.customerOrder = cloneDeep(emptyCustomerOrder);
  state.selectedStep = 0;
  state.creating = false;
  customerStore.emptyContainerCart();
  customerStore.setCreateOrderStatus("NOT_STARTED");
};

const createProductInvoice = async (lineItems, order_type) =>{
  state.customerOrder.order.type = order_type
  state.customerOrder.order.line_items = [...lineItems]
  let total = cartService.getCartTotal(state.cart);
  state.customerOrder.order.total_price = total;
  state.customerOrder.order.subtotal_price = total;
  state.customerOrder.order.remaining_balance = total + cartService.getTotalTax(state.cart);
  state.customerOrder.order.first_payment_strategy = state.first_payment_strategy;
  state.customerOrder.order.tax_exempt = state.taxExempt
  state.customerOrder.order.overridden_user_id = prop.overridden_user_id
  // state.customerOrder.order.
  if(state.first_payment_strategy.length != 0){
    const requestData = {
      title: "downpayment_note",
      content: state.first_payment_strategy_note,
    };
    state.customerOrder.order.note = requestData
  }
  return $isPublic
    ? await customerApi.createCustomerOrderPublic(
        state.customerOrder,
        userStore.cms.id,
        $route.currentRoute.value.query.code
      )
    : await customerApi.createCustomerOrder(state.customerOrder);
}

const createInvoice = async (valid) => {
  state.errors = false;
  if (!valid) {
    state.creating = valid;
    state.errors = true;
    state.creating = false;
    return;
  }
  let cartPriceTooLow = false;
  // placeholder permission, need to add more granular
  if (!$ability.can("read", "all_orders")) {
    state.cart.map((c, i) => {
      if (c.revenue < state.originalCart[i].revenue) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Price cannot be less than original price",
          group: "br",
          life: 4000,
        });
        state.creating = false;
        cartPriceTooLow = true;
        return;
      }
      if (c.shipping_revenue < state.originalCart[i].shipping_revenue) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Shipping cannot be less than original shipping",
          group: "br",
          life: 4000,
        });
        state.creating = false;
        cartPriceTooLow = true;
        return;
      }
    });
  }
  if (messageType.value === 0) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Select how you want to send this invoice",
      group: "br",
      life: 4000,
    });
    state.creating = false;
    return;
  }
  if (cartPriceTooLow) {
    return;
  }
  const applications = customerStore?.publicCms?.applications
  state.customerOrder = Object.assign(
    cloneDeep(state.customerOrder),
    cloneDeep(customerStore.customer)
  );
  state.customerOrder.order.address = cloneDeep(customerStore.address);
  state.customerOrder.order.billing_address = cloneDeep(customerStore.billing_address);
  state.customerOrder.order.status = state.selectedStatus;
  state.customerOrder.order.attributes = state.attributes;
  state.customerOrder.order.campaign_url = state.campaign_url;
  state.customerOrder.order.referral_source = state.referral_source;
  state.customerOrder.order.message_type = messageType.value;
  let accessoryLineItems = cartService.dtoCartToAccessoryOrder(
    state.cart
  ).order.line_items;
  let container_attributes = await customerApi.get_all_container_attributes()
  let pairs = container_attributes.data.value;
  let containerLineItems = cartService.dtoCartToContainerOrder(
    state.cart, pairs
  ).order.line_items;
  state.loading = true;
  const originalOrderType = state.customerOrder.order.type
  const accessoryOrderType = "PURCHASE_ACCESSORY"
  if(accessoryLineItems.length > 0){
    let {data, error} = await createProductInvoice(accessoryLineItems, accessoryOrderType)
    if (error.value) {
      state.loading = false;
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error creating invoice",
        group: "br",
        life: 4000,
      });
      state.creating = false;
      return;
    }
  }
  if(containerLineItems.length > 0){
    let {data, error} = await createProductInvoice(containerLineItems, originalOrderType)
    if (error.value) {
      state.loading = false;
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error creating invoice",
        group: "br",
        life: 4000,
      });
      state.creating = false;
      return;
    }
    toast.add({
    severity: "success",
    summary: "Success",
    detail: "Invoice created successfully",
    group: "br",
    life: 4000,
    });
    if ($isPublic) {
      let invoice_email_link = customerStore.publicCms?.links?.invoice_email_link
      window.location.href = invoice_email_link + `${data.value.order[0].id}`
      return;
    }
  }  
  state.loading = false;

  customerStore.setCustomer(null);
  customerStore.setAddress(null);
  customerStore.emptyContainerCart();
  customerStore.resetCreateOrderStatus();

  customerStore.setForceRefresh(true);

  if(prop.dupplicationMode){
    invoiceHelperStore.hideOrderDetails = !invoiceHelperStore.hideOrderDetails;
  }

  $route.push({
    name: "invoices",
    query: { status: "invoiced", forceRefresh: true },
  });

};

// on any update to the cart when creating the invoice, we will update everything
watch(
  () => state.cart,
  async (newVal, oldVal) => {
    state.cart.map(async (c, i) => {
      if (state.originalCart[i].revenue > newVal[i].revenue && !$ability.can('update', 'decrease-cart_line_item_price')) {
        state.cart[i].revenue = state.originalCart[i].revenue;
        return;
      }
      if (c.tax != 0) {
        const shipping_revenue = c.shipping_revenue;
        c.tax = await taxService.calculateTax(
          {
            monthly_price: c.monthly_owed,
            state: c.product_state,
            price: c.revenue
          },
          isDelivery.value, taxStore.taxes, c.type, state.first_payment_strategy, shipping_revenue, c.destination_state
        );
      }
      c.subTotal =
        typeof c.shipping_revenue !== undefined &&
        typeof c.revenue !== "undefined"
          ? c.shipping_revenue + c.revenue
          : c.price;
      c.shipping_revenue = newVal[i].shipping_revenue;
      c.revenue = newVal[i].revenue;
      c.price = newVal[i]?.price || 0;
      c.container_plus_shipping =
        typeof newVal[i].revenue !== undefined &&
        typeof newVal[i].shipping_revenue !== "undefined"
          ? newVal[i].revenue + newVal[i].shipping_revenue
          : newVal[i].price + newVal[i]?.shipping_revenue || 0;

      if (c.rent_period) {
        let rto_rate_obj = userStore.cms.rent_to_own_rates.find((r) => {
          return r.months == c.rent_period;
        });
        if (newVal[i].revenue !== undefined) {
          c.thirtyDayPrice = cartService.roundIt(
            newVal[i].revenue + newVal[i].shipping_revenue + c.tax,
            2
          );
          c.total_rental_price = cartService.roundIt(
            (c.thirtyDayPrice / rto_rate_obj.divide_total_price_by) *
              rto_rate_obj.months,
            2
          );

          c.monthly_owed = c.total_rental_price / rto_rate_obj.months;
        } else {
          c.thirtyDayPrice = cartService.roundIt(
            newVal[i].price + newVal[i].shipping_revenue + c.tax,
            2
          );
          c.total_rental_price = cartService.roundIt(
            (c.thirtyDayPrice / rto_rate_obj.divide_total_price_by) *
              rto_rate_obj.months,
            2
          );
        }
      }
    });
  },
  { deep: true }
);

watch(
  () => state.cart,
  (newVal) => {
    invoiceHelperStore.setCart(newVal);
  },
  { deep: true, immediate: true }
);

watch(
  () => customerStore.customer,
  (newVal) => {
    if (newVal !== null) {
      if ($isPublic){
        // let account_id = accountMap[window.location.host].account_id;
        // if (account_id == 1) {
        //   state.selectedStatus = "Invoiced"
        // } else {
        //   state.selectedStatus = "Estimate"
        // }
        state.selectedStatus = defaultPublicOrderStatus.value
      }
      else{
        state.selectedStatus = cloneDeep(newVal.order?.status) || "Invoiced";
      }
    }
  },
  { deep: true, immediate: true }
);
</script>

<style></style>
