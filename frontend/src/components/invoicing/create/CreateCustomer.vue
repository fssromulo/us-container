<template>
  <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
    <template v-if="state.selectedStep === 0 || !props.stepsEnabled">
      <div class="col-span-12 mb-3 text-xl font-medium text-900">Customer info</div>
      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="first_name" class="font-medium text-900">First Name</label>
        <InputText
          v-model="state.customer.first_name"
          :class="{ 'p-invalid': v$.customer.first_name.$invalid }"
          id="first_name"
          type="text"
          :disabled="inputs_disabled"
          class="p-component p-inputtext-fluid"
          @blur="updateStore"
        />
      </div>
      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="last_name" class="font-medium text-900">Last Name</label>
        <InputText
          v-model="state.customer.last_name"
          :class="{ 'p-invalid': v$.customer.last_name.$invalid }"
          id="last_name"
          type="text"
          :disabled="inputs_disabled"
          class="p-component p-inputtext-fluid"
          @blur="updateStore"
        />
      </div>

      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="email" class="font-medium text-900">Customer Email</label>
        <small class="ml-2" v-if="props.customerEmailNote.length > 0"
          >( {{ props.customerEmailNote }} )</small
        >

        <InputText
          :class="{ 'p-invalid': v$.customer.email.$invalid }"
          v-model="state.customer.email"
          id="email"
          type="text"
          :disabled="inputs_disabled"
          class="p-component p-inputtext-fluid"
          @blur="updateStore"
        />
      </div>

      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="phone" class="font-medium text-900">Phone</label>
        <InputMask
          mode="decimal"
          v-if="state.customer == undefined"
          mask="(999) 999-9999"
          placeholder="(999) 999-9999"
          :useGrouping="false"
          v-model="state.customer.phone"
          :class="{ 'p-invalid': v$.customer.phone.$invalid }"
          id="phone"
          type="phone"
          :disabled="inputs_disabled"
          class="p-component p-inputtext-fluid"
          @blur="updateStore"
        />
        <InputMask
          mode="decimal"
          v-if="state.customer != undefined"
          mask="(999) 999-9999"          
          placeholder="(999) 999-9999"
          :useGrouping="false"
          v-model="state.customer.phone"
          id="phone"
          type="phone"
          :disabled="inputs_disabled"
          class="p-component p-inputtext-fluid"
          @blur="updateStore"
        />
      </div>

      <div class="col-span-12 mb-3 field md:col-span-4">
        <label for="company" class="font-medium text-900">Company name</label>

        <InputText
          v-model="state.customer.company_name"
          id="email"
          type="text"
          :disabled="inputs_disabled"
          class="p-component p-inputtext-fluid"
          @blur="updateStore"
        />
      </div>
    </template>

  <template v-if="state.selectedStep === 1 || !props.stepsEnabled">
    <div class="col-span-12">
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 text-xl font-medium text-900 dark:text-0">
          {{
          !props.isPickupAddress ? "Deliver to address" : "Picking up from"
          }}
        </div>
        
        <div v-if="has_billing_address" class="col-span-12">
          <Checkbox v-model="state.billing_same_as_delivery" :binary="true" />
          <label> Billing same as delivery </label>
        </div>
        <div v-if="!props.isPickupAddress" class="col-span-12 mb-3 field md:col-span-4">
          <label for="street_address" class="font-medium text-900"
            >Street address</label
          >
          <InputText
            v-model="state.address.street_address"
            id="street_address"
            :class="{ 'p-invalid': v$.address.street_address.$invalid }"
            type="text"
            maxlength="60"
            :disabled="inputs_disabled"
            class="p-component p-inputtext-fluid"
            @blur="updateStore"
          />
        </div>
        <div class="col-span-12 mb-3 field md:col-span-4">
          <label for="city" class="font-medium text-900">City</label>
          <InputText
            :disabled="props.disableAddressFields || inputs_disabled"
            v-model="state.address.city"
            id="city"
            type="text"
            class="p-component p-inputtext-fluid"            
            @blur="updateStore"
          />
        </div>
        <div class="col-span-12 mb-4 md:col-span-4" v-if="getAccountCountry != 'Canada'">
          <label for="company_name" class="font-medium text-900 dark:text-0">County</label>
          <small class="ml-2">(Optional)</small>

          <InputText
            :disabled="props.disableAddressFields || inputs_disabled"
            v-model="state.address.county"
            id="company_name"
            type="text"
            class="p-component p-inputtext-fluid"            
            @blur="updateStore"
          />
        </div>
        <div v-if="getAccountCountry == 'Canada'" class="col-span-12 mb-4 md:col-span-4">
          <label for="state" class="font-medium text-900 dark:text-0">Province</label>
          <InputText class="p-inputtext p-component p-inputtext-fluid" 
          
          :disabled="props.disableAddressFields" v-model="state.address.province" placeholder="Province"
            @blur="updateStore" />
        </div>
        <div v-else class="col-span-12 mb-3 field md:col-span-4">
          <label for="state" class="font-medium text-900">State</label>
          <Select
            :disabled="props.disableAddressFields || inputs_disabled"
            v-model="state.address.state"
            class="p-component p-inputtext-fluid"
            placeholder="State"
            :options="state.statesList"
            @blur="updateStore"

          />
        </div>
        <div class="col-span-12 mb-3 field md:col-span-4">
          <label for="zip" class="font-medium text-900">{{ postalZipText }}</label>
          <InputText
            :disabled="props.disableAddressFields || inputs_disabled"
            id="zip"
            v-model="state.address.zip"
            class="p-component p-inputtext-fluid"
            type="text"
            @blur="updateStore"
          />
        </div>
      </div>
    </div>
    <div v-if="props.adminCreation" class="col-span-12 mb-4 field md:col-span-3">
      <ToggleButton v-model="state.isDeliveryAddress" onLabel="Delivery Address" offLabel="Pickup Address"
        onIcon="pi pi-car" offIcon="pi pi-file" />
    </div>
    <div v-if="props.adminCreation" class="col-span-12 mb-4 field md:col-span-3">
      <Button v-if="state.isDeliveryAddress" label="Calculate shipping" icon="pi pi-car"
        class="w-auto p-button-secondary"></Button>
    </div>

    <div class="grid grid-cols-12 gap-4 formgrid p-fluid" v-if="!state.billing_same_as_delivery && has_billing_address">
      <div class="col-span-12 mb-4 text-xl font-medium text-900 dark:text-0">
        <p> Billing Address </p>
      </div>
      <div v-if="!props.isPickupAddress" class="col-span-12 mb-4 field md:col-span-4">
        <label for="street_address" class="font-medium text-900 dark:text-0">Street address</label>
        <InputText v-model="state.billing_address.street_address" id="street_address" type="text" maxlength="60"
          @blur="updateStore" />
      </div>
      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="city" class="font-medium text-900 dark:text-0">City</label>
        <InputText v-model="state.billing_address.city" id="city" type="text" @blur="updateStore" />
      </div>
      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="company_name" class="font-medium text-900 dark:text-0">County</label>
        <small class="ml-2">(Optional)</small>

        <InputText v-model="state.billing_address.county" id="company_name" type="text" @blur="updateStore" />
      </div>
      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="state" class="font-medium text-900 dark:text-0">{{ stateProvinceText }}</label>
        <Select v-model="state.billing_address.state" :placeholder="stateProvinceText"
          :options="getAccountCountry == 'Canada' ? state.provinceList : state.statesList" @blur="updateStore" />
      </div>
      <div class="col-span-12 mb-4 field md:col-span-4">
        <label for="zip" class="font-medium text-900 dark:text-0">{{ postalZipText }}</label>
        <InputText id="zip" v-model="state.billing_address.zip" type="text" @blur="updateStore" />
      </div>
    </div>
  </template>
