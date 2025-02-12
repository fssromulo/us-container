<template>
  <div>
    <div v-if="!$ability.can('update', 'settings_invoice_column_ordering')">
      <container-invoicecolumnordering v-if="state.active === 0">
      </container-invoicecolumnordering>
      <!-- <CreateUser :isAdmin="false" :userProp="usersStore.currentUser" /> -->
    </div>
    <div v-else>
      <!-- tabs -->
      <ul
        class="flex p-2 m-0 overflow-x-scroll list-none select-none bg-0 dark:bg-900"
        style="max-width: 95vw"
      >
        <template :key="idx" v-for="(name, idx) in state.componentList">
          <li class="pr-4 md:pr-1">
            <a
              v-ripple
              class="flex items-center px-6 py-4 transition-colors duration-150 cursor-pointer md:px-2 hover:bg-100 dark:hover:bg-700 rounded-border p-ripple"
              :style="[
                state.active === idx ? { color: 'white !important' } : ''
              ]"
              :class="{
                'p-button p-component p-button-secondary': state.active === idx,
                'text-700 dark:text-100': state.active !== idx
              }"
              @click="state.active = idx"
            >
              <span class="text-lg font-medium md:text-2xl">{{ name }}</span>
            </a>
          </li>
          <li class="flex items-center">
            <div style="width: 1px; height: 50%" class="border border-r"></div>
          </li>
        </template>
      </ul>

      <!-- Declaring the components -->
      <CouponSettings v-if="state.active === 0"></CouponSettings>
      <container-invoicecolumnordering v-if="state.active === 1">
      </container-invoicecolumnordering>
      <container-integrations v-if="state.active === 2">
      </container-integrations>
      <container-invoicepage v-if="state.active === 3"> </container-invoicepage>
      <Rates v-if="state.active === 4"> </Rates>
      <container-emails v-if="state.active === 5"></container-emails>
      <OtherSettings v-if="state.active === 6"> </OtherSettings>
      <!-- <SettingsRefactor v-if="state.active == 7" :data="state.cms"></SettingsRefactor> -->
      <LogisticsZonesSettings v-if="state.active === 7">
      </LogisticsZonesSettings>
    </div>

    <div class="m-5">
      <CreateUser :isAdmin="false" :userProp="usersStore.currentUser" />
    </div>
  </div>
</template>

<script setup>
  import { computed, inject, reactive, onMounted } from "vue"
  // Importing the components
  import containerInvoicecolumnordering from "@/components/invoicing/InvoiceColumnOrdering.vue"
  import containerIntegrations from "@/components/settings/Integrations.vue"
  import containerInvoicepage from "@/components/settings/InvoicePage.vue"
  import Rates from "@/components/settings/Rates.vue"
  import containerEmails from "@/components/settings/ContainerEmails.vue"
  import OtherSettings from "@/components/settings/OtherSettings.vue"
  import SettingsRefactor from "../components/settings/SettingsRefactor.vue"
  import CouponSettings from "@/components/settings/CouponSettings.vue"
  import LogisticsZonesSettings from "@/components/settings/LogisticsZonesSettings.vue"
  import CouponApi from "@/api/coupon"
  import { useCoupons } from "@/store/modules/coupons"
  const $ability = inject("$ability")

  // End of import

  import CreateUser from "@/components/users/CreateUser.vue"
  import { useUsers } from "../store/modules/users"
  const usersStore = useUsers()
  const couponStore = useCoupons()
  const couponApi = new CouponApi()

  const state = reactive({
    active: 0,
    componentList: [
      "Coupons",
      "Order Column Fields",
      "Integrations",
      "InvoicePage",
      "Rates",
      "Emails",
      "Other Settings",
      "Logistics zones"
      // "Settings Refactor"
    ], // Components List
    cms: null
  })

  onMounted(async () => {
    // load coupons
    const res = await couponApi.getAllCoupons()
    couponStore.setCoupons(res.data.value)
    state.cms = usersStore.cms
  })
</script>