</div>
</template>

<script setup>
import { reactive, watch, onMounted, inject, computed } from "vue";
import StateService from "@/service/StateService";
import cloneDeep from "lodash.clonedeep";
import { useCustomerOrder } from "@/store/modules/customerOrder";

import { useVuelidate } from "@vuelidate/core";
import { required, email } from "@vuelidate/validators";
import { useUsers } from "@/store/modules/users";
import AccountApi from "@/api/account";
import { accountMap } from "../../../utils/accountMap";
import { useToast } from "primevue/usetoast";
import { useCustomerHelper } from "@/store/modules/customerHelper";


const customerHelper = useCustomerHelper();

const toast = useToast();

const customerStore = useCustomerOrder();

const accountApi = new AccountApi();

const $isObjectPopulated = inject("$isObjectPopulated");
const stateService = new StateService();

const emit = defineEmits(["validForm"]);

const $isPublic = inject("$isPublic");

const userStore = useUsers();

const postalZipText = computed(()=>{
  return userStore.cms?.account_country && userStore.cms?.account_country == 'Canada' ? "Postal Code": "Zip"
});
const stateProvinceText = computed(()=>{
  return userStore.cms?.account_country && userStore.cms?.account_country == 'Canada' ? "Province": "State"
});

const inputs_disabled = computed(() => {
  return customerHelper.disable;
})


const props = defineProps({
  forceReset: {
    type: Boolean,
    default: false,
  },
  stepsEnabled: {
    type: Boolean,
    default: false,
  },
  customerOrder: {
    type: Object,
    default: () => ({}),
  },
  adminCreation: {
    type: Boolean,
    default: false,
  },
  disableAddressFields: {
    type: Boolean,
    default: false,
  },
  isPickupAddress: {
    type: Boolean,
    default: false,
  },
  creating: {
    type: Boolean,
    default: false,
  },
  customerEmailNote: {
    type: String,
    default: "",
  },
  address: {
    type: Object,
    default: null
  },
  customer: {
    type: Object,
    default: null
  }
});

const state = reactive({
  selectedStep: 0,
  customer: {},
  address: {},
  isDeliveryAddress: true,
  forceReset: props.forceReset,
  billing_same_as_delivery: true,
  billing_address: {}
});

onMounted(async() => {
  state.statesList = stateService.getStates();
  state.provinceList = stateService.getProvinces();
  if (!props.forceReset) {
    state.customer = cloneDeep(customerStore.customer);
    state.address = cloneDeep(customerStore.address);

    if(has_billing_address){
      state.billing_address = cloneDeep(customerStore.address);
    } else {
      state.billing_address = null;
    }
  }

  if(props.customer && props.address){
    state.customer.first_name = props.customer.first_name;
    state.customer.last_name = props.customer.last_name;
    state.customer.email = props.customer.email;
    state.customer.company_name = props.customer.company_name;
    state.customer.phone = "" + props.customer.phone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "");
    state.address = cloneDeep(props.address);
  }

  if($isPublic){
    let account_id = accountMap[window.location.host].account_id;

    const {data, error} = await accountApi.getPublicAccount(
        account_id
      );

    if(error.value != undefined){
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error syncing account.",
          group: "br",
          life: 4000,
        });
        return
    }
    customerStore.setPublicCms(data.value);
  }
});

const getAccountCountry = computed(() => {
  let account_country = userStore.cms.account_country;
  return account_country;
})

const has_billing_address = computed(() => {
  return ($isPublic ? customerStore.publicCms?.billing_address : userStore?.cms?.billing_address) == true;
})

const addressRequired = !props.isPickupAddress
  ? { required, $lazy: true, max: 60 }
  : {};
const rules = computed(() => ({
  customer: {
    first_name: { required, $lazy: true },
    last_name: { required, $lazy: true },
    phone: { required, $lazy: true },
    email: { required, email, $lazy: true },
  },
  address: { street_address: addressRequired },
}));

const v$ = useVuelidate(rules, state);
const updateStore = async () => {
  customerStore.setCustomer(state.customer);
  customerStore.setAddress(state.address);
  if(has_billing_address){
    if(state.billing_same_as_delivery){
      customerStore.setBillingAddress(state.address);
    } else {
      customerStore.setBillingAddress(state.billing_address);
    }
  } else {
    customerStore.setBillingAddress(null);
  }
};
watch(
  () => props.creating,
  async (newVal) => {
    if (newVal) {
      const validation = await v$.value.$validate();
      if (validation) {
        customerStore.setCustomer(state.customer);
        customerStore.setAddress(state.address);
          if(has_billing_address){

            if(state.billing_same_as_delivery){
              customerStore.setBillingAddress(state.address);
            } else {
              customerStore.setBillingAddress(state.billing_address);
            }
          } else {
            customerStore.setBillingAddress(null);
          }
      }
      emit("validForm", validation);
    }
  }
);
watch(
  () => customerStore.customer,
  async (newVal) => {
    if (!state.forceReset) {
      state.customer = cloneDeep(customerStore.customer);
      state.address = cloneDeep(customerStore.address);
    } else {
      state.forceReset = false;
    }
  }
);

watch(
  () => customerHelper.version,
  async (newVal) => {
    state.customer.first_name = customerHelper.first_name;
    state.customer.last_name = customerHelper.last_name;
    state.customer.company_name = customerHelper.company_name;
    state.customer.email = customerHelper.customer_email;
    state.customer.phone = customerHelper.customer_phone;

    state.address.street_address = customerHelper.street_address;
    state.address.city = customerHelper.city;
    state.address.state = customerHelper.state;
    state.address.zip = customerHelper.zip;
    state.address.county = customerHelper.county;
  }
)
</script>
